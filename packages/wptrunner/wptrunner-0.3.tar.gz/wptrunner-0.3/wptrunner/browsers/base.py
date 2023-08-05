import os
import socket
import sys
import time
import tempfile
import shutil
import subprocess

import mozprocess
from mozprofile import FirefoxProfile, Preferences
from mozprofile.permissions import ServerLocations
from mozrunner import FirefoxRunner, B2GRunner
import mozdevice
import moznetwork

here = os.path.split(__file__)[0]

def get_free_port(start_port, exclude=None):
    """Get the first port number after start_port (inclusive) that is
    not currently bound.

    :param start_port: Integer port number at which to start testing.
    :param exclude: Set of port numbers to skip"""
    port = start_port
    while True:
        if exclude and port in exclude:
            port += 1
            continue
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", port))
        except socket.error:
            port += 1
        else:
            return port
        finally:
            s.close()


class BrowserError(Exception):
    pass


class Browser(object):
    process_cls = None
    init_timeout = 30

    def __init__(self, logger):
        """Abstract class serving as the basis for Browser implementations.

        The Browser is used in the TestRunnerManager to start and stop the browser
        process, and to check the state of that process. This class also acts as a
        context manager, enabling it to do browser-specific setup at the start of
        the testrun and cleanup after the run is complete.

        :param logger: Structured logger to use for output.
        """
        self.logger = logger

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, *args, **kwargs):
        self.cleanup()

    def setup(self):
        """Used for browser-specific setup that happens at the start of a test run"""
        pass

    def start(self):
        """Launch the browser object and get it into a state where is is ready to run tests"""
        raise NotImplementedError

    def stop():
        """Stop the running browser process."""
        raise NotImplementedError

    def on_output(self, line):
        """Callback function used with ProcessHandler to handle output from the browser process."""
        raise NotImplementedError

    def is_alive(self):
        """Boolean indicating whether the browser process is still running"""
        raise NotImplementedError

    def cleanup(self):
        """Browser-specific cleanup that is run after the testrun is finished"""
        pass

    def executor_browser(self):
        """Returns the ExecutorBrowser subclass for this Browser subclass and the keyword arguments
        with which it should be instantiated"""
        return ExecutorBrowser, {}

class NullBrowser(Browser):
    def start(self):
        """No-op browser to use in scenarios where the TestRunnerManager shouldn't
        actually own the browser process (e.g. Servo where we start one browser
        per test)"""
        pass

    def stop(self):
        pass

    def is_alive(self):
        return True

class ExecutorBrowser(object):
    def __init__(self, **kwargs):
        """View of the Browser used by the Executor object.
        This is needed because the Executor runs in a child process and
        we can't ship Browser instances between processes on Windows.

        Typically this will have a few product-specific properties set,
        but in some cases it may have more elaborate methods for setting
        up the browser from the runner process.
        """
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
