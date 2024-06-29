# <img src="slime_hook.png" alt="SLime Hook Terraria item" style="width:1ch"> Slime Hook

A Python tool for publishing Terraria server chat messages to a Discord channel.

Named after the [Slime Hook](https://terraria.wiki.gg/wiki/Slime_hook) from Terraria (becuase it uses web*hooks* to send Discord messages). <!-- Haha I am indeed a comedic genius -->

## Documentation

### Expected environment

Although this tool was originally made as a value-add for my personal Terraria server, I've tried to make it easy to configure and run for whoever wants to use it. If you have any queries or issues, feel free to open an issue on this repository :)

- Slime Hook is intended to be used with a Terraria server running in a Docker container. I've tested it with the [ryshe/terraria](https://registry.hub.docker.com/r/ryshe/terraria/) image.
- If another tool (like Podman) provides a Docker-compatible API, it should work with that too.
- Other docker images should also work, as long as they provide log output to stdout.
- It sends messages when players join/leave using Discord webhooks. You'll have to create one in the settings of your preferred Discord channel.
- This tool is written in Python, so Python 3.9 or later is required to run it.

If you want to edit the messages sent, you have to modify the code. Look for the `LINE_TYPES` constant in the `SlimeHook` class. I'll make this configurable if there's demand for it.

### Deployment guide

1. Clone this repository onto the server running the Terraria server
2. Create a virtual environment for the project and install the dependencies from `requirements.txt`
3. Copy the YAML code from [the section below](#required-fields) into a new file at `./config.yaml` within the repository folder
4. Create a Discord webhook for the channel you want to send messages to, copy the URL, and enter it into the config file
5. Run the script: `python3 cli.py config.yaml`

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

This shows optional fields with their default values.

```yaml
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
  base_url: # e.g. tcp://127.0.0.1:2375 or unix://var/run/docker.sock
```

## Development instructions

Starting a test server:

```bash
docker run -it -p 7777:7777 --rm -v ./worlds:/root/.local/share/Terraria/Worlds --name terraria ryshe/terraria:vanilla-latest -world /root/.local/share/Terraria/Worlds/Test.wld -autocreate 1
```
