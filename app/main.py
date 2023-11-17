import sys
from . command_handler import handle_command


def main():
    command = sys.argv[1]
    handle_command(command)


if __name__ == "__main__":
    main()
