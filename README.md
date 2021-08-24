# Subrift
Discord Music Bot that allows the user to play songs from a bot in Discord from any server that supports the subsonic API.

## Setup
* Requires you to create a discord bot in https://discord.com/developers/applications
* Requires a json file `subrift.json` containing the following:

```
{
    "USER":{
        "USERNAME": "[Username]",
        "SUBSONICPASSWORD": "[SubsonicPassword]"
    },
    "DISCORDTOKEN":"[DiscordBotToken]",
    "URL":"[ServerUrl]"
}
```
Place `subrift.json` inside main folder.
