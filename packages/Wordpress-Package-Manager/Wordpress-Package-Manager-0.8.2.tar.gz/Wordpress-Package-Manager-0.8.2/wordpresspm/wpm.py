#! /usr/bin/env python
import argparse
import os
import sys
import re
import shutil
import installers


class WPM(object):
    wp_latest = "http://wordpress.org/latest.zip"

    def __init__(self):

        parser = argparse.ArgumentParser(prog="wpm",
                                         description='A comand line tool to handle WordPress framework and plugin installation')

        subparsers = parser.add_subparsers(title="Available commands")

        install_framework_parser = subparsers.add_parser('installframework',
                                                         help="Install the latest version of WordPress")

        install_framework_parser.add_argument('location',
                                              help="Specify the target location.",
                                              default=os.getcwd())

        install_framework_parser.add_argument('-o', '--overwrite',
                                              action='store_true',
                                              help="Overwrite the previous installation of WordPress",
                                              default=False)

        install_framework_parser.set_defaults(func=self.install_framework)

        install_plugin_parser = subparsers.add_parser('installplugin',
                                                      help="Install a WordPress plugin")

        install_plugin_parser.add_argument('plugin',
                                           help="The plugin name",
                                           nargs='?',
                                           default=None)

        install_plugin_parser.add_argument('-l', '--location',
                                           help="Specify the target location.",
                                           default=os.getcwd())

        install_plugin_parser.add_argument('-o', '--overwrite',
                                           action='store_true',
                                           help="Overwrite the previous installation of WordPress",
                                           default=False)

        install_plugin_parser.add_argument('-r', '--requirements',
                                           help="Use a requirements file",
                                           default=False)

        install_plugin_parser.set_defaults(func=self.install_plugin)

        self.args = parser.parse_args()
        self.args.func(self.args)

    """
    Downloads and installs the WordPress framework.
    """

    def install_framework(self, parser, *args, **kwargs):

        installer = installers.FrameworkInstaller(url=self.wp_latest,
                                       target_location=self.args.location, overwrite=self.args.overwrite)

        if installer.install() is False:
            return False

        try:
            shutil.move(os.path.join(installer.target_location, 'wp-config-sample.php'),
                        os.path.join(installer.target_location, 'wp-config.php'))
            installer.set_security_keys(
                os.path.join(installer.target_location, 'wp-config.php'))
        except:
            print "Error while trying to add security keys to wp-config.php"

        print "Installed WordPress"

    """
    Installs a plugin
    """

    def install_plugin(self, parser, *args, **kwargs):

        if self.args.plugin is None and self.args.requirements is False:
            return

        if self.args.requirements:

            file = open(os.path.abspath(self.args.requirements), 'r')
            requirements = file.readlines()
            file.close()

            for line in requirements:
                self._route_install(line)
        else:
            self._route_install(self.args.plugin)

    """
    Search for available plugins to install
    """

    def search(self):

        local = open(os.path.expanduser('~/.wpm/available_plugins'), 'r+')
        search_str = sys.argv[2]

        for line in local.readlines():
            if re.search(search_str, line):
                print line.replace("\r\n", '')

    """
    List all installed plugins
    """

    def list(self):
        try:
            pass
        except:
            NotImplementedError

    """
    Update the local list of plugins
    """

    def update(self):

        print "Getting plugins list"
        installer = installers.DBInstaller(
            arguments=self.args, options=self.options)
        installer.install()
        print "\nPlugins updated."

    """
    Create the setup directory that contains the package repositories
    """

    def setup(self):

        print "Installing WPM"
        installer = installers.DBInstaller(
            arguments=self.args, options=self.options)
        installer.install()
        print "\nInstallation complete"

    """
    Decides which protocol to use to install the plugin
    """

    def _route_install(self, line):

        if line == '' or line[:1] == '#':
            return

        parsed = re.compile(
            '(?P<protocol>git|svn|zip)\+(?P<url>[^#]+)(?:#(?:name|egg)=(?P<name>.+))?').search(line.strip())

        params = {
            'arguments': self.args,
            'url': parsed.group('url') if parsed is not None else '',
            'plugin_name': parsed.group('name') if parsed is not None else '',
            'target_location': self.args.location,
            'overwrite': self.args.overwrite,
        }

        if parsed is None:
            params['plugin_name'] = line.strip()
            Installer = self._get_installer()
        else:
            Installer = self._get_installer(protocol=parsed.group('protocol'))

        instance = Installer(**params)
        instance.install()

        print "Installed " + params['plugin_name']

    def _get_installer(self, protocol='WP'):
        return getattr(installers, "%sInstaller" % protocol.upper())


if __name__ == '__main__':
    WPM()
