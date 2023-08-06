import logging
import os
import time

import fabric.api
import fabric.operations

import cloudenvy.core


class Provision(cloudenvy.core.Command):

    def _build_subparser(self, subparsers):
        help_str = 'Upload and execute script(s) in your Envy.'
        subparser = subparsers.add_parser('provision', help=help_str,
                                          description=help_str)
        subparser.set_defaults(func=self.run)

        subparser.add_argument('-n', '--name', action='store', default='',
                               help='Specify custom name for an Envy.')
        subparser.add_argument('-s', '--scripts', nargs='*', metavar='PATH',
                               help='Specify one or more scripts.')
        return subparser

    def run(self, config, args):
        envy = cloudenvy.core.Envy(config)

        logging.info('Running provision scripts for Envy \'%s\'.' %
                     envy.name)
        if not envy.ip():
            logging.error('Could not determine IP.')
            return

        with fabric.api.settings(
                host_string=envy.ip(), user=envy.config.remote_user,
                forward_agent=True, disable_known_hosts=True):

            if args.scripts:
                scripts = [os.path.expanduser(script) for
                           script in args.scripts]
            elif 'provision_scripts' in envy.config.project_config:
                scripts = [os.path.expanduser(script) for script in
                           envy.config.project_config['provision_scripts']]
            elif 'provision_script_path' in envy.config.project_config:
                provision_script = envy.config.project_config['provision_script_path']
                scripts = [os.path.expanduser(provision_script)]
            else:
                raise SystemExit('Please specify the path to your provision '
                                 'script(s) by either using the `--scripts` '
                                 'flag, or by defining the `provision_scripts`'
                                 ' config option in your Envyfile.')

            for script in scripts:
                logging.info('Running provision script from \'%s\'', script)

                for i in range(24):
                    try:
                        path = script
                        filename = os.path.basename(script)
                        remote_path = '~/%s' % filename
                        fabric.operations.put(path, remote_path, mode=0755)
                        fabric.operations.run(remote_path)
                        break
                    except fabric.exceptions.NetworkError:
                        logging.debug(
                            'Unable to upload the provision script '
                            'from `%s`. Trying again in 10 seconds.' % path
                        )
                        time.sleep(10)
                logging.info('Provision script \'%s\' finished.' % path)
