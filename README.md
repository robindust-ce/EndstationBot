# EndstationBot
This repository contains a Telegram bot that revolves around the community room of the "SV Spandauer Damm e.V.". A Raspberry Pi Pico W services requests from telegram users via the telegram API and announces the status of a cam switch (or "basement status") in a selected group chat.


# Prerequisites

- Raspberry Pi Pico W with a [MicroPython installation](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
- Cam Switch (or any other switch)
- [thonny IDE](https://thonny.org/)


# Cam Switch

The Cam Switch is used to control the basement status. Position 2 corresponds to open and positions 1 and 0 correspond to closed. Using a green LED the basement status is visually indicated at the switch.
Whenever the position of the switch is changed and the switch position is not currently ignored (see /forceopen and /forceclose) the new basement status is broadcasted to a selected telegram group. To avoid sending multiple, unintended messages when the switch is activated multiple times in a short time frame there is a cooldown after each registered status change.

The Cam Switch connector 3 is wired up to GP28 (PIN 34) of the raspbery pi pico w. Connector 4 is connected to GND (PIN 38) and GP28 is therefore set up in pull-up mode. In addition, connector 12 is connected to 3.3V (PIN 36) and connector 11 to the anode of a green LED (with an appropriate series resistance).The cathode of the LED is connected to connector 4 and therefore to GND (PIN 38).

![Cam Switch](assets/camswitch.jpg?raw=true "")

# Commands

Bot commands are divided in two groups: Admin and General. Admin Commands are only accepted from a selected user or group (see "admins" key in secrets.py). General Commands however will be answered independent of the user. General Commands issued from groups trigger a cooldown to prevent spam (general commands during the cooldown period are ignored).

Messages containing a command need to start with "@EndstationBot" and must be shorter than 120 characters.

Using the keyword "silent" in the same message as a command will cause changes in the basement status not to be announced.

In addition to the commands EndstationBot responds with the basement status to messages, which contain keyword combinations such as "basement" and "open".

## Admin Commands

- **@EndstationBot forceclose**

Forces the basement status to closed, independent of the status of the cam switch. The cam switch is ignored until it reflects the current basement status again (either by changing the switch status or another force command).

- **@EndstationBot forceopen**

Like forceclose, but for changing the basement status to open.

- **@EndstationBot help**

Returns a list of all commands including explanations.


## General Commands

- **@EndstationBot basementstatus**

Returns the current basement status and the last time it was changed.

- **@EndstationBot basementinfo**

Returns an info message about the community room.
