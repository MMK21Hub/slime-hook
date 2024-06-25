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
    pass


if __name__ == "__main__":
    config = Config(container="terraria")
    main(config)
