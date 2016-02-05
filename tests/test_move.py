"""
Tests for the move command: task mv

Author: Thomas Johns @t0mj
"""
import unittest
from tools import Commander


class TestMove(unittest.TestCase):
    def setUp(self):
        self.commander = Commander()

    def tearDown(self):
        self.commander.teardown()
        self.commander = None

    def test_mv_down(self):
        cmd = self.commander.command
        original_list = cmd('ls')
        message = cmd('mv 0 down')[0]
        assert message == 'Task 0 has been moved to task 1'
        new_list = cmd('ls')
        assert original_list != new_list
        assert original_list[1].replace('1', '0') == new_list[0]

    def test_mv_up(self):
        cmd = self.commander.command
        original_list = cmd('ls')
        message = cmd('mv 1 up')[0]
        assert message == 'Task 1 has been moved to task 0'
        new_list = cmd('ls')
        assert original_list != new_list
        assert original_list[0].replace('0', '1') == new_list[1]

    def test_mv_errors(self):
        cmd = self.commander.command
        message = cmd('mv 0 up')[0]
        assert message == 'Invalid move operation.'

        message = cmd('mv 2 down')[0]
        assert message == 'Invalid move operation.'

        message = cmd('mv -1')[0]
        assert message == 'Error: no such option: -1'

        message = cmd('mv 4')[0]
        assert message == ('You must give a direction or an order of your '
                           'tasks.')

        message = cmd('mv 4 up')[0]
        assert message == 'Task index out of range.'

        message = cmd('mv 4 down')[0]
        assert message == 'Task index out of range.'
