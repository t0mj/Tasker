"""
Tests for the list command: task ls

Author: Thomas Johns @t0mj
"""
import unittest
from tools import Commander


class TestList(unittest.TestCase):
    def setUp(self):
        self.commander = Commander()

    def tearDown(self):
        self.commander.teardown()
        self.commander = None

    def test_ls(self):
        task_list = self.commander.command('ls')
        assert len(task_list) == 3
