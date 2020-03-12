# NVDA-Time-Zoner
An add-on for NVDA to announce the time in selected timezones.

## Introduction
For a very long time now, Windows has had the ability to show multiple clocks from different timezones. Users can customize the clocks and they become instantly visible.

Unfortunately, for users of screen readers such as [NVDA](https://www.nvaccess.org/) or [JAWS](http://www.freedomscientific.com), there is no simple way to get this information. These screen readers don't support additional clocks, so blind computer users have to resort to other, third-party solutions, some of which are paid.

A lot of the work I do involves working across timezones, and eventually I got tired of manually converting times in my head, especially for timezones that aren't aligned to the hour (such as India which is +5:30 UTC.)

For these reasons, I've created this add-on for NVDA. The add-on lets you hear times in selected timezones through the use of the "timezone ring."

## Usage
You can either download and unzip the Master branch yourself, or grab the [latest NVDA add-on file from the releases page](releases/latest). The add-on supports both the legacy and the Python 3 version of NVDA.

Once the add-on is installed, press NVDA+N to bring up NVDA's context menu. Arrow down to "Preferences" and then up to "Time Zoner."

Press ENTER on "Configure Timezone Ring."

You will be presented with a dialog to set the timezones for which you want the time and date announced.

Select items in the timezone list to add them to your timezone ring. Deselect (or press the "Remove" button)  to remove them from the ring.

You can also reorder the timezones in the ring by using the "Move Up" and "Move Down" buttons.

Use the "Filter" box to search for specific timezones.

Check the "Announce abbreviated timezones" box to hear abbreviated timezone names such as IST or GMT. Uncheck the box to hear the full timezone names such as Asia/Kolkata or Europe/London.

When you are finished configuring the timezones, press the "Save" button.

From here on, you can press NVDA+ALT+T to announce times and dates in your timezone ring.

When you first install the add-on, NVDA will default to your local timezone if it can get it.