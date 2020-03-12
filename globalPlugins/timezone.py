# -*- coding: UTF-8 -*-
# timezone.py
#A part of NVDAtimezone add-on
#Copyright (C) 2020 Munawar Bijani
#This file is covered by the GNU General Public License.
#See the file LICENSE.txt for more details.

import threading
import os.path
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
pythonVersion = int(sys.version[:1])
# Here, we use the Python2 or 3 versions of pytz
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), "modules", "2" if pythonVersion == 2 else "3"))
from pytz import timezone, common_timezones
from tzlocal import get_localzone
del sys.path[0]
import gui
import wx
from gui import SettingsDialog, guiHelper
import json
from time import sleep
import addonHandler

addonHandler.initTranslation() 

class SpeakThread(threading.Thread):
	def __init__(self, repeatCount, destTimezones, announceAbbriv):
		threading.Thread.__init__(self)
		self.repeatCount = repeatCount
		self.interrupted = False
		self.destTimezones = destTimezones
		self.announceAbbriv = announceAbbriv

	def getTimezone(self):
		l = len(self.destTimezones)
		if l == 0:
			return ""
		return self.destTimezones[self.repeatCount%l]

	def sayInTimezone(self):
		selectedTz = self.getTimezone()
		if selectedTz == "":
			# For translators: message to inform there are no timezones defined
			core.callLater(0, ui.message, _("No timezones set"))
			return
		now = datetime.now(timezone("UTC"))
		destTimezone = now.astimezone(timezone(selectedTz))
		# By the time the code gets down here, we could have signaled this thread to terminate.
		# This will be the case if retrieval is taking a long time and we've pressed the key multiple times to get successive information in our timezone ring, in which case this thread is marked dirty.
		if self.interrupted:
			return
		# We'll use the winKernel here to announce the time and date in the user's locale.
		theTime =winKernel.GetTimeFormatEx(winKernel.LOCALE_NAME_USER_DEFAULT, winKernel.TIME_NOSECONDS, destTimezone, None)
		theDate = winKernel.GetDateFormatEx(winKernel.LOCALE_NAME_USER_DEFAULT, winKernel.DATE_LONGDATE, destTimezone, None)
		# For translators: message to announce the time, date and timezone
		core.callLater(0, ui.message, _("%s, %s (%s)" % (theTime, theDate, destTimezone.strftime("%Z") if self.announceAbbriv else selectedTz)))

	def run(self):
		self.sayInTimezone()

class TimezoneSelectorDialog(wx.Dialog):
	def __init__(self, parent, globalPluginClass):
		super(wx.Dialog, self).__init__(parent, title = _("Configure Timezone Ring"))
		self.gPlugin = globalPluginClass
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
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
		saveAndCancelHelper = guiHelper.BoxSizerHelper(self, orientation=wx.HORIZONTAL)
		sHelper.addItem(saveAndCancelHelper)
		# For translators: Name of the button to save the selections of time zones
		setButton = saveAndCancelHelper.addItem( wx.Button(self, label=_("Save")))
		setButton.Bind(wx.EVT_BUTTON, self.onSetTZClick)
		# For translators: Name of the button to exit without saving the selections of time zones
		cancelButton = saveAndCancelHelper.addDialogDismissButtons( wx.Button(self, id = wx.ID_CLOSE, label=_("Cancel")))
		cancelButton.Bind(wx.EVT_BUTTON, self.onCancelClick)
		self.SetEscapeId(wx.ID_CLOSE)

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

	def onSetTZClick(self, event):
		zones = self.selectedTimezonesList.GetItems()
		self.gPlugin.destTimezones = zones
		self.gPlugin.announceAbbriv = self.announceAbbriv.GetValue()
		with open(self.gPlugin.configFile, "w") as fout:
			fout.write(json.dumps({"announceAbbriv": self.gPlugin.announceAbbriv, "timezones": zones}))
		self.Destroy()

	def onCancelClick(self, event):
		self.Destroy()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		self.destTimezones = [get_localzone().zone]
		self.announceAbbriv = False
		scriptPath = os.path.realpath(__file__)
		# Place the config file in the aplication that the add-on is in.
		self.configFile = os.path.join(scriptPath[:scriptPath.rindex("\\")], "timezone.json")
		if os.path.isfile(self.configFile):
			with open(self.configFile) as fin:
				data = json.load(fin)
				self.destTimezones = data.get("timezones", self.destTimezones)
				self.announceAbbriv = data.get("announceAbbriv", self.announceAbbriv)
		else:
			# We'll try to set the local timezone as the default, but if it doesn't exist we'll just create an empty timezone list.
			# This is to rescue the script from systems that might not have a recognizable timezone.
			if self.destTimezones[0] not in common_timezones:
				self.destTimezones = []

		# Construction of the add-on menu
		self.menu = gui.mainFrame.sysTrayIcon.menu.GetMenuItems()[0].GetSubMenu()
		self.optionsMenu = wx.Menu()
		# For translators: Name of the menu of the add-on
		self.topLevel = self.menu.AppendSubMenu(self.optionsMenu, _("Time Zoner"), "")
		# For translators: Name of the sub-menu of the add-on
		self.setTZOption = self.optionsMenu.Append(wx.ID_ANY, _("Configure Timezone Ring..."), _("Allows the configuration of timezones"))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.showTimezoneDialog, self.setTZOption)

		self.lastSpeechThread = None

	@script(
		description = _("Speaks the time and date in the specified timezone in the configured timezone ring according to the amount of times this key is pressed in rapid succession."),
		category=globalCommands.SCRCAT_SYSTEM, # Same category as the NVDA speakDateTime script
		gestures=["kb:NVDA+ALT+T"]
	)
	def script_sayTimezoneTime(self, gesture):
		# We'll spawn a new thread here since the first retrieval of the timezone data has a slight delay and it will freeze NVDA for a second or two.
		# First, signal the last thread to die if it's taking too long and we've pressed this key multiple times.
		if self.lastSpeechThread is not None:
			self.lastSpeechThread.interrupted = True
		self.lastSpeechThread = SpeakThread(getLastScriptRepeatCount(), self.destTimezones, self.announceAbbriv)
		self.lastSpeechThread.start()

	@script(
		description=_("Brings up the timezone selection dialog."),
		gestures=None
	)
	def script_showTimezoneSelector(self, gesture):
		self.showTimezoneDialog(None)

	def showTimezoneDialog(self, event):
		def createTimezoneDialog():
			dlg= TimezoneSelectorDialog(gui.mainFrame, self)
			dlg.filterElement.SetFocus()
			dlg.Layout()
			dlg.Center(wx.BOTH|wx.Center)
			dlg.Show()
		wx.CallAfter(createTimezoneDialog) # The dialog must be created on the main thread.
