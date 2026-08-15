import argparse
import sys
from init import Repository

def main():
    parser=argparse.ArgumentParser(prog="pygit",description="This is a git hub like tool in python")
    subparser=parser.add_subparsers(dest="command",required=True)

    init_parser=subparser.add_parser("init",help="Initializes the repository")

    args=parser.parse_args()

    if not args.command:
        parser.print_help()
        return 

    try:
        if args.command=="init":
            repo=Repository()
            if not repo.init():
                print("Repository already exists")
                return 
    except Exception as e:
        print(f"Error:{e}")
        sys.exit(1)

    add_parser=subparser.add_parser("add",help="Adds a file to the repository")
    add_parser.add_arguments("path",nargs="+",help="Files and directories to add")

    