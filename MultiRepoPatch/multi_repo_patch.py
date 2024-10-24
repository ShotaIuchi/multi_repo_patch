import os
import subprocess
import argparse
import json

PWD = os.getcwd()
CWD = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')


def separator(ch: str = '='):
    print(ch * 128)


def apply_patch(patch_path, args):
    try:
        # First, check if the patch can be applied
        if args.check:
            subprocess.run(['git', 'apply', patch_path, '--check'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Apply the patch if requested
        if args.apply:
            subprocess.run(['git', 'am', patch_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f'Success')
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr.decode()}")
    except Exception as e:
        print(f"Error: {e}")


def load_repositories_from_json(json_file_path):
    try:
        with open(json_file_path, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        print(f"JSON file {json_file_path} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON file {json_file_path}.")
        return {}
    except Exception as e:
        print(f"Unexpected error while loading JSON: {e}")
        return {}


def main():
    parser = argparse.ArgumentParser(description="Apply patches to multiple Git repositories.")
    parser.add_argument('file', type=str, help='Path to the JSON file containing patch configurations.')
    parser.add_argument('--target', type=str, help='Root path of the target repositories.')
    parser.add_argument('--patch', type=str, help='Root path of the patches.')
    parser.add_argument('--apply', '-a', action='store_true', help='Apply patches using `git am`.')
    parser.add_argument('--check', '-c', action='store_true', help='Check if the patches can be applied cleanly.')
    parser.add_argument('--show', '-s', action='store_true', help='Show the list of patches without applying them.')
    parser.add_argument('--log', '-l', action='store_true', help='Display Git logs after applying the patches.')
    parser.add_argument('--oneline', '-o', action='store_true', help='Show Git logs in one-line format (requires --log).')
    # parser.add_argument('--reset', action='store_true', help='Reset the repository to the state before applying patches.')
    args = parser.parse_args()

    if args.oneline and not args.log:
        parser.error('--oneline requires --log to be specified.')

    patch_config = load_repositories_from_json(os.path.join(PWD, args.file))

    if not patch_config:
        print("Invalid or empty patch configuration. Exiting.")
        return

    target_root = args.target if args.target else os.path.join(PWD, patch_config.get('target_root', ''))
    patch_root = args.patch if args.patch else os.path.join(PWD, patch_config.get('patch_root', ''))
    patch_list = patch_config.get('patch_list', [])

    def apply_patch_list(target_path, patch_file_list):
        separator("=")
        target_full_path = os.path.join(target_root, target_path)
        print(f'Target path: {target_full_path}')

        original_dir = os.getcwd()
        try:
            os.chdir(target_full_path)

            # if args.reset:
            #    subprocess.run(['git', 'reset', '--hard', f'HEAD~{str(len(patch_file_list))}'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            for i, patch_path in enumerate(patch_file_list):
                patch_full_path = os.path.join(patch_root, patch_path)
                if args.check or args.apply or args.show:
                    separator("-")
                    print(f'Patch path  : {patch_full_path}')
                if args.check or args.apply:
                    apply_patch(patch_full_path, args)
                if args.show:
                    try:
                        subprocess.run(['git', 'show', f'HEAD~{i}'], check=True, stderr=subprocess.PIPE)
                    except subprocess.CalledProcessError as e:
                        print(f"Error displaying show: {e.stderr.decode() if e.stderr else 'No error message available'}")

            if args.log:
                separator("-")
                try:
                    if not args.oneline:
                        subprocess.run(['git', 'log', '-n', str(len(patch_file_list) + 1)], check=True, stderr=subprocess.PIPE)
                    else:
                        subprocess.run(['git', 'log', '-n', str(len(patch_file_list) + 1), '--oneline'], check=True, stderr=subprocess.PIPE)
                except subprocess.CalledProcessError as e:
                    print(f"Error displaying logs: {e.stderr.decode() if e.stderr else 'No error message available'}")
        finally:
            os.chdir(original_dir)

    for patch in patch_list:
        apply_patch_list(patch['target'], patch['patch'])


if __name__ == '__main__':
    main()
