#!/usr/bin/env python3

"""
Author: Tim McGlothin <tmcglothin@llbean.com>
Date: 2023-05-10

This script processes the /etc/sudoers file on a Unix/Linux system. It creates individual files in 
/etc/sudoers.d directory for each user or group that has sudo privileges, following the sudoers file 
format.

The script accepts several command-line arguments to specify the sudoers file, prefix for the sudoers.d 
files, directory for the sudoers.d files, and options to run in test mode and remove entries from sudoers 
file after moving them.

The script creates backups of the sudoers file and the sudoers.d directory if the --backup option is 
specified. It also performs a syntax check on each newly created file using `visudo -cf`. If visudo 
reports an error, the script deletes the file.

Usage:
    python3 sudoers_parser.py [options]

For more details on usage and options, see the README.md file or run:
    python3 sudoers_parser.py --help

Disclaimer:
This script makes changes to your system's sudo configuration. Incorrect sudo configuration can lock you 
out of your system or give unauthorized users sudo privileges. Always review the changes made by the 
script and use the --test mode to see what changes would be made before running the script. Always keep 
backups of your sudoers file and sudoers.d directory. The author of this script is not responsible for 
any damage caused by the use or misuse of this script.
"""

import os
import shutil
import re
import subprocess
import argparse
import tempfile
import datetime

# Regular expression to match user or group rules in sudoers file
rule_regex = re.compile(
    r"^(\%?[a-z_][a-z0-9_\-]*)\s+ALL=\(ALL\)(\:ALL)?(\s+NOPASSWD\: ALL)?(\s+.*)?$")

# ANSI color codes


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def backup_sudoers_file(sudoers_file):
    backup_file = f"{sudoers_file}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
    shutil.copy2(sudoers_file, backup_file)
    print(f"{Colors.OKGREEN}Backup of sudoers file created at {backup_file}{Colors.ENDC}")


def entry_exists_in_sudoers_d(entry, sudoers_d_dir):
    normalized_entry = ' '.join(entry.lower().split())
    for file_name in os.listdir(sudoers_d_dir):
        file_path = os.path.join(sudoers_d_dir, file_name)
        with open(file_path, 'r') as file:
            file_content = file.read()
            # Remove comments and normalize whitespace
            normalized_file_content = ' '.join(
                re.sub(r'#.*', '', file_content).lower().split())
            if normalized_entry in normalized_file_content:
                return file_name
    return None


def remove_entry_from_sudoers(sudoers_file, entry):
    temp = tempfile.NamedTemporaryFile(delete=False)
    with open(sudoers_file, "r") as sudoers, open(temp.name, "w") as temp_file:
        for line in sudoers:
            if line.strip() != entry:
                temp_file.write(line)

    # Replace sudoers file with the temporary file
    shutil.move(temp.name, sudoers_file)


def create_sudoers_d_files(sudoers_file, file_prefix, sudoers_d_dir, test_mode, remove_entries):
    try:
        with open(sudoers_file, "r") as sudoers:
            for line in sudoers:
                match = rule_regex.match(line.strip())
                if match:
                    user_or_group = match.group(1)
                    entry = line.strip()

                    print(
                        f"\n{Colors.HEADER}Processing line: {line.strip()}{Colors.ENDC}")

                    # Exclude root and wheel accounts (case-insensitive)
                    if user_or_group.lower() not in ['root', '%wheel']:
                        existing_file = entry_exists_in_sudoers_d(
                            entry, sudoers_d_dir)
                        if not existing_file:
                            # Create file name, removing '%' if it's a group
                            file_name = sudoers_d_dir + "/" + file_prefix + \
                                "_" + user_or_group.replace('%', '')

                            print(f"{Colors.OKGREEN}Would create file: {file_name}{Colors.ENDC}") if test_mode else print(
                                f"{Colors.OKGREEN}Creating file: {file_name}{Colors.ENDC}")
                            # Write rule to new file
                            if not test_mode:
                                with open(file_name, 'w') as new_file:
                                    new_file.write(entry)

                                # Check the file with visudo
                                print(
                                    f"{Colors.OKBLUE}Checking file with visudo.{Colors.ENDC}")
                                result = subprocess.run(
                                    ['visudo', '-cf', file_name])

                                # If visudo found an error, delete the file
                                if result.returncode != 0:
                                    print(
                                        f"{Colors.FAIL}Error in {file_name}, deleting file.{Colors.ENDC}")
                                    os.remove(file_name)
                                elif remove_entries:
                                    print(
                                        f"{Colors.WARNING}Removing line from {sudoers_file}{Colors.ENDC}")
                                    remove_entry_from_sudoers(
                                        sudoers_file, entry)
                        else:
                            print(
                                f"{Colors.WARNING}Entry {user_or_group} already exists in {existing_file}, skipping.{Colors.ENDC}")
                    else:
                        print(
                            f"{Colors.WARNING}Skipping {user_or_group} account.{Colors.ENDC}")

    except IOError as e:
        print(f"{Colors.FAIL}Error opening sudoers file: {e}{Colors.ENDC}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process sudoers file.')
    parser.add_argument('-s', '--sudoers-file',
                        help='Path to the sudoers file', default='/etc/sudoers')
    parser.add_argument('-p', '--file-prefix',
                        help='Prefix for the sudoers.d files', default='10')
    parser.add_argument('-d', '--sudoers-d-dir',
                        help='Directory for the sudoers.d files', default='/etc/sudoers.d')
    parser.add_argument('-t', '--test', action='store_true',
                        help='Run in test mode (no changes are made)')
    parser.add_argument('-r', '--remove', action='store_true',
                        help='Remove entries from sudoers file after moving them')
    parser.add_argument('-b', '--backup', action='store_true',
                        help='Create a backup of the sudoers file before making changes')

    args = parser.parse_args()

    if args.backup:
        backup_sudoers_file(args.sudoers_file)

    create_sudoers_d_files(args.sudoers_file, args.file_prefix,
                           args.sudoers_d_dir, args.test, args.remove)
