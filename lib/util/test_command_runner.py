import unittest

from ..util.command_runner import CommandRunner

class Obj:
    def func0(self):
        pass

    def func1(self, a):
        pass

    def func2(self, a ,b):
        pass

class TestModule(unittest.TestCase):

    def testcall(self):
        CommandRunner(Obj(), [ "func0" ]).run()
        CommandRunner(Obj(), [ { "cmd": "func1", "args": [1] } ]).run()
        CommandRunner(Obj(), [ { "cmd": "func2", "args": [1, 2] } ]).run()

