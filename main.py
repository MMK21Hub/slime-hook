from datetime import datetime
import re
import docker
from docker.models.containers import Container
import requests


class Config:
    def __init__(
        self,
        container: str,
        discord_webhook_url: str,
    ):
        """
        :param container: The ID or name of the Terraria server Docker container
        :param discord_webhook_url: The full URL of the Discord webhook to send messages to
        """
        self.container = container
        self.discord_webhook_url = discord_webhook_url


def remove_ansii_escape_codes(string: str) -> str:
    # TODO: Decide if this will be necessary or not
    # Link: https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python?answertab=trending#tab-top
    pass


class SlimeHook:
    def __init__(self, config: Config) -> None:
        self.config = config

    def send_discord_message(self, message: str):
        requests.post(
            self.config.discord_webhook_url,
            json={
                "content": message,
            },
        )

    def handle_line(self, line: str):
        line = line.strip()
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
            self.send_discord_message(f"<**{player}**> {message}")
        elif player_joined.match(line):
            player = player_joined.match(line).group(1)
            self.send_discord_message(f":inbox_tray: **{player}** has joined")
        elif player_left.match(line):
            player = player_left.match(line).group(1)
            self.send_discord_message(f":outbox_tray: **{player}** has left")
        elif world_backup.match(line):
            self.send_discord_message("_Backup successfully created_")
        elif connection_attempt.match(line):
            pass
        elif connection_booted.match(line):
            pass
        elif world_save_progress.match(line):
            pass
        elif world_validation_progress.match(line):
            pass
        elif terraria_error.match(line):
            pass
        else:
            print(f"{line.encode()}")

    def run(self):
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
                    self.handle_line(line)
                line_buffer = lines[-1]


if __name__ == "__main__":
    config = Config(
        container="terraria",
        # Test server webhook. Send me some messages if you really want to :)
        discord_webhook_url="https://discord.com/api/webhooks/1255891706750963732/8XeM600_nsEqh0MnTLKC56Hw3yQsd4_1hDx67kyQh3w_e64ysW2vtAlMPxwz6WnBGGKq",
    )
    try:
        app = SlimeHook(config)
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
