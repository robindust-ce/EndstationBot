# EndstationBot
This repository contains a Telegram bot that revolves around the community room of the "SV Spandauer Damm e.V.". A Raspberry Pi Pico W services requests from telegram users via the telegram API and announces the status of a cam switch in a selected group chat.


# Prerequisites

- Raspberry Pi Pico W with a MicroPython installation
- Cam Switch (or any other button/switch)
- thonny IDE


# Commands

Bot commands are divided in two groups: Admin and General. Admin Commands are only accepted from a selected user or group (see "admins" key in secrets.py). General Commands however will be answered independent of the user. General Commands issued from groups trigger a cooldown to prevent spam (general commands during the cooldown period are ignored).

Using the keyword "silent" in the same message as a command will cause changes in the basement status not to be announced.

In addition to the commands EndstationBot responds with the basement status to messages, which contain keyword combinations such as "basement" and "open".

## Admin Commands

- /forceclose

Forces the basement status to closed, independent of the status of the cam switch. The cam switch is ignored until it reflects the current basement status again (either by changing the switch status or another /force command).

- /forceopen

Like /forceclose, but for changing the basement status to open.

- /help

Returns a list of all commands including explanations.


## General Commands

- /basementstatus

Returns the current basement status and the last time it was changed.

- /basementinfo

Returns an info message about the community room.