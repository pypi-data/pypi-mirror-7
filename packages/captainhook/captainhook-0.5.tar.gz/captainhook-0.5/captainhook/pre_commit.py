#!/usr/bin/env python
# # # # # # # # # # # # # #
# CAPTAINHOOK IDENTIFIER  #
# # # # # # # # # # # # # #
"""
A pre commit hook for git.

This will look at the [githooks] section of tox.ini file to see which checks
you would like to run.

To add a new check:

    1. Create a function that returns a true like, printable object for
       failure, or ``None`` for success.
    2. Add that function to ``CHECKS``.
    3. Add a corresponding line (the name of the function) to your tox.ini file
       with 'on' (run this check) or 'off' (don't). The default behaviour is to
       run all checks defined in ``CHECKS``.
"""
try:
    import ConfigParser as configparser
except ImportError:
    # python 3
    import configparser

from contextlib import contextmanager
import os.path
import sys
from subprocess import Popen, PIPE


class bash(object):
    "This is lower class because it is intended to be used as a method."

    def __init__(self, cmd):
        """
        TODO: Release this as a separate library!
        """
        self.p = None
        self.output = None
        self.bash(cmd)

    def bash(self, cmd):
        self.p = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
        self.output, self.err = self.p.communicate(input=self.output)
        return self

    def __str__(self):
        return self.output.strip().decode(encoding='UTF-8')

    def __nonzero__(self):
        return bool(str(self))


def title_print(msg):
    "Pretty print a title bar."
    bar = '=' * 79
    print(bar)
    print(msg)
    print(bar)


def python_files_for_commit():
    "Get all python files that are staged for commit, that are not deleted."
    files_pattern = '\.py(\..+)?$'
    return bash((
        "git diff --cached --name-status | "
        "grep -E '{files_pattern}' | "
        "grep -v -E '^D' | "
        "awk '{{ print ( $(NF) ) }}' "
    ).format(files_pattern=files_pattern))


def python3():
    "Check to see if python files are py3 compatible"
    py_files = str(python_files_for_commit())
    errors = []
    for py_file in py_files.splitlines():
        b = bash('python3 -m py_compile {0}'.format(py_file))
        if b.err:
            errors.append(b.err)
    return "\n".join(errors)


def pdb():
    "Look for pdb.set_trace() commands in python files."
    forbidden = '^[^#"]*pdb.set_trace()'
    py_files = python_files_for_commit()
    if not py_files:
        return
    files = py_files.bash((
        "xargs grep --color --with-filename -n "
        "-e '{forbidden}'"
    ).format(
        forbidden=forbidden
    ))
    return files


def flake8():
    "Check flake8 errors in the code base."
    py_files = str(python_files_for_commit())
    if not py_files:
        return
    b = bash("flake8 {0}".format(py_files.replace('\n', ' ')))
    if b.err:
        if "command not found" in b.err:
            return (
                "flake8 is required for the flake8 plugin.\n"
                "`pip install flake8` or turn it off in your tox.ini file.")
    return b


def changes_to_stash():
    "Check there are changes to stash"
    return bool(bash('git diff'))


@contextmanager
def gitstash(stash=True):
    """
    Validate the commit diff.

    Stash the unstaged changes first and unstash afterwards regardless of
    failure.
    """
    if stash and not changes_to_stash():
        stash = False

    if stash:
        bash("git stash -q --keep-index")
    try:
        yield
    finally:
        if stash:
            bash("git stash pop -q")


def get_hook_checks():
    """
    Return the hook check options set in tox.ini.

    Return an empty dict if none are set.
    """
    config = configparser.ConfigParser()
    if os.path.exists('tox.ini'):
        config.readfp(open('tox.ini'))
        if config.has_section('captainhook'):
            return {
                key: value for key, value in config.items('captainhook')
            }
    return {}


def get_check_function(check_name):
    """
    Get the check function being used in tox.ini

    This can be anything on the PYTHONPATH.
    """
    try:
        return globals()[check_name]
    except KeyError:
        print("TODO: Implement importing of extensions.")

CHECKS = (pdb, flake8, python3)


def main(stash):
    """
    Run the configured code checks.

    Return system exit code.
        1 - reject commit
        0 - accept commit
    """
    exit_code = 0
    hook_checks = get_hook_checks()
    with gitstash(stash):
        for func in CHECKS:
            name = func.__name__
            if hook_checks.get(name, 'on') == 'on':
                errors = func()
                if errors:
                    title_print("Checking {0}".format(name))
                    print(errors)
                    exit_code = 1

    if exit_code == 1:
        title_print("Rejecting commit")
    sys.exit(exit_code)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nostash', action='store_true')
    args = parser.parse_args()
    main(stash=not args.nostash)
