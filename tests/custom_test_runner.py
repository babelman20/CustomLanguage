import time
import unittest

class CustomTestResult(unittest.TextTestResult):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.successes = 0
        self.start_time = time.time()

    def addSuccess(self, test):
        self.successes += 1

    def stopTestRun(self):
        self.stop_time = time.time()
        super().stopTestRun()

class CustomTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)