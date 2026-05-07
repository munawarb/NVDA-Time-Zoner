# Time Zoner
An add-on for NVDA to announce the time in selected timezones.

## Information
* Author: Munawar Bijani
* Download [stable version][1]
* Compatibility: NVDA 2021.1 and later

## Introduction
For a very long time now, Windows has had the ability to show multiple clocks from different timezones. Users can customize the clocks and they become instantly visible.

Unfortunately, for users of screen readers such as [NVDA](https://www.nvaccess.org/) or [JAWS](http://www.freedomscientific.com), there is no simple way to get this information. These screen readers don't support additional clocks, so blind computer users have to resort to other, third-party solutions, some of which are paid.

A lot of the work I do involves working across timezones, and eventually I got tired of manually converting times in my head, especially for timezones that aren't aligned to the hour (such as India which is +5:30 UTC.)

For these reasons, I've created this add-on for NVDA. The add-on lets you hear times in selected timezones through the use of the "timezone ring."

## Usage
You can [download the latest release here][1]. The add-on supports both the legacy and the Python 3 version of NVDA.

Once the add-on is installed, you can configure it by activating NVDA's settings dialog and going down to the "Time Zoner" category.

Select items in the timezone list to add them to your timezone ring. Deselect (or press the "Remove" button)  to remove them from the ring.

You can also reorder the timezones in the ring by using the "Move Up" and "Move Down" buttons.

Use the "Filter" box to search for specific timezones.

Check the "Announce abbreviated timezones" box to hear abbreviated timezone names such as IST or GMT. Uncheck the box to hear the full timezone names such as Asia/Kolkata or Europe/London.

You can configure what information you hear when querying the time in a timezone by checking/unchecking the boxes in the "Components" group:

* Continent: Announce the continent for the current timezone.
* Country: Announce the country for the current timezone.
* City: Announce the city for the current timezone.
* Time: Announce the time for the current timezone.
* Date: Announce the date for the current timezone.
* Announce timezone at (Beginning or End): Say the timezone first, or as the last thing you hear. For example, if you wish to hear "BST 9:42 AM", select the "Beginning" radio button. If you wish to hear 9:42 AM (BST)", select the "End" radio button.

When you are finished configuring your preferences, press the "OK" button.

From here on, you can press the following keys to announce times in your timezone ring:

* NVDA+ALT+UP ARROW: Announce the previous timezone.
* NVDA+ALT+DOWN ARROW: Announce the next timezone.
* NVDA+ALT+T: Announce the last timezone you were pointing at in your timezone ring. Pressing this key multiple times in rapid succession will move forward through your timezone ring but will not change the timezone at which you are pointing.
* To configure these keys, use the "Time Zoner" category in the "Input Gestures" dialog.

When you first install the add-on, NVDA will default to your local timezone if it can get it.

## Acknowledgements
Thanks to [@ruifontes](https://github.com/ruifontes) for helping significantly to make this add-on compliant with NVAccess add-on code guidelines. Thanks to Myla for testing the add-on on NVDA 2019.2.

## Change Log

### Version 3.01, released on 03/26/2022
- Blocked scripts from running in NVDA Secure Mode.

### Version 3.00, released on 03/24/2022
- Now compatible with version 2022.1 of NVDA.
- Fixed an issue where two configuration categories would show up if the add-on was reloaded ([#10](https://github.com/munawarb/NVDA-Time-Zoner/issues/10))

### Version 2.00, released on 07/14/2021
- Now compatible with version 2021.1 of NVDA.
- BREAKING CHANGE: This add-on is no longer compatible with legacy versions of NVDA. Please use version 1.06 or earlier for legacy support.

### Version 1.05, released on 07/26/2020
- Fixed a crash when announcing general timezones such as UTC or EST ([#7](https://github.com/munawarb/NVDA-Time-Zoner/issues/7))

### Version 1.04, released on 04/19/2020
- Timezone announcements are now customizable. In addition, pressing NVDA+ALT+UP ARROW or NVDA+ALT+DOWN ARROW will cycle through the timezone ring, making the add-on user-friendly for configurations with many timezones set ([#6](https://github.com/munawarb/NVDA-Time-Zoner/issues/6))
- The "Input Gestures" dialog uses a new category, "Time Zoner", to make it easier to find gestures for the Time Zoner add-on ([#5](https://github.com/munawarb/NVDA-Time-Zoner/issues/5))
- Settings are configured using the NVDA Settings dialog instead of through a stand-alone dialog.

### Version 1.03, released on 03/21/2020
- The add-on no longer crashes if the default timezone can't be set.
- Fixed an issue with relative links in the documentation.

### Version 1.02, released on 03/18/2020
- When installing a new version of this add-on, the settings from a previous installation are no longer lost.
- Other changes to conform to NVDA add-on standard compliance.

### Version 1.01, released on 03/12/2020
- The time and date are announced in the user's locale, meaning that 24-hour time is honored if set.
- NVDA will announce either the abbreviated or full timezone depending on the user's setting in the Timezone Ring dialog. For example, it will either say Europe/London, or it will say GMT or BST. This setting is controlled by checking or unchecking the "Announce abbreviated timezones" checkbox.
- Add-on includes translator comments (@ruifontes.)
- Add-on now includes header comments (@ruifontes.)
- The Escape key closes the Timezone Ring Dialog (@ruifontes.)
- The menu item to open the Timezone Ring dialog is now named appropriately (@ruifontes.)
- NVDA now defaults to the local timezone on installation of this add-on, if the local timezone is available.
- Support for multiple timezones through the use of a timezone ring.
- This add-on now uses the key NVDA+ALT+T to prevent conflict with the Clock add-on.
- The timezone selector dialog now has a filter box. NVDA will announce the number of results as the user starts typing into the filter field.
- Python 2 support
- The date and time is now announced in a separate thread to prevent hanging the NVDA thread in case retrieval takes a little while.
- The timezone selector dialog now has a cancel button and no longer prevents NVDA from shutting down.

[1]: https://github.com/munawarb/NVDA-Time-Zoner/releases/latest