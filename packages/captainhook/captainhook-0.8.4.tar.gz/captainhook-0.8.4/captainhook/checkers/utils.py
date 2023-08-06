# # # # # # # # # # # # # #
# CAPTAINHOOK IDENTIFIER  #
# # # # # # # # # # # # # #
try:
    import ConfigParser as configparser
except ImportError:
    # python 3
    import configparser

import os.path
from subprocess import PIPE, Popen


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

    def __unicode__(self):
        return self.value()

    def __str__(self):
        return self.value()

    def __nonzero__(self):
        return self.__bool__()

    def __bool__(self):
        return bool(self.value())

    def value(self):
        return self.output.strip().decode(encoding='UTF-8')


class bash_no_errors(bash):

    def bash(self, cmd):
        super(bash_no_errors, self).bash(cmd)
        if self.err:
            raise Exception(self.err)
        return self


def get_files(commit_only=True, copy_dest=None):
    "Get copies of files for analysis."
    if commit_only:
        real_files = bash(
            "git diff --cached --name-status | "
            "grep -v -E '^D' | "
            "awk '{ print ( $(NF) ) }' "
        ).value().strip()

        if real_files:
            return create_fake_copies(real_files.split('\n'), copy_dest)
        return []
    else:
        return bash(
            "git ls-tree --name-only --full-tree -r HEAD"
        ).value().split('\n')


def create_fake_copies(files, destination):
    """
    Create copies of the given list of files in the destination given.

    Creates copies of the actual files to be committed using
    git show :<filename>

    Return a list of destination files.
    """
    dest_files = []
    for filename in files:
        leaf_dest_folder = os.path.join(destination, os.path.dirname(filename))
        if not os.path.exists(leaf_dest_folder):
            os.makedirs(leaf_dest_folder)
        dest_file = os.path.join(destination, filename)
        bash("git show :{filename} > {dest_file}".format(
            filename=filename,
            dest_file=dest_file)
        )
        dest_files.append(dest_file)
    return dest_files


def filter_python_files(files=None):
    "Get all python files from the list of files."
    py_files = []
    for f in files:
        # If we end in .py, or if we don't have an extension and file says that
        # we are a python script, then add us to the list
        extension = os.path.splitext(f)[-1]
        if extension:
            if extension == '.py':
                py_files.append(f)
        elif 'python' in open(f, 'r').readline():
            py_files.append(f)
        elif 'python script' in bash('file {}'.format(f)).value().lower():
            py_files.append(f)

    return py_files


class HookConfig(object):

    def __init__(self, config_filename):
        self.config_filename = config_filename
        self._config = {}

    def get_file(self):
        return open(self.config_filename)

    @property
    def config(self):
        if not self._config and os.path.exists(self.config_filename):
            c = configparser.ConfigParser()
            c.readfp(self.get_file())
            self._config = dict(c.items('captainhook'))
        return self._config

    def is_enabled(self, plugin, default='off'):
        setting = self.configuration(plugin)[0]
        return setting == 'on' or (setting == 'default' and default == 'on')

    def arguments(self, plugin):
        return self.configuration(plugin)[1].strip()

    def configuration(self, plugin):
        """
        Get plugin configuration.

        Return a tuple of (on|off|default, args)
        """
        conf = self.config.get(plugin, "default;").split(';')
        if len(conf) == 1:
            conf.append('')
        return tuple(conf)
