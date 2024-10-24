# Git Patch Application Script

This Python script is designed to apply patches to multiple Git repositories based on configurations specified in a JSON file. It provides options to check the applicability of patches, apply them, and display Git logs. It also supports showing patches before application.

## A Note to Developers

This script is dedicated to all developers working on projects managed by multiple Git repositories, such as those using `repo`.

For those who, due to network constraints, are forced to exchange patches instead of benefiting from Git's distributed version control, we offer this tool as a way to keep your workflow efficient and manageable. Even in challenging environments, we hope this script helps you maintain momentum in your development efforts.

## Features

- Apply patches to multiple Git repositories using `git am`.
- Check if patches can be applied cleanly without applying them (`git apply --check`).
- View a list of patches without applying them.
- Display Git logs after applying patches, with an option to display in a one-line format.

## Requirements

- Python 3.x
- Git

## Installation

1. Clone the repository or download the script.
2. Make sure Git is installed and available in your system's PATH.

## Usage

```bash
python multi_repo_patch.py <json_file> [options]
```

### Arguments

- `json_file`: Path to the JSON file containing patch configurations (see format below).

### Options

- `--target`, `-t`: Root path of the target repositories. If not provided, the script uses the path from the JSON file.
- `--patch`, `-p`: Root path of the patches. If not provided, the script uses the path from the JSON file.
- `--apply`, `-a`: Apply patches using `git am`.
- `--check`, `-c`: Check if the patches can be applied cleanly (without applying them).
- `--show`, `-s`: Show the list of patches without applying them.
- `--log`, `-l`: Display Git logs after applying the patches.
- `--oneline`, `-o`: Show Git logs in one-line format (requires `--log`).

### Example

To check the applicability of patches:

```bash
python multi_repo_patch.py patches.json --check
```

To apply patches and view the Git log after applying:

```bash
python multi_repo_patch.py patches.json --apply --log
```

### JSON Configuration File

The JSON file should define the target repositories and the list of patches to apply for each repository. Example format:

```json
{
  "target_root": "/path/to/repositories",
  "patch_root": "/path/to/patches",
  "patch_list": [
    {
      "target": "repo1",
      "patch": ["patch1.patch", "patch2.patch"]
    },
    {
      "target": "repo2",
      "patch": ["patch3.patch"]
    }
  ]
}
```

### Handling Errors

- If the script encounters errors during patch application or log display, error messages will be shown with details from Git.

## License

This project is licensed under the MIT License.
