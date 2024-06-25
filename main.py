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


def main(config: Config):
    client = docker.from_env()
    container: Container = client.containers.get(config.container)
    log_lines = container.logs(since=datetime.now(), follow=True, stream=True)
    for log in log_lines:
        print(log.decode("utf-8"), end="")


if __name__ == "__main__":
    config = Config(container="terraria")
    main(config)
