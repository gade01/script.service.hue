[![Build Status](https://travis-ci.com/zim514/script.service.hue.svg?branch=master)](https://travis-ci.com/zim514/script.service.hue) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/1a4a910144f044208821341f1a07c38e)](https://www.codacy.com/app/zim514/script.service.hue?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=zim514/script.service.hue&amp;utm_campaign=Badge_Grade)
# script.service.hue
**Kodi Service for Philips Hue**

## Installation
<<<<<<< HEAD

 1. [Download latest .zip version](https://github.com/zim514/script.service.hue/releases)
 2. [Install to Kodi from Zip](https://kodi.wiki/view/HOW-TO:Install_add-ons_from_zip_files)

=======
[Download latest version](https://github.com/zim514/script.service.hue/releases)
>>>>>>> README.md updated from https://stackedit.io/

## Features:
- Create and delete multi-room LightScenes
	- Adjust your lights as desired, and use the add-on to select the lights and transition time.
	- Supports lights in multiple rooms or groups.
	- The official Hue app won't show scenes made outside of the official app, but most 3rd party apps will let you see and edit your scene
-   Apply selected scene on playback
	- Select scenes to apply when on Play, Pause and Stop
	- Separate scenes for Audio or Video playback
-   Daylight detection
	- Uses Hue's sunrise and sunset settings
	- Disable during daylight hours
	- If sunset falls while watching media, optionally turn on lights
	- Add-on does nothing at sunset if there's no playback


## Notes:
- Hue Bridge with nPNP only
	- Requires bridge & Kodi connectivity to Philipps servers ( https://discovery.meethue.com/ ) 
- Does not support multiple bridges on your network
- Only tested on LibreElec 9.0.2 & Windows 10, but no reason it shouldn't work anywhere.
- No ambilight / dynamic lighting support.
	- If anyone knows a good algorithm to generate colours from a screenshot, I'll be looking into this in the future.


## Problems?
- Make sure you update your Hue bridge to the latest version. This add-on assumes you have the latest features
- Turn on debug logging or the addon's logging (in addon_data)


## Credits:
- Based on original plugin by cees-elzinga, michaelrcarroll, mpolednik
- Uses Qhue (C) Quentin Stafford-Fraser - https://github.com/quentinsf/qhue
<!--stackedit_data:
<<<<<<< HEAD
eyJoaXN0b3J5IjpbMTI2MDI1ODI4NywtMjEzNDQ5MzI0Nl19
=======
eyJoaXN0b3J5IjpbMTAzODI1NzU3OCwtMjEzNDQ5MzI0Nl19
>>>>>>> README.md updated from https://stackedit.io/
-->