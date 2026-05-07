# -*- coding: UTF-8 -*-
# timezone.py
#A part of NVDA timezone add-on
#Copyright (C) 2020 Munawar Bijani
#This file is covered by the GNU General Public License.
#See the file LICENSE.txt for more details.

import threading
import os.path
from os import remove
import sys
import globalPluginHandler
from scriptHandler import getLastScriptRepeatCount
from scriptHandler import script
import globalCommands
import winKernel
import ui
import core
import speech
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), "modules"))
import pytz
from pytz import timezone, common_timezones, country_names, country_timezones
from pytz.exceptions import UnknownTimeZoneError
from tzlocal import get_localzone
del sys.path[0]
import gui
import wx
from gui import settingsDialogs, guiHelper, NVDASettingsDialog
import json
from time import sleep
import addonHandler
import globalVars
from config import conf
addonHandler.initTranslation() 
timezoneToCountry = {}
configRoot = "TimeZoner"
# The schema for the NVDA configuration
conf.spec[configRoot] = {
	"announceAbbriv": "boolean(default=False)",
	"ptr": "integer(default=0)",
	"time": "boolean(default=True)",
	"date": "boolean(default=True)",
	"continent": "boolean(default=False)",
	"country": "boolean(default=False)",
	"city": "boolean(default=False)",
	"timezone": "integer(default=1)",
	"timezones": "string_list()"
}

def getFormattedTimeMessage(time=True, date=True, country=False, continent=False, city=False, timezone=1):
	# In the short message, the continent and city won't exist since we're looking at just a timezone such as UTC, EDT, etc.
	# In this case, we will also assume no country exists, since the timezone is generalized.
	components = []
	noContinentAndCityComponents = []
	if timezone == 0:
		components.append("{timezone}")
		noContinentAndCityComponents.append("{timezone}")
	if country:
		components.append("{country}" + (":" if continent or city else ""))
	if continent:
		components.append("{continent}" + ("/" if city else ""))
	if city:
		components.append("{city} ")
	if time:
		components.append("{time}" + ("," if date else ""))
		noContinentAndCityComponents.append("{time}" + ("," if date else ""))
	if date:
		components.append("{date}")
		noContinentAndCityComponents.append("{date}")
	if timezone == 1:
		components.append("({timezone})")
		noContinentAndCityComponents.append("({timezone})")
	return (" ".join(components), " ".join(noContinentAndCityComponents))
globalPluginClass = None

class SpeakThread(threading.Thread):
	def __init__(self, ptr, repeatCount, destTimezones, announceAbbriv, formatStringL, formatStringS):
		threading.Thread.__init__(self)
		self.ptr = ptr
		self.repeatCount = repeatCount
		self.interrupted = False
		self.destTimezones = destTimezones
		self.formatStringL = formatStringL
		self.formatStringS = formatStringS
		self.announceAbbriv = announceAbbriv

	def getTimezone(self):
		l = len(self.destTimezones)
		if l == 0:
			return ""
		return self.destTimezones[(self.repeatCount + self.ptr) % l]

	def sayInTimezone(self):
		selectedTz = self.getTimezone()
		if selectedTz == "":
			# For translators: message to inform there are no timezones defined
			core.callLater(0, ui.message, _("No timezones set"))
			return
		now = datetime.now(pytz.timezone("UTC"))
		destTimezone = now.astimezone(pytz.timezone(selectedTz))
		# By the time the code gets down here, we could have signaled this thread to terminate.
		# This will be the case if retrieval is taking a long time and we've pressed the key multiple times to get successive information in our timezone ring, in which case this thread is marked dirty.
		if self.interrupted:
			return
		# We'll use the winKernel here to announce the time and date in the user's locale.
		theTime =winKernel.GetTimeFormatEx(winKernel.LOCALE_NAME_USER_DEFAULT, winKernel.TIME_NOSECONDS, destTimezone, None)
		theDate = winKernel.GetDateFormatEx(winKernel.LOCALE_NAME_USER_DEFAULT, winKernel.DATE_LONGDATE, destTimezone, None)
		separator = selectedTz.find("/")
		country = timezoneToCountry.get(selectedTz, "Unknown country")
		timezone = destTimezone.strftime("%Z") if self.announceAbbriv else selectedTz
		continent = ""
		city = ""
		if separator != -1:
			continent = selectedTz[:separator]
			city = selectedTz[separator+1:]
			# For translators: message to announce the time, date and timezone
			core.callLater(0, ui.message, _(self.formatStringL.format(time=theTime, date=theDate, country=country, continent=continent, city=city, timezone=timezone)))
		else:
			# For translators: message to announce the time, date and timezone
			core.callLater(0, ui.message, _(self.formatStringS.format(time=theTime, date=theDate, timezone=timezone)))

	def run(self):
		self.sayInTimezone()

class TimezoneSelectorDialog(settingsDialogs.SettingsPanel):
	# For translators: Name of the Time Zoner settings category
	title = _("Time Zoner")
	def makeSettings(self, mainSizer):
		self.gPlugin = globalPluginClass
		sHelper = guiHelper.BoxSizerHelper(self, sizer=mainSizer)
		self.filterElement = sHelper.addLabeledControl(_("Filter:"), wx.TextCtrl)
		# The label and text box will be next to each other.
		# Below this we will find the label and listbox.
		listBoxesHelper = guiHelper.BoxSizerHelper(self, orientation=wx.HORIZONTAL)
		sHelper.addItem(listBoxesHelper)
		# For translators: Name of time zones list
		self.timezonesList = listBoxesHelper.addLabeledControl(_("Timezones (select to add, deselect to remove)"), wx.ListBox, choices=common_timezones, style=wx.LB_MULTIPLE)
		self.timezonesList.Bind(wx.EVT_LISTBOX, self.onTimezoneSelected)
		# For translators: Name of time zones ring list
		self.selectedTimezonesList = listBoxesHelper.addLabeledControl(_("Timezone Ring"), wx.ListBox, choices=[])
		self.selectedTimezonesList.AppendItems(self.gPlugin.destTimezones)
		self.setTimezonesListSelections()
		# The label and listbox will be below each other
		self.filterElement.Bind(wx.EVT_TEXT, self.onFilterTextChange)
		buttonsHelper = guiHelper.BoxSizerHelper(self, orientation=wx.HORIZONTAL)
		sHelper.addItem(buttonsHelper)
		# For translators: Name of the button to remove a time zone
		removeButton = buttonsHelper.addItem( wx.Button(self, label=_("Remove")))
		removeButton.Bind(wx.EVT_BUTTON, self.onRemoveClick)
		# For translators: Name of the button to move up a time zone
		moveUpButton = buttonsHelper.addItem( wx.Button(self, label=_("Move Up")))
		moveUpButton.Bind(wx.EVT_BUTTON, self.onMoveUp)
		# For translators: Name of the button to move down a time zone
		moveDownButton = buttonsHelper.addItem( wx.Button(self, label=_("Move Down")))
		moveDownButton.Bind(wx.EVT_BUTTON, self.onMoveDown)
		# For translators: The label for the checkbox to announce timezones in abbreviated form.
		self.announceAbbriv = sHelper.addItem(wx.CheckBox(self, label=_("Announce abbreviated timezones")))
		# Check the box by default if we're announcing abbreviations.
		self.announceAbbriv.SetValue(self.gPlugin.announceAbbriv)
		formattersBoxes = sHelper.addItem(wx.StaticBoxSizer(wx.VERTICAL, self, _("Components")))
		self.continentChk = wx.CheckBox(formattersBoxes.GetStaticBox(), label=_("Continent"))
		formattersBoxes.Add(self.continentChk)
		self.continentChk.SetValue(self.gPlugin.continent)
		self.countryChk = wx.CheckBox(formattersBoxes.GetStaticBox(), label=_("Country"))
		formattersBoxes.Add(self.countryChk)
		self.countryChk.SetValue(self.gPlugin.country)
		self.cityChk = wx.CheckBox(formattersBoxes.GetStaticBox(), label=_("City"))
		formattersBoxes.Add(self.cityChk)
		self.cityChk.SetValue(self.gPlugin.city)
		self.timeChk = wx.CheckBox(formattersBoxes.GetStaticBox(), label=_("Time"))
		formattersBoxes.Add(self.timeChk)
		self.timeChk.SetValue(self.gPlugin.time)
		self.dateChk = wx.CheckBox(formattersBoxes.GetStaticBox(), label=_("Date"))
		formattersBoxes.Add(self.dateChk)
		self.dateChk.SetValue(self.gPlugin.date)
		self.timezonePositionRadio = wx.RadioBox(formattersBoxes.GetStaticBox(), label=_("Announce Timezone At:"), choices=["Beginning", "End"])
		formattersBoxes.Add(self.timezonePositionRadio)
		self.timezonePositionRadio.SetSelection(self.gPlugin.timezone)

	def isMovable(self):
		index = self.selectedTimezonesList.GetSelection()
		numItems = self.selectedTimezonesList.GetCount()
		if index == wx.NOT_FOUND or numItems < 2:
			return False
		return True

	def onMoveUp(self, event):
		if not self.isMovable():
			return
		index = self.selectedTimezonesList.GetSelection()
		if index == 0:
			return
		tzToMove = self.selectedTimezonesList.GetString(index)
		self.selectedTimezonesList.InsertItems([tzToMove], index-1)
		self.selectedTimezonesList.Delete(index+1)

	def onMoveDown(self, event):
		if not self.isMovable():
			return
		index = self.selectedTimezonesList.GetSelection()
		numItems = self.selectedTimezonesList.GetCount()
		if index == numItems-1:
			return
		tzToMove = self.selectedTimezonesList.GetString(index)
		# We want to insert the item after the one below it, so we have to insert it before index+2
		self.selectedTimezonesList.InsertItems([tzToMove], index+2)
		self.selectedTimezonesList.Delete(index)

	def setTimezonesListSelections(self):
		# We use the selectedTimezonesList here because this is where the user will actively add and remove items.
		# The gPlugin.destTimezones list is only updated on save.
		for tz in self.selectedTimezonesList.GetItems():
			index = self.timezonesList.FindString(tz)
			if index != wx.NOT_FOUND:
				self.timezonesList.SetSelection(index)

	def onRemoveClick(self, event):
		if self.selectedTimezonesList.GetSelection() == wx.NOT_FOUND:
			return
		tzToRemove = self.selectedTimezonesList.GetString(self.selectedTimezonesList.GetSelection())
		self.selectedTimezonesList.Delete(self.selectedTimezonesList.GetSelection())
		indexToRemove = self.timezonesList.FindString(tzToRemove)
		if indexToRemove != wx.NOT_FOUND:
			self.timezonesList.Deselect(indexToRemove)

	def onTimezoneSelected(self, event):
		if event.IsSelection():
			if self.selectedTimezonesList.FindString(event.GetString()) == wx.NOT_FOUND:
				self.selectedTimezonesList.Append(event.GetString())
		else:
			if self.selectedTimezonesList.FindString(event.GetString()) != wx.NOT_FOUND:
				self.selectedTimezonesList.Delete(self.selectedTimezonesList.FindString(event.GetString()))

	# Used to speak the number of filtered results after a delay so that letting up on keys won't interrupt NVDA.
	def announceFilterAfterDelay(self, n):
		sleep(0.5)
		speech.cancelSpeech()
		# For translators: Message to announce the number of matches found
		core.callLater(0, ui.message, _("%d results now showing" % n))

	def onFilterTextChange(self, event):
		filterText = self.filterElement.GetValue()
		filtered = []
		if not filterText:
			filtered = common_timezones
		else:
			filterText = filterText.lower()
			filtered = [option for option in common_timezones if filterText in option.lower()]
		self.timezonesList.Set(filtered)
		if len(filtered) > 0:
			self.setTimezonesListSelections()
		# We'll delay the speaking of the filtered results so key presses don't interrupt it.
		t = threading.Thread(target=self.announceFilterAfterDelay, args=[len(filtered)])
		t.start()

	def onSave(self):
		self.gPlugin.destTimezones = self.selectedTimezonesList.GetItems()
		self.gPlugin.announceAbbriv = self.announceAbbriv.GetValue()
		self.gPlugin.continent = self.continentChk.GetValue()
		self.gPlugin.country = self.countryChk.GetValue()
		self.gPlugin.city = self.cityChk.GetValue()
		self.gPlugin.time = self.timeChk.GetValue()
		self.gPlugin.date = self.dateChk.GetValue()
		self.gPlugin.timezone = self.timezonePositionRadio.GetSelection()
		self.gPlugin.ptr = 0
		self.gPlugin.setFormatString()
		self.gPlugin.mapTZToCountry()
		self.gPlugin.save()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	# For translators: The name of the category under which to display hotkeys for this add-on in Input Gestures.
	scriptCategory = _("Time Zoner")
	def __init__(self):
		global globalPluginClass
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		if globalVars.appArgs.secure: # Don't allow to run on UAC screens.
			return
		globalPluginClass = self
		NVDASettingsDialog.categoryClasses.append(TimezoneSelectorDialog)
		try:
			self.destTimezones = [get_localzone().zone]
		except UnknownTimeZoneError:
			# We couldn't find the user's default timezone.
			self.destTimezones = []
		self.announceAbbriv = False
		self.ptr = 0
		self.time=True
		self.date=True
		self.country=False
		self.continent=False
		self.city=False
		self.timezone=1
		self.formatStringL, self.formatStringS = getFormattedTimeMessage(time=self.time, date=self.date, timezone=self.timezone) # Default configuration of time, date, timezone
		# For versions of add-ons upgrading to the NVDA  config version, we'll import the JSON file and then delete it.
		# The JSON file was used to store config options before the rewrite to use the NVDA config API and is no longer needed. But we don't want the user to lose their settings because of the upgrade.
		scriptPath = os.path.realpath(__file__)
		# Place the config file in the aplication that the add-on is in.
		configFile = os.path.join(scriptPath[:scriptPath.rindex("\\")], "timezone.json")
		if os.path.isfile(configFile):
			with open(configFile) as fin:
				data = json.load(fin)
				for confKey in data:
					conf[configRoot][confKey] = data.get(confKey, "")
			# Since we're importig settings, let's save the NVDA config before we delete the legacy data.json file.
			# Otherwise, the settings will be lost if NVDA exits without the config being saved.
			conf.save()
			remove(configFile)
		tzSettings = conf[configRoot]
		self.destTimezones = tzSettings.get("timezones", self.destTimezones)
		self.announceAbbriv = tzSettings.get("announceAbbriv", self.announceAbbriv)
		self.ptr = tzSettings.get("ptr", self.ptr)
		self.time = tzSettings.get("time", self.time)
		self.date = tzSettings.get("date", self.date)
		self.country = tzSettings.get("country", self.country)
		self.continent = tzSettings.get("continent", self.continent)
		self.city = tzSettings.get("city", self.city)
		self.timezone = tzSettings.get("timezone", self.timezone)
		self.formatStringL, self.formatStringS = getFormattedTimeMessage(time=self.time, date=self.date, country=self.country, continent=self.continent, city=self.city, timezone=self.timezone)
		# We'll try to set the local timezone as the default, but if it doesn't exist we'll just create an empty timezone list.
		# If we couldn't determine the user's default timezone, the destTimezones array will be empty.
		# This is to rescue the script from systems that might not have a recognizable timezone.
		if len(self.destTimezones) > 0 and self.destTimezones[0] not in common_timezones:
			self.destTimezones = []
		self.lastSpeechThread = None
		self.mapTZToCountry()

	def terminate(self):
		try:
			NVDASettingsDialog.categoryClasses.remove(TimezoneSelectorDialog)
		except ValueError as e:
			pass

	# Builds an inverse mapping of timezone to countries.
	# for the timezones the user has selected.
	def mapTZToCountry(self):
		global timezoneToCountry
		timezoneToCountry.clear() # So we don't leak memory: in case the user adds and removes a lot of timezones, we don't want unused timezones being left over.
		for countryCode in country_timezones:
			timezonesInCountry = filter(lambda tz: tz in self.destTimezones, country_timezones[countryCode])
			for tz in timezonesInCountry:
				timezoneToCountry[tz] = country_names[countryCode]

	def setFormatString(self):
		self.formatStringL, self.formatStringS = getFormattedTimeMessage(continent=self.continent, country=self.country, city=self.city, time=self.time, date=self.date, timezone=self.timezone)

	def save(self):
		conf[configRoot] = {"announceAbbriv": self.announceAbbriv, "timezones": self.destTimezones, "ptr": self.ptr, "continent": self.continent, "country": self.country, "city": self.city, "time": self.time, "date": self.date, "timezone": self.timezone}

	def stopLastSpeakThread(self):
		if self.lastSpeechThread is not None:
			self.lastSpeechThread.interrupted = True

	@script(
		description = _("Speaks the time and date in the specified timezone in the configured timezone ring according to the amount of times this key is pressed in rapid succession."),
		gestures=["kb:NVDA+ALT+T"]
	)
	def script_sayTimezoneTime(self, gesture):
		if globalVars.appArgs.secure: # Don't allow to run on UAC screens.
			return
		# We'll spawn a new thread here since the first retrieval of the timezone data has a slight delay and it will freeze NVDA for a second or two.
		# First, signal the last thread to die if it's taking too long and we've pressed this key multiple times.
		self.stopLastSpeakThread()
		self.lastSpeechThread = SpeakThread(self.ptr, getLastScriptRepeatCount(), self.destTimezones, self.announceAbbriv, self.formatStringL, self.formatStringS)
		self.lastSpeechThread.start()

	@script(
		description = _("Moves to and speaks the previous timezone in the timezone ring."),
		gestures=["kb:NVDA+ALT+UPARROW"]
	)
	def script_sayPreviousTimezone(self, gesture):
		if globalVars.appArgs.secure: # Don't allow to run on UAC screens.
			return
		# We'll spawn a new thread here since the first retrieval of the timezone data has a slight delay and it will freeze NVDA for a second or two.
		# First, signal the last thread to die if it's taking too long and we've pressed this key multiple times.
		self.stopLastSpeakThread()
		self.ptr -= 1
		# If the pointer has gone negative, reset it to the highest timezone value
		highestIndex = max(0, len(self.destTimezones) - 1)
		if self.ptr < 0:
			self.ptr = highestIndex
		self.lastSpeechThread = SpeakThread(self.ptr, 0, self.destTimezones, self.announceAbbriv, self.formatStringL, self.formatStringS)
		self.lastSpeechThread.start()
		self.save()

	@script(
		description = _("Moves to and speaks the next timezone in the timezone ring."),
		gestures=["kb:NVDA+ALT+DOWNARROW"]
	)
	def script_sayNextTimezone(self, gesture):
		if globalVars.appArgs.secure: # Don't allow to run on UAC screens.
			return
		# We'll spawn a new thread here since the first retrieval of the timezone data has a slight delay and it will freeze NVDA for a second or two.
		# First, signal the last thread to die if it's taking too long and we've pressed this key multiple times.
		self.stopLastSpeakThread()
		l = len(self.destTimezones)
		if l > 0:
			self.ptr = (self.ptr+1) % l
		else:
			self.ptr = 0
		self.lastSpeechThread = SpeakThread(self.ptr, 0, self.destTimezones, self.announceAbbriv, self.formatStringL, self.formatStringS)
		self.lastSpeechThread.start()
		self.save()