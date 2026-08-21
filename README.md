# PyGit

A lightweight, from-scratch implementation of Git in Python — built to understand and reproduce the core internals of version control rather than to replace Git itself.

PyGit reimplements Git's content-addressable object model, staging index, and repository metadata, exposing a familiar Git-style CLI for the most fundamental workflow: `init → add → status → commit → log`.

## Why

Git's plumbing (blobs, trees, commits, SHA-1 hashing, zlib compression) is usually a black box. This project peels that back by re-implementing it directly — every object PyGit creates is a real, valid Git object, hashed and compressed the same way Git does it internally.

## Features

- **`init`** — Initialize a new repository, setting up the `.git`-style directory structure (object store, refs, HEAD).
- **`add`** — Stage files by hashing their contents into blob objects and recording them in a persistent staging index.
- **`status`** — Traverse the working directory, compare against the index and HEAD, and report changed/staged/untracked files.
- **`commit`** — Build hierarchical tree objects from the staged index, wrap them in a commit object with metadata, and update HEAD/refs.
- **`log`** — Walk the commit history from HEAD, following parent pointers, and print commit metadata.

## How it works

### Object model

Git's object model is content-addressable: every piece of data is identified by the SHA-1 hash of its own contents. PyGit implements the three core object types:

| Object | Purpose |
|---|---|
| **Blob** | Raw contents of a single file |
| **Tree** | A snapshot of a directory — maps filenames to blob/tree hashes |
| **Commit** | A tree hash + parent commit + metadata (author, message, timestamp) |

Each object is serialized with a Git-style header (`<type> <size>\0<content>`), hashed with **SHA-1** to produce its object ID, compressed with **zlib**, and written into the object store keyed by that hash — identical to how Git stores objects on disk.

### Repository state

Alongside the object store, PyGit maintains:
- A **staging index** that tracks what's been `add`ed and is waiting to be committed
- **HEAD** and **refs**, pointing at the current branch/commit
- Serialization/deserialization logic to read and write this state as persistent JSON/metadata between runs

### Tree construction

`commit` walks the staged files, groups them by directory, and recursively builds tree objects bottom-up — nested directories become nested tree objects, mirroring exactly how Git encodes a filesystem hierarchy into its object graph.

## Project structure

```
pygit/
├── main.py         # CLI entry point — argparse-based command parsing and routing
├── repository.py   # Core Git logic: init, add, commit, status, log, index/HEAD/refs management
├── gitobjects.py    # Git object model: Blob, Tree, and Commit classes (hashing, serialization, zlib compression)
└── .gitignore
```

- **`main.py`** — Defines the CLI using `argparse`, parsing Git-style subcommands and dispatching them to the appropriate repository method.
- **`repository.py`** — Implements repository-level operations (`init`, `add`, `commit`, `status`, `log`), including filesystem traversal, index management, and reading/writing HEAD and refs.
- **`gitobjects.py`** — Defines the object model (blob, tree, commit), including hashing with SHA-1, header construction, and zlib compression/decompression for storage.

## Usage

```bash
# Initialize a new repository
python main.py init

# Stage files
python main.py add <file>...

# Check working directory / staging status
python main.py status

# Commit staged changes
python main.py commit -m "commit message"

# View commit history
python main.py log
```

## Tech stack

- **Python** — implementation language
- **argparse** — CLI parsing and command routing
- **hashlib (SHA-1)** — content-addressable object hashing
- **zlib** — object compression, matching Git's on-disk format
- **JSON** — serialization of repository metadata (index, refs)

## Roadmap

Possible next steps beyond the current command set:
- `diff` — show changes between working tree, index, and commits
- `branch` / `checkout` — branch creation and switching
- `merge` — basic merge support
- Packfiles / object compaction

## Disclaimer

PyGit is an educational project for learning Git internals — it is not intended to be a drop-in replacement for Git and is not optimized, hardened, or tested for production use.
