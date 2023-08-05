import socket
import os
import uuid
from collections import defaultdict
import time
import urlparse
import threading
import hashlib
import traceback

marionette = None

here = os.path.join(os.path.split(__file__)[0])

from .base import TestExecutor, testharness_result_converter, reftest_result_converter
from ..testrunner import Stop

def do_delayed_imports():
    global marionette
    import marionette

class MarionetteTestExecutor(TestExecutor):
    def __init__(self, browser, http_server_url, timeout_multiplier=1):
        do_delayed_imports()
        TestExecutor.__init__(self, browser, http_server_url, timeout_multiplier)
        self.marionette_port = browser.marionette_port
        self.marionette = None

        self.timer = None
        self.window_id = str(uuid.uuid4())

    def setup(self, runner):
        """Connect to browser via marionette"""
        self.runner = runner

        self.logger.debug("Connecting to marionette on port %i" % self.marionette_port)
        self.marionette = marionette.Marionette(host='localhost', port=self.marionette_port)
        #XXX Move this timeout somewhere
        self.logger.debug("Waiting for marionette connection")
        success = self.marionette.wait_for_port(60)
        session_started = False
        if success:
            for i in xrange(5):
                try:
                    self.logger.debug("Starting marionette session attempt %i" % i)
                    self.marionette.start_session()
                except:
                    self.logger.warning("Starting marionette session failed")
                    time.sleep(1)
                    break
                else:
                    self.logger.debug("Marionette session started")
                    session_started = True
                    break

        if not success or not session_started:
            self.logger.warning("Failed to connect to marionette")
            self.runner.send_message("init_failed")
        else:
            try:
                self.after_connect()
            except Exception:
                self.logger.warning("Post-connection steps failed")
                self.logger.error(traceback.format_exc())
                self.runner.send_message("init_failed")
            else:
                self.runner.send_message("init_succeeded")

    def teardown(self):
        try:
            self.marionette.delete_session()
        except:
            pass
        del self.marionette

    def is_alive(self):
        try:
            #Get a simple property over the connection
            self.marionette.current_window_handle
        except (socket.timeout, marionette.errors.InvalidResponseException):
            return False
        return True

    def after_connect(self):
        self.logger.debug(urlparse.urljoin(self.http_server_url, "/testharness_runner.html"))
        try:
            self.marionette.navigate(urlparse.urljoin(self.http_server_url, "/testharness_runner.html"))
        except:
            self.logger.critical("Loading initial page %s failed. Ensure that the there are no other programs bound to this port and that your firewall rules or network setup does not prevent access.")
            raise
        self.marionette.execute_script("document.title = '%s'" % threading.current_thread().name)

    def run_test(self, test):
        """Run a single test.

        This method is independent of the test type, and calls
        do_test to implement the type-sepcific testing functionality.
        """
        #Lock to prevent races between timeouts and other results
        #This might not be strictly necessary if we need to deal
        #with the result changing post-hoc anyway (e.g. due to detecting
        #a crash after we get the data back from marionette)
        result = None
        result_flag = threading.Event()
        result_lock = threading.Lock()

        timeout = test.timeout * self.timeout_multiplier

        def timeout_func():
            with result_lock:
                if not result_flag.is_set():
                    result_flag.set()
                    result = (test.result_cls("EXTERNAL-TIMEOUT", None), [])
                    self.runner.send_message("test_ended", test, result)

        self.timer = threading.Timer(timeout + 10, timeout_func)
        self.timer.start()

        try:
            self.marionette.set_script_timeout((timeout + 5) * 1000)
        except marionette.errors.InvalidResponseException:
            self.logger.error("Lost marionette connection")
            self.runner.send_message("restart_test", test)
            return Stop

        try:
            result = self.convert_result(test, self.do_test(test, timeout))
        except marionette.errors.ScriptTimeoutException:
            with result_lock:
                if not result_flag.is_set():
                    result_flag.set()
                    result = (test.result_cls("EXTERNAL-TIMEOUT", None), [])
            # Clean up any unclosed windows
            # This doesn't account for the possibility the browser window
            # is totally hung. That seems less likely since we are still
            # getting data from marionette, but it might be just as well
            # to do a full restart in this case
            # XXX - this doesn't work at the moment because window_handles
            # only returns OS-level windows (see bug 907197)
            # while True:
            #     handles = self.marionette.window_handles
            #     self.marionette.switch_to_window(handles[-1])
            #     if len(handles) > 1:
            #         self.marionette.close()
            #     else:
            #         break
            # Now need to check if the browser is still responsive and restart it if not
        except (socket.timeout, marionette.errors.InvalidResponseException, IOError):
            # This can happen on a crash
            # Also, should check after the test if the firefox process is still running
            # and otherwise ignore any other result and set it to crash
            with result_lock:
                if not result_flag.is_set():
                    result_flag.set()
                    result = (test.result_cls("CRASH", None), [])
        finally:
            self.timer.cancel()

        with result_lock:
            if result:
                self.runner.send_message("test_ended", test, result)


class MarionetteTestharnessExecutor(MarionetteTestExecutor):
    convert_result = testharness_result_converter

    def __init__(self, *args, **kwargs):
        MarionetteTestExecutor.__init__(self, *args, **kwargs)
        self.script = open(os.path.join(here, "testharness_marionette.js")).read()

    def do_test(self, test, timeout):
        assert len(self.marionette.window_handles) == 1
        return self.marionette.execute_async_script(
            self.script % {"abs_url": urlparse.urljoin(self.http_server_url, test.url),
                           "url": test.url,
                           "window_id": self.window_id,
                           "timeout_multiplier": self.timeout_multiplier,
                           "timeout": timeout * 1000}, new_sandbox=False)


class MarionetteReftestExecutor(MarionetteTestExecutor):
    convert_result = reftest_result_converter

    def __init__(self, *args, **kwargs):
        MarionetteTestExecutor.__init__(self, *args, **kwargs)
        with open(os.path.join(here, "reftest.js")) as f:
            self.script = f.read()
        with open(os.path.join(here, "reftest-wait.js")) as f:
            self.wait_script = f.read()
        self.ref_hashes = {}
        self.ref_urls_by_hash = defaultdict(set)

    def do_test(self, test, timeout):
        test_url, ref_type, ref_url = test.url, test.ref_type, test.ref_url
        hashes = {"test": None,
                  "ref": self.ref_hashes.get(ref_url)}
        self.marionette.execute_script(self.script)
        self.marionette.switch_to_window(self.marionette.window_handles[-1])
        for url_type, url in [("test", test_url), ("ref", ref_url)]:
            if hashes[url_type] is None:
                #Would like to do this in a new tab each time, but that isn't
                #easy with the current state of marionette
                full_url = urlparse.urljoin(self.http_server_url, url)
                try:
                    self.marionette.navigate(full_url)
                except marionette.errors.MarionetteException:
                    return {"status":"ERROR",
                            "message":"Failed to load url %s" % (full_url,)}
                if url_type == "test":
                    self.wait()
                screenshot = self.marionette.screenshot()
                #strip off the data:img/png, part of the url
                if screenshot.startswith("data:image/png;base64,"):
                    screenshot = screenshot.split(",", 1)[1]
                hashes[url_type] = hashlib.sha1(screenshot).hexdigest()

        self.ref_urls_by_hash[hashes["ref"]].add(ref_url)
        self.ref_hashes[ref_url] = hashes["ref"]

        if ref_type == "==":
            passed = hashes["test"] == hashes["ref"]
        elif ref_type == "!=":
            passed = hashes["test"] != hashes["ref"]
        else:
            raise ValueError

        return {"status":"PASS" if passed else "FAIL",
                "message": None}

    def wait(self):
        self.marionette.execute_async_script(self.wait_script)

    def teardown(self):
        count = 0
        for hash_val, urls in self.ref_urls_by_hash.iteritems():
            if len(urls) > 1:
                self.logger.info("The following %i reference urls appear to be equivalent:\n %s" %
                                 (len(urls), "\n  ".join(urls)))
                count += len(urls) - 1
        MarionetteTestExecutor.teardown(self)
