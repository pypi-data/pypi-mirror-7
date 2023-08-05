# # # # # # # # # # # # # #
# CAPTAINHOOK IDENTIFIER  #
# # # # # # # # # # # # # #
try:
    import ConfigParser as configparser
except ImportError:
    # python 3
    import configparser

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
        return self.__bool__()

    def __bool__(self):
        return bool(str(self))


def python_files_for_commit():
    "Get all python files that are staged for commit, that are not deleted."
    files_pattern = '\.py(\..+)?$'
    return bash((
        "git diff --cached --name-status | "
        "grep -E '{files_pattern}' | "
        "grep -v -E '^D' | "
        "awk '{{ print ( $(NF) ) }}' "
    ).format(files_pattern=files_pattern))


class HookConfig(object):

    def __init__(self, config_filename):
        self.config_filename = config_filename
        self._config = None

    def get_file(self):
        return open(self.config_filename)

    @property
    def config(self):
        if not self._config:
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
