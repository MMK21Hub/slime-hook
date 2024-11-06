from datetime import datetime
import re
import time
from typing import Callable, Optional
import docker
import docker.errors
from docker.models.containers import Container
import requests
from pydantic import BaseModel


class AutoRetryConfig(BaseModel):
    interval_seconds: float


class AutoRetryConfigs(BaseModel):
    container_not_found: Optional[AutoRetryConfig] = None
    container_not_running: Optional[AutoRetryConfig] = None


class DockerConnection(BaseModel):
    base_url: str


class EnabledLogMessages(BaseModel):
    connection_attempt: bool = False
    connection_booted: bool = False
    player_joined: bool = True
    player_left: bool = True
    chat_message: bool = True
    world_backup: bool = True
    terraria_error: bool = True
    server_listening: bool = True
    server_stopped: bool = True


class Config(BaseModel):
    container: str
    discord_webhook_url: str
    auto_retry: Optional[AutoRetryConfigs] = None
    docker_connection: Optional[DockerConnection] = None
    log_messages: EnabledLogMessages = EnabledLogMessages()


class LogLineType:
    def __init__(
        self,
        name: str,
        regex: str,
        is_enabled: bool = False,
        callback: Optional[Callable[..., None]] = None,
        capture_groups: int = 0,
    ):
        self.name = name
        self.regex = regex
        self.callback = callback
        self.capture_groups = capture_groups
        self.is_enabled = is_enabled

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

        if self.is_enabled:
            if self.callback:
                self.callback(*groups)
            else:
                print(
                    f"Warning: Tried to send a {self.name} log message, but it has not been implemented"
                )
        return True


class ContainerNotRunning(RuntimeError):
    pass


class SlimeHook:
    def __init__(self, config: Config) -> None:
        self.config = config
        # FIXME: Regex doesn't handle IPv6 addresses (not that I've spotted any in the wild yet :/)
        self.LINE_TYPES = [
            LogLineType(
                "connection_attempt",
                r"^[\d\.]{7,15}:\d{1,5} is connecting\.\.\.",
                is_enabled=self.config.log_messages.connection_attempt,
            ),
            LogLineType(
                "connection_booted",
                r"^[\d\.]{7,15}:\d{1,5} was booted: Invalid operation at this state\.",
                is_enabled=self.config.log_messages.connection_booted,
            ),
            LogLineType(
                "player_joined",
                r"^(.*) has joined.$",
                is_enabled=self.config.log_messages.player_joined,
                callback=lambda player: self.send_discord_message(
                    f":inbox_tray: **{player}** has joined"
                ),
                capture_groups=1,
            ),
            LogLineType(
                "player_left",
                r"^(.*) has left.$",
                is_enabled=self.config.log_messages.player_left,
                callback=lambda player: self.send_discord_message(
                    f":outbox_tray: **{player}** has left"
                ),
                capture_groups=1,
            ),
            LogLineType(
                "chat_message",
                r"^<(.*)> (.*)$",
                is_enabled=self.config.log_messages.chat_message,
                callback=lambda player, message: self.send_discord_message(
                    f"<**{player}**> {message}"
                ),
                capture_groups=2,
            ),
            LogLineType(
                "world_save_progress",
                r"^Saving world data: (\d+)%",
                is_enabled=self.config.log_messages.world_backup,
                capture_groups=1,
            ),
            LogLineType(
                "world_validation_progress",
                r"^Validating world save: (\d+)%",
                capture_groups=1,
            ),
            LogLineType(
                "world_backup",
                r"^Backing up world file",
                is_enabled=self.config.log_messages.world_backup,
                callback=lambda: self.send_discord_message(
                    "_Backup successfully created_"
                ),
            ),
            LogLineType(
                "terraria_error",
                r"^Error on message Terraria\.MessageBuffer",
                is_enabled=self.config.log_messages.terraria_error,
            ),
            LogLineType(
                "world_load_objects_progress",
                r"^Resetting game objects (\d+)%",
                capture_groups=1,
            ),
            LogLineType(
                "world_load_data_progress",
                r"^Loading world data: (\d+)%",
                capture_groups=1,
            ),
            LogLineType(
                "world_load_liquids_progress",
                r"^Settling liquids (\d+)%",
                capture_groups=1,
            ),
            LogLineType(
                "server_listening",
                r"^Listening on port \d+",
                is_enabled=self.config.log_messages.server_listening,
                callback=lambda: self.send_discord_message(
                    ":zap: **Server has started!**"
                ),
            ),
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
        for line_type in self.LINE_TYPES:
            did_process_line = line_type.process_line(line)
            if did_process_line:
                return line_type
        print(line.encode())

    def get_docker_client(self):
        conn_options = self.config.docker_connection
        if not conn_options:
            return docker.from_env()
        return docker.DockerClient(base_url=conn_options.base_url)

    def run(self):
        client = self.get_docker_client()

        container: Container = client.containers.get(self.config.container)
        if container.status != "running":
            raise ContainerNotRunning(f'Container "{container.name}" is not running')
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
                    try:
                        self.handle_line(line)
                    except Exception as exception:
                        print(f"Failed to process line: {line}")
                        print(exception)
                line_buffer = lines[-1]

        # If we get here then it usually means the container has stopped
        self.send_discord_message(":skull: **Server has stopped**")
        raise ContainerNotRunning(f'Container "{container.name}" is not running')

    def run_with_auto_retry(self):
        if not self.config.auto_retry:
            raise ValueError("No auto_retry config provided")

        has_shown_message = False

        def retry_later(
            error: Exception, retry_options: Optional[AutoRetryConfig], message: str
        ):
            if not retry_options:
                raise error
            nonlocal has_shown_message
            if not has_shown_message:
                print(message)
                has_shown_message = True
            time.sleep(retry_options.interval_seconds)

        while True:
            try:
                self.run()
                break
            except docker.errors.NotFound as error:
                retry_later(
                    error,
                    self.config.auto_retry.container_not_found,
                    f'Docker container "{self.config.container}" not found, retrying in background...',
                )
                continue
            except ContainerNotRunning as error:
                retry_later(
                    error,
                    self.config.auto_retry.container_not_running,
                    f'Docker container "{self.config.container}" not running, retrying in background...',
                )
                continue
