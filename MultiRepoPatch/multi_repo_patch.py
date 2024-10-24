import os
import subprocess
import argparse
import json

PWD = os.getcwd()
CWD = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')


TITLE_TARGET = "TARGET: "
TITLE_PATCH = ""


def separator(ch: str = '='):
    print(ch * 128)


def load_repositories_from_json(json_file_path):
    try:
        with open(json_file_path, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        print(f"JSON file {json_file_path} not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON file {json_file_path}.")
    except Exception as e:
        print(f"Unexpected error while loading JSON: {e}")
    return {}


def run_git_command(command, error_message):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode()
    except subprocess.CalledProcessError as e:
        print(f"{error_message}: {e.stderr.decode() if e.stderr else 'No error message available'}")
        return None


def run_git_command_nopipe(command, error_message):
    try:
        subprocess.run(command, check=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"{error_message}: {e.stderr.decode() if e.stderr else 'No error message available'}")


def check_patch(patch_path):
    return run_git_command(['git', 'apply', patch_path, '--check'], "Failed to check patch applicability") is not None


def apply_patch(patch_path):
    return run_git_command(['git', 'am', patch_path], "Failed to apply patch") is not None


def show_patch(index):
    return run_git_command_nopipe(['git', 'show', f'HEAD~{index}'], "Failed to display patch") is not None


def display_git_logs(num_patches, oneline=False):
    log_command = ['git', 'log', '-n', str(num_patches)]
    if oneline:
        log_command.append('--oneline')
    return run_git_command_nopipe(log_command, "Failed to display git logs") is not None


def reset_patch(len_patches):
    return run_git_command(['git', 'reset', '--hard', f'HEAD~{str(len_patches)}'], "Failed to display git logs") is not None


def apply_patch_list(target_path, patch_file_list, target_root, patch_root, args):
    separator("=")
    target_full_path = os.path.join(target_root, target_path)
    print(f'{TITLE_TARGET}{target_full_path}')

    original_dir = os.getcwd()
    try:
        os.chdir(target_full_path)

        if args.reset:
            reset_patch(len(patch_file_list))

        for i, patch_path in enumerate(patch_file_list):
            patch_full_path = os.path.join(patch_root, patch_path)
            if args.check or args.apply or args.show:
                separator("-")
                print(f'{TITLE_PATCH}{patch_full_path}')
            if args.check:
                if not check_patch(patch_full_path):
                    break
            if args.apply:
                if not apply_patch(patch_full_path):
                    break
            if args.show:
                if not show_patch(i):
                    break

        if args.log:
            separator("-")
            display_git_logs(len(patch_file_list) + 1, args.oneline)
    finally:
        os.chdir(original_dir)


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
    parser.add_argument('--reset', action='store_true', help='Reset the repository to the state before applying patches.')
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

    for patch in patch_list:
        apply_patch_list(patch['target'], patch['patch'], target_root, patch_root, args)


if __name__ == '__main__':
    main()
