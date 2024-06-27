# Slime Hook

A Python tool for publishing Terraria server chat messages to a Discord channel.

Named after the [Slime Hook](https://terraria.wiki.gg/wiki/Slime_hook) from Terraria becuase it uses webhooks to send Discord messages. <!-- Haha I am indeed a comedic genius -->

## Documentation

- This tool is intended to be used with a Terraria server running in a Docker container. I've tested it with the [ryshe/terraria](https://registry.hub.docker.com/r/ryshe/terraria/) image.
- It sends messages when players join/leave using Discord webhooks. You'll have to create one in the settings for your prefered Discord channel.

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
# When true, the CLI will keep trying to connect to the Docker container if it's not present
# This means that the script can automatically start when the container is started
# When false, the CLI will exit with an error if the container is not found (useful for testing)
auto_retry: false
```

### Deployment guide

1. Clone this repository onto the server running the Terraria server
2. Create a virtual environment for the project and install the dependencies from `requirements.txt`
3. Copy the YAML code from above into a new file at `./config.yaml` within the repository folder
4. Run the script: `python3 cli.py config.yaml`

## Development instructions

Starting a test server:

```bash
docker run -it -p 7777:7777 --rm -v ./worlds:/root/.local/share/Terraria/Worlds --name terraria ryshe/terraria:vanilla-latest -world /root/.local/share/Terraria/Worlds/Test.wld -autocreate 1
```
