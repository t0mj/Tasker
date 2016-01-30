import click
import datetime
import os
import yaml

from collections import OrderedDict
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from subprocess import call


DIR = os.path.expanduser('~/.tasker')
DATA_FILE = os.path.join(DIR, 'task_data.yml')
TODAY = datetime.date.today()
BOX = lambda checked: u"\u2705" if checked else u"\u25FB\uFE0F"
CYAN = lambda txt: click.echo(click.style(txt, fg='cyan', bold=True))
GREEN = lambda txt: click.echo(click.style(txt, fg='green', bold=True))
RED = lambda txt: click.echo(click.style(txt, fg='red', bold=True))
YELLOW = lambda txt: click.echo(click.style(txt, fg='yellow', bold=True))


class Tasker(object):
    def __init__(self):
        self.task_data = {}
        if not os.path.exists(DIR):
            os.makedirs(DIR)
        if not os.path.exists(DATA_FILE):
            self.write_data()

    def load_data(self):
        stream = file(DATA_FILE, 'r')
        self.task_data = self.sort_dict(yaml.load(stream))

    def daily_tasks(self, task_date=TODAY):
        # Returns a list with the task for a given day
        if type(task_date) != datetime.date:
            task_date = parse(task_date).date()
        one_days_data = self.task_data.get(task_date)
        if not one_days_data:
            RED('No tasks found on {}'.format(task_date))
        return one_days_data

    def query_data(self, query_type):
        start_date = TODAY - relativedelta(days=7)
        query_data = {}
        for task_date, data in self.task_data.iteritems():
            if query_type == 'weekly':
                if task_date <= TODAY and task_date >= start_date:
                    query_data[task_date] = data
            elif query_type == 'monthly':
                if task_date.month == TODAY.month:
                    query_data[task_date] = data
        return self.sort_dict(query_data)

    def sort_dict(self, adict):
        return OrderedDict(sorted(adict.iteritems()))

    def write_data(self):
        with open(DATA_FILE, 'w') as tdf:
            yaml.dump(self.task_data, tdf)

pass_tasker = click.make_pass_decorator(Tasker)


@click.group()
@click.version_option('1.1')
@click.pass_context
def cli(ctx):
    """
    Tasker is a CLI to track and manage your daily tasks.
    """
    ctx.obj = Tasker()


@cli.command()
@click.argument('task_title', nargs=-1, required=True)
@click.option('--link', '-l', default=None,
              help='Attach a link to your task.  Open with: task browse')
@pass_tasker
def add(tasker, task_title, link):
    """
    Add a new task to todays list.\n
    ex: task add Respond to meanface Sue's email
    """
    tasker.load_data()
    tasker.task_data.setdefault(TODAY, [])
    task_dict = {'title': ' '.join(task_title), 'complete': False}
    if link:
        task_dict['link'] = link
    tasker.task_data[TODAY].append(task_dict)
    tasker.sort_dict(tasker.task_data)
    tasker.write_data()
    GREEN('Task added.')


@cli.command()
@click.argument('task_idx', type=int, required=True)
@click.option('--task_date', '-d', default=TODAY,
              help='Pass a date to remove, defaults to today.')
@pass_tasker
def browse(tasker, task_idx, task_date):
    """
    Open browser for a task with a link. (cyan)\n
    Examples:\n
    task browse 0 -d 2016-01-28\n
    task browse 3
    """
    tasker.load_data()
    daily_tasks = tasker.daily_tasks(task_date)
    if daily_tasks:
        if task_idx >= len(daily_tasks):
            RED('No task {} found on {}'.format(task_idx, task_date))
            return
        task = daily_tasks[task_idx]
        if task.get('link'):
            call(["open", task['link']])


@cli.command()
@click.argument('task_idx', type=int, required=True)
@click.option('--task_date', '-d', default=TODAY,
              help='Pass a date to remove, defaults to today.')
@pass_tasker
def done(tasker, task_idx, task_date):
    """
    Toggles complete status for a passed index.\n
    Examples:\n
    task done 2\n
    task done 0 -d 2016-01-30
    """
    tasker.load_data()
    daily_tasks = tasker.daily_tasks(task_date)
    if daily_tasks:
        if task_idx >= len(daily_tasks):
            RED('No task {} found on {}'.format(task_idx, task_date))
            return
        curr_status = daily_tasks[task_idx]['complete']
        daily_tasks[task_idx]['complete'] = not curr_status
        tasker.write_data()
        GREEN('Task marked complete.')


@cli.command()
@click.option('--all_tasks', '-a', is_flag=True,
              help='List all tasks by date.')
@click.option('--week', '-w', is_flag=True,
              help='List all tasks for the last week.')
@click.option('--month', '-m', is_flag=True,
              help='List all tasks for the current month.')
@pass_tasker
def ls(tasker, all_tasks, week, month):
    """
    List todays tasks.
    CYAN tasks have links and can be opened from cli.
    Ex: task open 3
    """
    tasker.load_data()
    if all_tasks:
        task_data = tasker.task_data
    elif week:
        task_data = tasker.query_data('weekly')
    elif month:
        task_data = tasker.query_data('monthly')
    else:
        task_data = {TODAY: tasker.task_data.get(TODAY)}
        if not task_data[TODAY]:
            GREEN('No tasks today.')
            return
    for task_date, data in task_data.iteritems():
        if not data:
            continue
        click.echo()
        YELLOW('Tasks for {}:'.format(task_date))
        for idx, task in enumerate(tasker.task_data[task_date]):
            output_str = ('{}  {}. {}'
                          .format(BOX(task['complete']).encode('utf-8'),
                                  idx, task['title']))
            if task.get('link'):
                CYAN(output_str)
            else:
                click.echo(output_str)


@cli.command()
@click.argument('task_idx', type=int, required=True)
@click.option('--task_date', '-d', default=TODAY,
              help='Pass a date to remove, defaults to today.')
@pass_tasker
def rm(tasker, task_idx, task_date):
    """
    Remove a task for the passed index.\n
    Examples:\n
    task rm 0 -d 2016-01-28\n
    task rm 3
    """
    tasker.load_data()
    daily_tasks = tasker.daily_tasks(task_date)
    if daily_tasks:
        if task_idx >= len(daily_tasks):
            RED('No task {} found on {}'.format(task_idx, task_date))
            return
        daily_tasks.pop(task_idx)
        tasker.sort_dict(tasker.task_data)
        tasker.write_data()
        GREEN('Task removed.')
