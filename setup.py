from setuptools import setup


setup(
    name='Tasker',
    version='1.4',
    py_modules=['tasks'],
    install_requires=[
        'Click',
        'pyyaml',
        'python-dateutil',
    ],
    entry_points='''
        [console_scripts]
        task=tasks:cli
    '''
)
