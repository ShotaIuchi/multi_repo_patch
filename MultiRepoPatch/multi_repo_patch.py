import os
import subprocess
import argparse
import json


PWD = os.getcwd()
CWD = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')


class JsonKeys:
    TARGET_ROOT = 'target_root'
    PATCH_ROOT = 'patch_root'
    PATCH_LIST = 'patch_list'
    TARGET = 'target'
    PATCH = 'patch'


class LogMsg:
    TITLE_TARGET = 'TARGET: '
    TITLE_PATCH = 'PATCH: '
    OK = 'OK'
    NG = 'NG'
    OK_RESULT = 'RESULT: OK'
    NG_RESULT = 'RESULT: NG'


def ok(message):
    print(f"\033[32m{message}\033[0m")


def ng(message):
    print(f"\033[31m{message}\033[0m")


def separator(ch: str = '=', num: int = 128, color: str = '0'):
    print(f"\033[{color}m{ch * num}\033[0m")


def load_repositories_from_json(json_file_path):
    try:
        with open(json_file_path, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        print(f'JSON file {json_file_path} not found.')
    except json.JSONDecodeError:
        print(f'Error decoding JSON file {json_file_path}.')
    except Exception as e:
        print(f'Unexpected error while loading JSON: {e}')
    return {}


def run_git_command(command: list[str]) -> str:
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode()
    except subprocess.CalledProcessError as e:
        ng(e.stderr.decode())
    except Exception as e:
        ng(e)
    return None


def run_git_command_nopipe(command: list[str]) -> str:
    try:
        result = subprocess.run(command, check=True, stderr=subprocess.PIPE)
        return result
    except subprocess.CalledProcessError as e:
        ng(e.stderr.decode())
    except Exception as e:
        ng(e)
    return None


def check_patch(patch_path) -> bool:
    return run_git_command(['git', 'apply', patch_path, '--check']) is not None


def apply_patch(patch_path) -> bool:
    return run_git_command(['git', 'am', patch_path]) is not None


def show_patch(index) -> bool:
    return run_git_command_nopipe(['git', 'show', f'HEAD~{index}']) is not None


def log_patch(num_patches, oneline=False) -> bool:
    log_command = ['git', 'log', '-n', str(num_patches)]
    if oneline:
        log_command.append('--oneline')
    return run_git_command_nopipe(log_command) is not None


def forall(command) -> bool:
    return run_git_command_nopipe(command.split()) is not None


def exec_patch_list(target_root, patch_root, target_path, patch_file_list, args) -> bool:
    target_full_path = os.path.join(target_root, target_path)
    print(f'{LogMsg.TITLE_TARGET}{target_full_path}')

    original_dir = os.getcwd()
    try:
        os.chdir(target_full_path)

        if args.command == 'forall':
            return forall(args.forall_cmd)

        if args.command == 'log':
            return log_patch(len(patch_file_list) + 1, args.oneline)

        if args.command == 'apply':
            isAllOk = True
            for i, patch_path in enumerate(patch_file_list):
                separator('-', color='91')
                patch_full_path = os.path.join(patch_root, patch_path)
                print(f'{LogMsg.TITLE_PATCH}{patch_full_path}')
                if args.check:
                    result = check_patch(patch_full_path)
                else:
                    result = apply_patch(patch_full_path)
                if result:
                    ok(LogMsg.OK)
                else:
                    ng(LogMsg.NG)
                isAllOk &= result
            return isAllOk

        if args.command == 'show':
            isAllOk = True
            for i, patch_path in enumerate(patch_file_list):
                separator('-', color='91')
                patch_full_path = os.path.join(patch_root, patch_path)
                print(f'{LogMsg.TITLE_PATCH}{patch_full_path}')
                isAllOk &= show_patch(i)
            return isAllOk

    finally:
        os.chdir(original_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description='Apply patches to multiple Git repositories.')
    parser.add_argument('file', type=str, help='Path to the JSON file containing patch configurations.')

    parser.add_argument('--target', type=str, help='Root path of the target repositories.')
    parser.add_argument('--patch', type=str, help='Root path of the patches.')

    subparsers = parser.add_subparsers(dest='command', required=True)

    parser_forall = subparsers.add_parser('forall', help='Run a command for all repositories.')
    parser_forall.add_argument('forall_cmd', type=str, help='Command to run for all repositories.')

    parser_apply = subparsers.add_parser('apply', help='Apply patches using `git am`.')
    parser_apply.add_argument('--check', '-c', action='store_true', help='Show Git logs in one-line format (requires --log).')

    parser_show = subparsers.add_parser('show', help='Show the list of patches without applying them.')

    parser_log = subparsers.add_parser('log', help='Display Git logs after applying the patches.')
    parser_log.add_argument('--oneline', '-o', action='store_true', help='Show Git logs in one-line format (requires --log).')

    args = parser.parse_args()

    patch_config = load_repositories_from_json(os.path.join(PWD, args.file))

    if not patch_config:
        print('Invalid or empty patch configuration. Exiting.')
        return

    target_root = args.target if args.target else os.path.join(PWD, patch_config.get(JsonKeys.TARGET_ROOT, ''))
    patch_root = args.patch if args.patch else os.path.join(PWD, patch_config.get(JsonKeys.PATCH_ROOT, ''))
    patch_list = patch_config.get(JsonKeys.PATCH_LIST, [])

    isAllOk = True
    for patch in patch_list:
        separator('=', color='96')
        target_path = patch.get(JsonKeys.TARGET, '')
        patch_file_list = patch.get(JsonKeys.PATCH, [])
        isAllOk &= exec_patch_list(target_root, patch_root, target_path, patch_file_list, args)

    separator('=', color='96')
    if isAllOk:
        ok(LogMsg.OK_RESULT)
    else:
        ng(LogMsg.NG_RESULT)


if __name__ == '__main__':
    main()
