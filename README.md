# NVDA-Time-Zoner
An add-on for NVDA to announce the time in a selected timezone.

## Introduction
For a very long time now, Windows has had the ability to show multiple clocks from different timezones. Users can customize the clocks and they become instantly visible.

Unfortunately, for users of screen readers such as [NVDA](https://www.nvaccess.org/) or [JAWS](http://www.freedomscientific.com), there is no simple way to get this information. These screen readers don't support additional clocks, so blind computer users have to resort to other, third-party solutions, some of which are paid.

A lot of the work I do involves working across timezones, and eventually I got tired of manually converting times in my head, especially for timezones that aren't aligned to the hour (such as India which is +5:30 UTC.)

For these reasons, I've created this add-on for NVDA. The add-on lets you hear a time in a selected timezone through a simple key-press.

## Usage
You can either compile the Master branch yourself, or grab the nvda-addon file from the releases page. The add-on supports both the legacy and the Python 3 version of NVDA.

Once the add-on is installed, press NVDA+N to bring up NVDA's context menu. Arrow down to "Preferences" and then up to "Configure Timezones."

Press ENTER on "Set Timezone."

You will be presented with a dialog to set the timezone for which you want the time and date announced.

Once you've set the timezone, press NVDA+F12 three times quickly to hear the time in that timezone. Press the key four times quickly to hear the date in the selected timezone.