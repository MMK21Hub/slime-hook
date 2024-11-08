# <img src="slime_hook.png" alt="SLime Hook Terraria item" style="width:1ch"> Slime Hook

[![Built during Arcade 2024](https://badges.api.lorebooks.wiki/badges/hackclub/arcade)](https://hackclub.com/arcade)
![Hakatime time tracking](https://waka.hackclub.com/api/badge/U073M5L9U13/interval:any/project:slime-hook?label=Hakatime)

A Python tool for publishing Terraria server chat messages to a Discord channel.

Named after the [Slime Hook](https://terraria.wiki.gg/wiki/Slime_hook) from Terraria (because it uses web*hooks* to send Discord messages). <!-- Haha I am indeed a comedic genius -->

![A screenshot of Discord messages showing a player joining, talking about Slime Hook in chat, leaving, and the server stopping](assets/slime-hook-demo.png)

## Documentation

### Expected environment

Although this tool was originally made as a value-add for my personal Terraria server, I've tried to make it easy to configure and run for whoever wants to use it. If you have any queries or issues, feel free to open an issue on this repository :)

- Slime Hook is intended to be used with a Terraria server running in a Docker container. I've tested it with the [ryshe/terraria](https://registry.hub.docker.com/r/ryshe/terraria/) image.
- Other Docker images should also work, as long as they provide log output to stdout.
- If container manager (like Podman) provides a Docker-compatible API, it should work with that too.
- It sends messages when players join/leave using Discord webhooks. You'll have to create one in the settings of your preferred Discord channel.
- This tool is written in Python, so Python 3.9 or later is required to run it.

If you want to edit the messages sent, you have to modify the code. Look for the `LINE_TYPES` constant in the `SlimeHook` class. I'll make this configurable if there's demand for it.

### Deployment guide

The easiest way to deploy Slime Hook is using `docker compose`. If you don't have access to Docker, then you can follow the [non-Docker deployment guide](#non-docker-deployment-guide).

Start off by creating a folder for your compose file and Slime Hook config. Inside it, create a file named `config.yaml` with the following content:

```yaml
services:
  slime-hook:
    image: mmk21/slime-hook:latest
    volumes:
      - ./config.yaml:/config.yaml
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped
```

Then, configure the tool by the YAML code from [the section below](#required-fields) into a new file called `config.yaml` in out folder. Edit it so that the `container` field matches the name of the Docker container that runs your Terraria server, and set `discord_webhook_url` to the URL of the Discord webhook you created.

Finally, create and start the containers with `docker compose`:

```bash
docker compose up -d
```

Feel free to customize the compose file to suit your needs. I'd also recommend adding the `auto_retry` option to your `config.yaml` (see the [optional config fields](#optional-fields) section for details).

### Config file

Slime Hook is configured using a YAML file provided as an argument to the CLI, e.g. `cli.py config.yaml`.

The available options are listed below to show the format the data should be in.

#### Required fields

Your config file should look similar to this to successfully run the script.

```yaml
# The ID or name of the Terraria server Docker container
container: terraria
# The full URL of the Discord webhook to send messages to
discord_webhook_url: https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz
```

#### Optional fields

This shows optional fields with some suggested values.

```yaml
# Customise which kinds of log messages should be sent to Discord
log_messages:
  connection_attempt: False # Warning: This will reveal users' IP addresses
  connection_booted: False # Warning: This will reveal users' IP addresses
  player_joined: True
  player_left: True
  chat_message: True
  world_backup: False
  terraria_error: False
  server_listening: True
  server_stopped: True
# When provided, Slime Hook will be restarted if certain errors occur, such as the container being stopped or removed
# This is useful when the script is automatically running in the background
# The auto-retry feature will only be enabled for error types specified under `auto_retry`
auto_retry:
  container_not_found:
    # The number of seconds to wait between attempts
    interval_seconds: 120
  container_not_running:
    interval_seconds: 5
# Specify how Slime Hook should connect to the Docker daemon
# If not specified, configuration will come from environment variables
# See upstream docs for details: https://docker-py.readthedocs.io/en/stable/client.html#docker.client.from_env
docker_connection:
  base_url: unix://var/run/docker.sock # Or a URL like tcp://127.0.0.1:2375
```

### Non-Docker deployment guide

1. Clone this repository onto the server running the Terraria server
2. Create a virtual environment for the project and install the dependencies from `requirements.txt`
3. Copy the YAML code from [the section above](#required-fields) into a new file at `./config.yaml` within the repository folder
4. Create a Discord webhook for the channel you want to send messages to, copy the URL, and enter it into the config file
5. Run the script: `python3 cli.py config.yaml`

## Demo video

Click the image below to watch a brief video demo of Slime Hook (<https://youtube.com/watch?v=RB2MHu3Dz5s>).

[![Slime Hook demo: Bridge your Terraria server with a Discord channel - YouTube)](assets/youtube-video-snapshot.png)](https://www.youtube.com/watch?v=RB2MHu3Dz5s)

## Documentation for developing Slime Hook

Starting a test server:

```bash
docker run -it -p 7777:7777 --rm -v ./worlds:/root/.local/share/Terraria/Worlds --name terraria ryshe/terraria:vanilla-latest -world /root/.local/share/Terraria/Worlds/Test.wld -autocreate 1
```

### Publishing a new release

The steps are something like this. We can probably make this a Bash script or even a GitHub action if we want to be fancy.

So that multiple architectures can be built, you must set Docker to use the containerd image store, as explained [in the Docker documentation](https://docs.docker.com/storage/containerd/). You also need to [install the `arm64` emulator for Docker](https://github.com/tonistiigi/binfmt?tab=readme-ov-file#installing-emulators) to build the ARM64 image in an x86 computer (or vice versa if you're using an ARM computer), so run `docker run --privileged --rm tonistiigi/binfmt --install arm64`.

```bash
export VERSION=v1.x.y # Replace with the new version number
git checkout main

git tag $VERSION
git push origin $VERSION

docker build -t mmk21/slime-hook:$VERSION --platform linux/amd64,linux/arm64 .
docker push mmk21/slime-hook:$VERSION

docker tag mmk21/slime-hook:$VERSION mmk21/slime-hook:latest
docker push mmk21/slime-hook:latest
```
