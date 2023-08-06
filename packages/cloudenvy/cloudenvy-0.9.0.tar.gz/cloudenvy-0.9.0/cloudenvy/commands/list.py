import cloudenvy.core


class List(cloudenvy.core.Command):

    def _build_subparser(self, subparsers):
        help_str = 'List all Envys in your current project.'
        subparser = subparsers.add_parser('list', help=help_str,
                                          description=help_str)
        subparser.set_defaults(func=self.run)
        return subparser

    def run(self, config, args):
        envy = cloudenvy.core.Envy(config)

        for server in envy.list_servers():
            if server.name.startswith(envy.name):
                print server.name[len(envy.name)+1:] or '(default)'
