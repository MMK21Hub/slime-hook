from datetime import datetime
import re
import docker
from docker.models.containers import Container


class Config:
    def __init__(
        self,
        container: str,
    ):
        """
        :param container: The ID or name of the Terraria server Docker container
        """
        self.container = container


def remove_ansii_escape_codes(string: str) -> str:
    # TODO: Decide if this will be necessary or not
    # Link: https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python?answertab=trending#tab-top
    pass


def handle_line(line: str):
    # FIXME: Regex doesn't handle IPv6 addresses (but I haven't spotted any  in the logs yet :/)
    connection_attempt = re.compile(r"^[\d\.]{7,15}:\d{1,5} is connecting\.\.\.")
    connection_booted = re.compile(
        r"^[\d\.]{7,15}:\d{1,5} was booted: Invalid operation at this state\."
    )
    player_joined = re.compile(r"^(.*) has joined.$")
    player_left = re.compile(r"^(.*) has left.$")
    chat_message = re.compile(r"^<(.*)> (.*)$")
    world_save_progress = re.compile(r"^Saving world data: (\d+)%")
    world_validation_progress = re.compile(r"^Validating world save: (\d+)%")
    world_backup = re.compile(r"^Backing up world file")
    terraria_error = re.compile(r"^Error on message Terraria\.MessageBuffer")

    if chat_message.match(line):
        player = chat_message.match(line).group(1)
        message = chat_message.match(line).group(2)
        print(f'"{player}" said "{message}"')
    elif player_joined.match(line):
        player = player_joined.match(line).group(1)
        print(f'"{player}" joined the server')
    elif player_left.match(line):
        player = player_left.match(line).group(1)
        print(f'"{player}" left the server')

    elif connection_attempt.match(line):
        pass
    elif connection_booted.match(line):
        pass
    elif world_save_progress.match(line):
        pass
    elif world_validation_progress.match(line):
        pass
    elif world_backup.match(line):
        pass
    elif terraria_error.match(line):
        pass
    else:
        print(f"{line.encode()}")


def main(config: Config):
    client = docker.from_env()
    container: Container = client.containers.get(config.container)
    log_parts = container.logs(since=datetime.now(), follow=True, stream=True)
    print("Listening to log output from container...")
    line_buffer = ""
    for log in log_parts:
        line_buffer += log.decode("utf-8")
        # Split the buffer into lines just in case the current part has multiple newlines
        if "\n" in line_buffer:
            lines = line_buffer.split("\n")
            for line in lines[:-1]:
                handle_line(line)
            line_buffer = lines[-1]


if __name__ == "__main__":
    config = Config(container="terraria")
    try:
        main(config)
    except KeyboardInterrupt:
        print("\nExiting...")
