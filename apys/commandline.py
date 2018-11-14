import argparse
import sys
import os
import importlib
import importlib.util

from apys import settings


def main():
    # Adding current dir to sys path
    sys.path.insert(0, './')

    parser = argparse.ArgumentParser(description='apys - a restful api framework.')
    parser.add_argument('-s', '--start', '--serve', 
                        action='store_true', default=False, 
                        help='starts server')
    parser.add_argument('-c', '--config',
                        action='store', default=False, 
                        help='select config file')
    parser.add_argument('-i', '--init',
                        action='store_true', default=False, 
                        help='initialize project folder')
    parser.add_argument('-b', '--build', 
                        action='store_true', default=False, 
                        help='build project [not yet implemented]')
    parser.add_argument('-v', '--version',
                        action='store_true', default=False, 
                        help='show lib version')

    ##
    # Adding CLI utils
    #
    utils = []
    if os.path.exists(os.path.join('.', settings.DIR_UTILS)):
        for subdir in os.listdir(os.path.join('.', settings.DIR_UTILS)):
            if(
                    (os.path.isdir(os.path.join('.', settings.DIR_UTILS, subdir))) and
                    (os.path.exists(os.path.join('.', settings.DIR_UTILS, subdir, '__cli__.py')))
            ):

                util = subdir
                spec = importlib.util.spec_from_file_location(
                    util,
                    os.path.join('.', settings.DIR_UTILS, util, '__cli__.py'))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Get util CLI object
                cli = module.CLI(None)
                parser.add_argument('-{}'.format(util[0]), '--{}'.format(util),
                                    action=cli.action, default=cli.default,
                                    help=cli.help)

                # Adding util to list
                utils += [util]

    ##
    # Get arguments and execute scripts
    #
    args = parser.parse_args()

    if args.start:
        from apys import server
        server.start(args.config)
    elif args.init:
        from apys import project
        project.init()
    elif args.version:
        import apys
        print(apys.__version__)
    else:

        # start util script
        for util in utils:
            if getattr(args, util, False):

                # Cli argument
                arg = getattr(args, util, False)

                # Starting server
                from apys import server
                server.cli_start(util, args.config, arg)

                return

        # nothing found, show help
        parser.print_help()
