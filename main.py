import argparse
import sys
from repository import Repository


def main():
    parser=argparse.ArgumentParser(prog="pygit",description="This is a git hub like tool in python")
    subparser=parser.add_subparsers(dest="command",required=True)

    init_parser=subparser.add_parser("init",help="Initializes the repository")
    add_parser=subparser.add_parser("add",help="Adds a files or directory to the staging area")
    add_parser.add_argument("paths",nargs='+',help="Files and directories to add")

    commit_parser = subparser.add_parser("commit", help="Create a new commit")
    commit_parser.add_argument(
        "-m",
        "--message",
        help="Commit message",
        required=True,
    )
    commit_parser.add_argument(
        "--author",
        help="Author name and email",
    )
    
    status_parser = subparser.add_parser("status", help="Show the working tree status")
    log_parser = subparser.add_parser("log", help="Show commit logs")

    branch_parser = subparser.add_parser("branch", help="List, create, or delete branches")
    branch_parser.add_argument("name", nargs="?", help="Branch name")
    branch_parser.add_argument("-d", action="store_true", help="Delete branch")

    checkout_parser = subparser.add_parser("checkout", help="Checkout a branch")
    checkout_parser.add_argument("branch", help="Branch name")
    checkout_parser.add_argument("-b", action="store_true", help="Create branch")

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
        elif args.command == "commit":
            if not repo.git_dir.exists():
                print("Not a git repository")
                return

            author = args.author or "PyGit user <user@pygit.com>"
            repo.commit(args.message, author)
        elif args.command == "status":
            if not repo.git_dir.exists():
                print("Not a git repository")
                return
            repo.status()
        elif args.command == "log":
            if not repo.git_dir.exists():
                print("Not a git repository")
                return
            repo.log()
        elif args.command == "branch":
            if not repo.git_dir.exists():
                print("Not a git repository")
                return
            repo.branch(args.name, args.d)
        elif args.command == "checkout":
            if not repo.git_dir.exists():
                print("Not a git repository")
                return
            repo.checkout(args.branch, args.b)


    except Exception as e:
        print(f"Error:{e}")
        sys.exit(1)

    

if __name__ == "__main__":
    main()   