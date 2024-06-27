from datetime import datetime
import re
from typing import Callable
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


class LogLineType:
    def __init__(
        self,
        name: str,
        regex: str,
        callback: Callable[..., None] | None = None,
        capture_groups: int = 0,
    ):
        name = name
        self.regex = regex
        self.callback = callback
        self.capture_groups = capture_groups

    def match(self, line: str):
        return re.compile(self.regex).match(line)

    def process_line(self, line: str) -> bool:
        match_result = self.match(line)
        if not match_result:
            return False
        groups = match_result.groups()
        if len(groups) != self.capture_groups:
            raise ValueError(
                f"Expected {self.capture_groups} capture groups, but got {len(groups)}"
            )

        if self.callback:
            self.callback(*groups)
        return True


class SlimeHook:
    def __init__(self, config: Config) -> None:
        self.config = config
        # FIXME: Regex doesn't handle IPv6 addresses (but I haven't spotted any  in the logs yet :/)
        self.LINE_TYPES = [
            LogLineType(
                "connection_attempt", r"^[\d\.]{7,15}:\d{1,5} is connecting\.\.\."
            ),
            LogLineType(
                "connection_booted",
                r"^[\d\.]{7,15}:\d{1,5} was booted: Invalid operation at this state\.",
            ),
            LogLineType(
                "player_joined",
                r"^(.*) has joined.$",
                callback=lambda player: self.send_discord_message(
                    f":inbox_tray: **{player}** has joined"
                ),
                capture_groups=1,
            ),
            LogLineType(
                "player_left",
                r"^(.*) has left.$",
                callback=lambda player: self.send_discord_message(
                    f":outbox_tray: **{player}** has left"
                ),
                capture_groups=1,
            ),
            LogLineType(
                "chat_message",
                r"^<(.*)> (.*)$",
                callback=lambda player, message: self.send_discord_message(
                    f"<**{player}**> {message}"
                ),
                capture_groups=2,
            ),
            LogLineType("world_save_progress", r"^Saving world data: (\d+)%"),
            LogLineType("world_validation_progress", r"^Validating world save: (\d+)%"),
            LogLineType(
                "world_backup",
                r"^Backing up world file",
                callback=lambda: self.send_discord_message(
                    "_Backup successfully created_"
                ),
            ),
            LogLineType("terraria_error", r"^Error on message Terraria\.MessageBuffer"),
        ]

    def send_discord_message(self, message: str):
        requests.post(
            self.config.discord_webhook_url,
            json={
                "content": message,
            },
        )

    def handle_line(self, line: str):
        line = line.strip()
        handled = False
        for line_type in self.LINE_TYPES:
            if line_type.process_line(line):
                handled = True
                break
        if not handled:
            print(line.encode())

    def run(self):
        client = docker.from_env()
        container: Container = client.containers.get(config.container)
        incoming_log_parts = container.logs(
            since=datetime.now(), follow=True, stream=True
        )
        print("Listening to log output from container...")
        line_buffer = ""
        for log in incoming_log_parts:
            try:
                decoded_line = log.decode("utf-8")
            except UnicodeDecodeError:
                continue
            line_buffer += decoded_line
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
