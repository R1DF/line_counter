# Imports
from rich.console import Console
from rich import print as rprint
import questionary
import os
import readchar
import sys

# Constants
CONSOLE = Console()


# Functions
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_error(text: str | int | float):
    CONSOLE.print(text, style="red")


def print_green(text: str | int | float):
    CONSOLE.print(text, style="green")


def wait_for_enter():
    CONSOLE.print("Press any key to continue.", style="yellow")
    readchar.readchar()


def accumulate_counts(directories: list[str], extensions: list[str]) -> list[int]:
    counts = []  # Note: counts[i] is the total sum of lines of each read file in directories[i]
    for directory in directories:
        total = 0
        for file in os.listdir(os.path.join(os.getcwd(), directory)):
            file_path = os.path.join(os.getcwd(), directory, file)
            if file.split(".")[-1] in extensions:
                total += count_lines(file_path, tell=True)
        counts.append(total)
    return counts


def count_lines(file_path: str, *, tell: bool = False) -> int:
    if tell:
        print(f"{file_path}: ", end="")
    with open(file_path) as f:
        lines = len(f.readlines())
    if tell:
        print_green(lines)
    return lines


def reduce_path(full_path: str, starting_directory: str) -> str:
    items_split = full_path.split("\\")
    return "\\".join(items_split[items_split.index(starting_directory):])


def scan_for_extensions(paths: list[str]) -> list[str]:
    extensions = []
    for directory in paths:
        for file in os.listdir(directory):
            if "." in file:
                extension = file.split(".")[-1]
                if extension not in extensions:
                    extensions.append(extension)
    return extensions


def scan_for_directories(path: str) -> list[str]:
    results = []
    for item in os.listdir(path):
        if os.path.isdir(os.path.join(path, item)):
            results.append(os.path.join(path, item))
            for item_inner in scan_for_directories(os.path.join(path, item)):
                results.append(os.path.join(path, item_inner))
    return results


def main():
    run = True
    program_directory = os.getcwd()
    home_directory = os.path.expanduser("~")
    while run:
        # Setup for each loop
        directories_excluded = []
        extensions_included = []
        clear()

        # Menu, asking for directory of project to scan
        print("Welcome to Line Counter.\nProject made by R1DF on GitHub.\n")
        os.chdir(home_directory)
        try:
            directory = questionary.path(
                "Select the directory of your project (press Tab for navigation):",
                only_directories=True
            ).unsafe_ask()

        except KeyboardInterrupt:
            print_error("Interrupted.")
            try:
                if not input("Press Enter without input to leave: "):
                    clear()
                    sys.exit()
                continue
            except KeyboardInterrupt:
                clear()
                sys.exit()

        os.chdir(program_directory)
        full_directory = os.path.join(home_directory, directory)
        if (not os.path.exists(full_directory)) or directory == "":
            print("This \"directory\" does not exist.")
            wait_for_enter()
            continue

        print("Searching for directories... Please be patient...\n")
        try:
            directories = [full_directory] + scan_for_directories(full_directory)
        except PermissionError:
            print_error("Access to this directory was denied.")
            wait_for_enter()
            continue

        print(f"{len(directories)} folder(s) found.")
        wait_for_enter()

        # Filtering out directories
        while True:
            clear()
            print("Current directories:")
            for index, directory in enumerate(directories):
                is_excluded = "" if directory not in directories_excluded else " [yellow](excluded)[/yellow]"
                if index:
                    directory_formatted = reduce_path(directory, directories[0].split("\\")[-1])
                else:
                    directory_formatted = directory.split("\\")[-1]
                rprint(f"{index + 1}. {directory_formatted}{is_excluded}")

            user_input = input(
                "\nPlease enter the number of folder you wish to exclude (or include) (enter none to continue, \"*\" for exclude all): ").strip()
            if not user_input:
                break
            elif user_input == "*":
                directories_excluded = directories.copy()
            elif not user_input.isdigit():
                print("Please enter a number.")
                wait_for_enter()
                continue
            elif 0 > int(user_input) or int(user_input) > len(directories):
                print("Please enter a valid number of a directory listed above.")
                wait_for_enter()
                continue
            else:
                directory = directories[int(user_input) - 1]
                if directory in directories_excluded:
                    directories_excluded.remove(directory)
                else:
                    directories_excluded.append(directory)

            clear()
        directories_included = [x for x in directories if x not in directories_excluded]
        if not directories_included:
            print("You have excluded every directory.\nThere is nothing to search.")
            wait_for_enter()
            continue

        extensions = scan_for_extensions(directories_included)

        # Searching for extension
        print("Searching for directories... Please be patient...\n")
        extensions = scan_for_extensions(directories_included)
        print(f"{len(extensions)} extension(s) found.")
        wait_for_enter()

        # Filtering out extensions
        while True:
            clear()
            print("Extensions:")
            for index, extension in enumerate(extensions):
                is_excluded = " [yellow](excluded)[/yellow]" if extension not in extensions_included else ""
                rprint(f"{index + 1}. {extension}{is_excluded}")

            extension = input("\nEnter an extension you wish to include (enter none to continue, \"*\" for include all): ").strip().lower()
            if not extension:
                break

            if extension == "*":
                extensions_included = extensions.copy()
                continue

            if extension not in extensions:
                print("Please enter an extension that is in the list.")
                wait_for_enter()
                continue

            if extension in extensions_included:
                extensions_included.remove(extension)
            else:
                extensions_included.append(extension)
            clear()

        if not extensions_included:
            print("You have excluded every extension.\nThere is nothing to search.")
            wait_for_enter()
            continue
        clear()

        # Counting line counts
        print("Checking files...")
        try:
            directory_length_counts = accumulate_counts(directories_included, extensions_included)
            total = sum(directory_length_counts)
            print(f"\nThe total line length is {total}.")
            wait_for_enter()
        except UnicodeDecodeError as e:
            print_error(f"\nAn error occurred while decoding a file.\nException details: {str(e)}")
            wait_for_enter()

# Start
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear()
        sys.exit()
