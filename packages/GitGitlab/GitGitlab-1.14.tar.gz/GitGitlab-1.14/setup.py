"""GitGitlab: git plugin for GitLab."""

from setuptools import setup

setup(
    name='GitGitlab',
    version='1.14',
    description='gitlab for git',
    packages=['gitgitlab'],
    install_requires=['gitpython==0.3.2.RC1', 'keyring==3.3', 'opster==4.1', 'python-gitlab==0.6',
                      'requests==2.2.1'],
    entry_points={'console_scripts': ['git-lab=gitgitlab.cli:git']}
)
