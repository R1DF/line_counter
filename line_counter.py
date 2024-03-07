# Imports
from rich.console import Console
import questionary
import os
import readchar
import sys

# Constants
CONSOLE = Console()


# Functions
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_error(text: str):
    CONSOLE.print(text, style="red")


def print_green(text: str):
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


def scan_for_directories(path: str, original_directory="") -> list[str]:
    results = []
    if not original_directory:
        original_directory = path.split("\\")[-1]

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
        directories = [full_directory] + scan_for_directories(full_directory)
        print(f"{len(directories)} folder(s) found.")
        wait_for_enter()
        clear()

        # Filtering out directories
        user_input = ""
        while True:
            print("Current directories:")
            for index, directory in enumerate(directories):
                is_excluded = "" if directory not in directories_excluded else " (excluded)"
                if index:
                    directory_formatted = reduce_path(directory, directories[0].split("\\")[-1])
                else:
                    directory_formatted = directory.split("\\")[-1]
                print(f"{index + 1}. {directory_formatted}{is_excluded}")

            user_input = input(
                "\nPlease enter the number of folder you wish to exclude (or include) (enter none to continue): ").strip()
            if not user_input:
                break
            elif not user_input.isdigit():
                print("Please enter a number.")
            elif 0 > int(user_input) or int(user_input) > len(directories):
                print("Please enter a valid number of a directory listed above.")
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
        clear()

        # Filtering out extensions
        while True:
            print("Extensions:")
            for index, extension in enumerate(extensions):
                is_excluded = " (excluded)" if extension not in extensions_included else ""
                print(f"{index + 1}. {extension}{is_excluded}")

            extension = input("\nEnter an extension you wish to include (enter none to continue): ").strip().lower()
            if not extension:
                break

            if extension not in extensions:
                print("Please enter an extension that is in the list.")
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
        directory_length_counts = accumulate_counts(directories_included, extensions_included)
        total = sum(directory_length_counts)
        print(f"\nThe total line length is {total}.")
        wait_for_enter()


# Start
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear()
        sys.exit()
