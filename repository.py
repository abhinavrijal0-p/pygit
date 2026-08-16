from pathlib import Path
import json
from gitobjects import Blob,GitObject
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
        if full_path.is_file():
            self.add_file(path)
        elif full_path.is_dir():
            self.add_dir(path)
        else:
            raise ValueError(f"{path} is neither a file nor a directory")

    # add file

    def add_file(self,path:str):
        #reads file content and stores the byte in blob objects
        #store objects in database (.pygit/objects)
        full_path=self.path/path
        if not full_path.exists():
            print(f"Path:{path} not found")
        content=full_path.read_bytes()
        blob=Blob(content)
        blob_hash=self.store_object(blob)
        #update the index file
        index=self.load_index()
        index[path]=blob_hash
        self.save_index(index)
        print("Added file path")

        
        
        