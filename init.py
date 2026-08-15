from pathlib import Path

class Repository():
    def __init__(self,path="."):
        self.path=Path(path).resolve()
        self.git_dir=self.path/".pygit"

        # objects dir
        self.object_dir=self.git_dir/".objects"

        # ref dir
        self.ref_dir=self.git_dir/".refs"
        self.head_dir=self.ref_dir/".heads"

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
        self.head_dir.mkdir()
        self.head_file.write_text("ref: refs/heads/master\n")
        self.save_index({})
        print(f"Initialized a new git repository in {self.git_dir}")

        return True
        
        