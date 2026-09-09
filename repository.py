from pathlib import Path
import json
from gitobjects import Blob,GitObject,Commit,Tree
from typing import Dict, List, Optional, Tuple

class Repository():

    #initialize repo
    def __init__(self,path="."):
        self.path=Path(path).resolve()
        self.git_dir=self.path/".pygit"

        # objects dir
        self.object_dir=self.git_dir/".objects"

        # ref dir
        self.ref_dir=self.git_dir/".refs"
        self.heads_dir=self.ref_dir/".heads"

        #index dir
        self.index_file=self.git_dir/".index"

        #head file
        self.head_file=self.git_dir/".HEAD"

    
    def init(self)->bool:
        if self.git_dir.exists():
            return False
        self.git_dir.mkdir()
        self.object_dir.mkdir()
        self.ref_dir.mkdir()
        self.heads_dir.mkdir()
        self.head_file.write_text("ref: refs/heads/master\n")
        self.save_index({})
        print(f"Initialized a new git repository in {self.git_dir}")

        return True

    def save_index(self, index):
            self.index_file.write_text(json.dumps(index, indent=2))

    def load_index(self)->Dict[str,str]:
        if not self.index_file.exists():
            return {}
        try:
            return json.loads(self.index_file.read_text())
        except:
            return {}

    #add 
   
    def store_object(self,obj:GitObject)->str:
        obj_hash=obj.hash()
        obj_dir=self.object_dir/obj_hash[:2]
        obj_file=obj_dir/obj_hash[2:]
        if not obj_file.exists():
            obj_dir.mkdir(exist_ok=True)
            obj_file.write_bytes(obj.serialize())
        return obj_hash


    def add_path(self,path:str)->None :
        full_path=self.path/path
        if not full_path.exists():
            print(f"Path:{path} not found")
            return
        if full_path.is_file():
            self.add_file(path)
        elif full_path.is_dir():
            self.add_directory(path)
        else:
            raise ValueError(f"{path} is neither a file nor a directory")

    # add file

    def add_directory(self, path: str):
        full_path = self.path / path
        if not full_path.exists():
            raise FileNotFoundError(f"Directory {path} not found")
        if not full_path.is_dir():
            raise ValueError(f"{path} is not a directory")
        index = self.load_index()
        added_count = 0
        # recursively traverse the directory
        for file_path in full_path.rglob("*"):
            if file_path.is_file():
                if ".git" in file_path.parts:
                    continue

                # create & store blob object
                content = file_path.read_bytes()
                blob = Blob(content)
                blob_hash = self.store_object(blob)
                # update index
                rel_path = str(file_path.relative_to(self.path))
                index[rel_path] = blob_hash
                added_count += 1

        self.save_index(index)

        if added_count > 0:
            print(f"Added {added_count} files from directory {path}")
        else:
            print(f"Directory {path} already up to date")



    def add_file(self,path:str):
        #reads file content and stores the byte in blob objects
        #store objects in database (.pygit/objects)
        full_path=self.path/path
        if not full_path.exists():
            print(f"Path:{path} not found")
            return
        content=full_path.read_bytes()
        blob=Blob(content)
        blob_hash=self.store_object(blob)
        #update the index file
        index=self.load_index()
        index[path]=blob_hash
        self.save_index(index)
        print("Added file path")


    def load_object(self, obj_hash: str) -> GitObject:
        obj_dir = self.object_dir / obj_hash[:2]
        obj_file = obj_dir / obj_hash[2:]

        if not obj_file.exists():
            raise FileNotFoundError(f"Object {obj_hash} not found")

        return GitObject.deserialize(obj_file.read_bytes())

    def create_tree_from_index(self):
        index = self.load_index()
        if not index:
            tree = Tree()
            return self.store_object(tree)

        dirs = {}
        files = {}

        for file_path, blob_hash in index.items():
            parts = file_path.split("/")

            if len(parts) == 1:
                # file in root
                files[parts[0]] = blob_hash
            else:
                dir_name = parts[0]
                if dir_name not in dirs:
                    dirs[dir_name] = {}

                current = dirs[dir_name]
                for part in parts[1:-1]:
                    if part not in current:
                        current[part] = {}

                    current = current[part]

                current[parts[-1]] = blob_hash

        def create_tree_recursive(entries_dict: Dict):
            tree = Tree()

            for name, blob_hash in entries_dict.items():
                if isinstance(blob_hash, str):
                    tree.add_entry("100644", name, blob_hash)

                if isinstance(blob_hash, dict):
                    subtree_hash = create_tree_recursive(blob_hash)
                    tree.add_entry("40000", name, subtree_hash)

            return self.store_object(tree)

        root_entries = {**files}
        for dir_name, dir_contents in dirs.items():
            root_entries[dir_name] = dir_contents

        return create_tree_recursive(root_entries)

    def get_current_branch(self) -> str:
        if not self.head_file.exists():
            return "master"

        head_content = self.head_file.read_text().strip()
        if head_content.startswith("ref: refs/heads/"):
            return head_content[16:]

        return "HEAD"  # detached HEAD

    def get_branch_commit(self, current_branch: str):
        branch_file = self.heads_dir / current_branch

        if branch_file.exists():
            return branch_file.read_text().strip()

        return None

    def set_branch_commit(self, current_branch: str, commit_hash: str):
        branch_file = self.heads_dir / current_branch
        branch_file.write_text(commit_hash + "\n")

    def commit(
        self,
        message: str,
        author: str = "PyGit User <user@pygit.com>",
    ):
        # create a tree object from the index (staging area)
        tree_hash = self.create_tree_from_index()

        current_branch = self.get_current_branch()
        parent_commit = self.get_branch_commit(current_branch)
        parent_hashes = [parent_commit] if parent_commit else []

        index = self.load_index()
        if not index:
            print("nothing to commit, working tree clean")
            return None

        if parent_commit:
            parent_git_commit_obj = self.load_object(parent_commit)
            parent_commit_data = Commit.from_content(parent_git_commit_obj.content)
            if tree_hash == parent_commit_data.tree_hash:
                print("nothing to commit, working tree clean")
                return None

        commit = Commit(
            tree_hash=tree_hash,
            parent_hashes=parent_hashes,
            author=author,
            committer=author,
            message=message,
        )
        commit_hash = self.store_object(commit)

        self.set_branch_commit(current_branch, commit_hash)
        self.save_index({})
        print(f"Created commit {commit_hash} on branch {current_branch}")
        return commit_hash

    def get_files_from_tree_recursive(
        self,
        tree_hash: str,
        prefix: str = "",
    ):
        files = set()
        try:
            tree_obj = self.load_object(tree_hash)
            tree = Tree.from_content(tree_obj.content)
            # list<tuple<str, str, str>>
            for mode, name, obj_hash in tree.entries:
                full_name = f"{prefix}{name}"
                if mode.startswith("100"):
                    files.add(full_name)
                elif mode.startswith("400"):
                    subtree_files = self.get_files_from_tree_recursive(
                        obj_hash, f"{full_name}/"
                    )
                    files.update(subtree_files)
        except Exception as e:
            print(f"Warning: Could not read tree {tree_hash}: {e}")

        return files

    def checkout(self, branch: str, create_branch: bool):
        # computed the files to clear from the previous branch
        previous_branch = self.get_current_branch()
        files_to_clear = set()
        previous_commit_hash = None
        try:
            previous_commit_hash = self.get_branch_commit(previous_branch)
            if previous_commit_hash:
                prev_commit_object = self.load_object(previous_commit_hash)
                prev_commit = Commit.from_content(prev_commit_object.content)
                if prev_commit.tree_hash:
                    files_to_clear = self.get_files_from_tree_recursive(
                        prev_commit.tree_hash
                    )
        except Exception:
            files_to_clear = set()

        # created/moved to a new branch
        branch_file = self.heads_dir / branch
        if not branch_file.exists():
            if create_branch:
                if previous_commit_hash:
                    self.set_branch_commit(branch, previous_commit_hash)
                    print(f"Created new branch {branch}")
                else:
                    print("No commits yet, cannot create a branch")
                    return
            else:
                print(f"Branch '{branch}' not found.")
                print(
                    f"Use 'python3 main.py checkout -b {branch}' to create and switch to a new branch."
                )
                return
        self.head_file.write_text(f"ref: refs/heads/{branch}\n")

        # restore working directory
        self.restore_working_directory(branch, files_to_clear)
        print(f"Switched to branch {branch}")

    def restore_tree(self, tree_hash: str, path: Path):
        tree_obj = self.load_object(tree_hash)
        tree = Tree.from_content(tree_obj.content)
        for mode, name, obj_hash in tree.entries:
            file_path = path / name
            if mode.startswith("100"):
                blob_obj = self.load_object(obj_hash)
                blob = Blob(blob_obj.content)
                file_path.write_bytes(blob.content)
            elif mode.startswith("400"):
                file_path.mkdir(exist_ok=True)
                self.restore_tree(obj_hash, file_path)

    def restore_working_directory(
        self,
        branch: str,
        files_to_clear: set,
    ):
        target_commit_hash = self.get_branch_commit(branch)
        if not target_commit_hash:
            return

        # remove files tracked by previous branch
        for rel_path in sorted(files_to_clear):
            file_path = self.path / rel_path
            try:
                if file_path.is_file():
                    file_path.unlink()

                elif file_path.is_dir():
                     if not any(file_path.iterdir()):
                         file_path.rmdir()
            except Exception:
                pass

        target_commit_obj = self.load_object(target_commit_hash)
        target_commit = Commit.from_content(target_commit_obj.content)

        if target_commit.tree_hash:
            self.restore_tree(target_commit.tree_hash, self.path)

        self.save_index({})