# # # # # # # # # # # # # #
# CAPTAINHOOK IDENTIFIER  #
# # # # # # # # # # # # # #
from .utils import bash

DEFAULT = 'off'
NO_ARG_MESSAGE = 'You must specify an argument to the grep checker.'


def grep(args, files):
    return bash('grep -n -H --exclude=tox.ini {} {}'.format(args, files))


def run(files, temp_folder, arg=None):
    if arg is None:
        return NO_ARG_MESSAGE
    files = ' '.join(files)
    return grep(arg, files).value()
