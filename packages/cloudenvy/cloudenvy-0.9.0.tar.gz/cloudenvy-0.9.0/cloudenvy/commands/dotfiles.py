import logging
import tarfile
import tempfile
import os

import fabric.api
import fabric.operations

import cloudenvy.core


class Dotfiles(cloudenvy.core.Command):

    def _build_subparser(self, subparsers):
        help_str = 'Upload dotfiles from your local machine to an Envy.'
        subparser = subparsers.add_parser('dotfiles', help=help_str,
                                          description=help_str)
        subparser.set_defaults(func=self.run)
        subparser.add_argument('-n', '--name', action='store', default='',
                               help='Specify custom name for an Envy.')
        subparser.add_argument('-f', '--files', action='store',
                               help='Limit operation to a specific list of '
                                    'comma-separated files.')
        return subparser

    def run(self, config, args):
        envy = cloudenvy.core.Envy(config)

        if envy.ip():
            host_string = '%s@%s' % (envy.config.remote_user, envy.ip())

            temp_tar = tempfile.NamedTemporaryFile(delete=True)

            with fabric.api.settings(host_string=host_string):
                if args.files:
                    dotfiles = args.files.split(',')
                else:
                    dotfiles = config['defaults']['dotfiles'].split(',')

                dotfiles = [dotfile.strip() for dotfile in dotfiles]

                with tarfile.open(temp_tar.name, 'w') as archive:
                    for dotfile in dotfiles:
                        path = os.path.expanduser('~/%s' % dotfile)
                        if os.path.exists(path):
                            if not os.path.islink(path):
                                archive.add(path, arcname=dotfile)

                fabric.operations.put(temp_tar, '~/dotfiles.tar')
                fabric.operations.run('tar -xvf ~/dotfiles.tar')
        else:
            logging.error('Could not determine IP.')
