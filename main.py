from datetime import datetime
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
    pass


def handle_line(line: str):
    # print(f"{line.encode('utf-8')}")
    print(">", line)


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
        print("Exiting...")
