# Slime Hook

A Python tool for publishing Terraria server chat messages to a Discord channel.

Named after the [Slime Hook](https://terraria.wiki.gg/wiki/Slime_hook) from Terraria becuase it uses webhooks to send Discord messages. <!-- Haha I am indeed a comedic genius -->

## Documentation

- This tool is intended to be used with a Terraria server running in a Docker container. I've tested it with the [ryshe/terraria](https://registry.hub.docker.com/r/ryshe/terraria/) image.
- It sends messages when players join/leave using Discord webhooks. You'll have to create one in the settings for your prefered Discord channel.

## Development instructions

Starting a test server:

```bash
docker run -it -p 7777:7777 --rm -v ./worlds:/root/.local/share/Terraria/Worlds --name terraria ryshe/terraria:vanilla-latest -world /root/.local/share/Terraria/Worlds/Test.wld -autocreate 1
```
