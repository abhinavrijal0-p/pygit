import argparse
import sys
from repository import Repository


def main():
    parser=argparse.ArgumentParser(prog="pygit",description="This is a git hub like tool in python")
    subparser=parser.add_subparsers(dest="command",required=True)

    init_parser=subparser.add_parser("init",help="Initializes the repository")
    add_parser=subparser.add_parser("add",help="Adds a files or directory to the staging area")
    add_parser.add_argument("paths",nargs='+',help="Files and directories to add")

    args=parser.parse_args()
    

    if not args.command:
        parser.print_help()
        return 
    try:
        repo=Repository()
        if args.command=="init":
            if not repo.init():
                print("Repository already exists")
                return 
        elif args.command=="add":
            if not repo.git_dir.exists():
                print("Not a git repository")
                return 
            for path in args.paths:
                repo.add_path(path)


        
    except Exception as e:
        print(f"Error:{e}")
        sys.exit(1)

    

if __name__ == "__main__":
    main()   