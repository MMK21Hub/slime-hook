#!/usr/bin/env python3
from sys import argv, stderr
from pydantic import ValidationError
import yaml

from slime_hook import Config, SlimeHook


def main():
    if len(argv) != 2:
        if len(argv) < 2:
            print("Please provide a path to a YAML config file", file=stderr)
        elif len(argv) > 2:
            print("Too many arguments", file=stderr)
        print(f"Usage: {argv[0]} <file>", file=stderr)
        exit(1)

    print(f"Using config from {argv[1]}")
    with open(argv[1], "r") as file:
        try:
            config_dict = yaml.safe_load(file)
            if not config_dict:
                print("Error: Config file is empty >:(", file=stderr)
                exit(2)
        except yaml.YAMLError as e:
            print(f"Syntax error in config: {e}", file=stderr)
            exit(2)
        try:
            parsed_config = Config(**config_dict)
        except ValidationError as error:
            print(f"Type error in config: {error}", file=stderr)
            exit(2)
        slime_hook = SlimeHook(parsed_config)

    try:
        if parsed_config.auto_retry:
            slime_hook.run_with_auto_retry()
        else:
            slime_hook.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        exit(0)


if __name__ == "__main__":
    main()
