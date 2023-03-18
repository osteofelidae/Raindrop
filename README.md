# Raindrop

A discord bot for synchronizing announcements, events, and bans between servers.




## Features
* Syncronizing announcements within a server group
* Propagating event announcements within a server group
* Propagating bans within a server group



## Commands
Syntax: command(essential_arg, \[optional_arg\])

`about()` - Returns info about the bot and a link to this GitHub page.

`setup([announcement_channel,] [bot_channel,] [sync_list,] [auto_event,] [auto_announce])` - Sets up server. All parameters must be input at some point for all features to work.
* announcement_channel: The channel where other servers' announcements will be mirrored, and where announcements will be autodetected if auto_event == true.
* bot_channel: The channel where asynchronous bot output will go. For admin use only.
* sync_list: A code referring to the server group. Multiple servers with the same sync_list value will form a server group, and announcements will propagate between all servers in that group.
* auto_event: Boolean value of whether an announcement is created and propagated automatically when an event is created.
* auto_announce: Boolean value of whether an announcement is propagated automatically when it is sent in announcement_channel.

`announce(title, content, [url,], [ping_role])` - Creates an announcement embed and propagates it throughout the server group.
* title: The title of the announcement
* content: The content of the announcement
* url: The link which clicking the title leads to
* ping_role: The role that is pinged by the announcement. Only pings in the source server.

`cross_ban(user, [reason])` - Bans a user in the server group.
* user - The user to ban.
* reason - The reason provided for the ban.