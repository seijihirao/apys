import argparse

def main():

    parser = argparse.ArgumentParser(description='apys - a restful api framework.')
    parser.add_argument('-s', '--start', '--serve', 
                        action='store_true', default=False, 
                        help='starts server')
    parser.add_argument('-c', '--config',
                        action='store', default=False, 
                        help='select config file')
    parser.add_argument('-i','--init',
                        action='store_true', default=False, 
                        help='initialize project folder')
    parser.add_argument('-b', '--build', 
                        action='store_true', default=False, 
                        help='build project [not yet implemented]')
    parser.add_argument('-t', '--test',
                        action='store_true', default=False, 
                        help='run automated tests [not yet implemented]')
    parser.add_argument('-v', '--version',
                        action='store_true', default=False, 
                        help='show lib version')
    
    args = parser.parse_args()

    if args.start:
        from apys import server
        server.start(args.config)
    elif args.init:
        from apys import project
        project.init()
    elif args.version:
        import apys
        print(apys.version())
    else:
        parser.print_help()