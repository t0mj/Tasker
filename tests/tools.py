"""
Tests tools to simulate task data.  Commander creates a new class that allows
commands to be run as if they were on the command line.

Author: Thomas Johns @t0mj
"""
import datetime
import mock
import re

from click.testing import CliRunner
from mock import MagicMock
from tasks import cli, Tasker


TEST_DATA = {datetime.date.today(): [
    {"complete": False, "title": "Kiss my task"},
    {"complete": True, "title": "Foo task"},
    {"complete": True, "title": "Tests suck :("}
]}


def load_data(self):
    self.task_data = TEST_DATA


class Commander(object):
    def __init__(self):
        self.runner = CliRunner()

    def clean_output(self, output):
        output = re.sub(r'[^\x00-\x7F]+', '', output)
        output = output.split('\n')
        clean_output = []
        for str_ in output:
            if str_ and 'Tasks for' not in str_:
                clean_output.append(str_)
        return clean_output

    @mock.patch.object(Tasker, 'load_data', load_data)
    @mock.patch.object(Tasker, 'write_data', MagicMock())
    def command(self, command):
        if not isinstance(command, list):
            command = command.split(' ')
        result = self.runner.invoke(cli, command)
        self.generic_asserts(result)
        return self.clean_output(result.output)

    def generic_asserts(self, result):
        try:
            assert not result.exception
            assert result.exit_code == 0
        except AssertionError:
            # Check if its a click help text
            assert result.exit_code == 2
            assert 'Error: no such option:' in result.output

    def teardown(self):
        self.runner = None
