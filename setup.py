# setup.py
from setuptools import setup, find_packages

setup(
    name='tasks',
    version='1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'tasks = tasks.tasks:main',  # This creates the "tasks" command
        ],
    },
)