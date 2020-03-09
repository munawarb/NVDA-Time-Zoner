import threading
import os.path
import sys
import globalPluginHandler
from scriptHandler import getLastScriptRepeatCount
from scriptHandler import script
import globalCommands
from globalCommands import GlobalCommands as Scripts
import ui
from datetime import datetime
pythonVersion = int(sys.version[:1])
# Here, we use the Python2 or 3 versions of pytz
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), "modules", "2" if pythonVersion == 2 else "3"))
from pytz import timezone, common_timezones
del sys.path[0]
import gui
import wx
from gui import SettingsDialog, guiHelper
import json
from time import sleep

class TimezoneSelectorDialog(wx.Dialog):
	def __init__(self, parent, globalPluginClass):
		super(wx.Dialog, self).__init__(parent, title="Select A Timezone")
		self.gPlugin = globalPluginClass
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		self.filterElement = sHelper.addLabeledControl("Filter:", wx.TextCtrl)
		# The label and text box will be next to each other.
		# Below this we will find the label and listbox.
		self.timezonesList = sHelper.addLabeledControl("Choose option", wx.ListBox, choices=common_timezones)
		# The label and listbox will be below each other
		self.filterElement.Bind(wx.EVT_TEXT, self.onFilterTextChange)
		self.timezonesList.SetSelection(self.timezonesList.FindString(self.gPlugin.destTimezone))
		button = sHelper.addItem( wx.Button(self, label="Set Timezone"))
		button.Bind(wx.EVT_BUTTON, self.onSetTZClick)
		cancelButton = sHelper.addItem( wx.Button(self, label="Cancel"))
		cancelButton.Bind(wx.EVT_BUTTON, self.onCancelClick)
		# TODO: Right now, the buttons are stacked. We should put them next to each other.

# Used to speak the number of filtered results after a delay so that letting up on keys won't interrupt NVDA.
	def announceFilterAfterDelay(self, n):
		sleep(0.5)
		ui.message("%d results now showing" % n)

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
			self.timezonesList.SetSelection(0)
		# We'll delay the speaking of the filtered results so key presses don't interrupt it.
		t = threading.Thread(target=self.announceFilterAfterDelay, args=[len(filtered)])
		t.start()

	def onSetTZClick(self, event):
		self.gPlugin.destTimezone = self.timezonesList.GetString(self.timezonesList.GetSelection())
		with open(self.gPlugin.configFile, "w") as fout:
			fout.write(json.dumps({"timezones": [self.gPlugin.destTimezone]}))
		self.Destroy()

	def onCancelClick(self, event):
		self.Destroy()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		scriptPath = os.path.realpath(__file__)
		# Place the config file in the aplication that the add-on is in.
		self.configFile = os.path.join(scriptPath[:scriptPath.rindex("\\")], "timezone.json")
		if os.path.isfile(self.configFile):
			with open(self.configFile) as fin:
				data = json.load(fin)
				self.destTimezone = data["timezones"][0]
		else:
			self.destTimezone = common_timezones[0]
		self.menu = gui.mainFrame.sysTrayIcon.menu.GetMenuItems()[0].GetSubMenu()
		self.optionsMenu = wx.Menu()
		self.topLevel = self.menu.AppendSubMenu(self.optionsMenu, "Configure Timezones", "")
		self.setTZOption = self.optionsMenu.Append(wx.ID_ANY, "Set Timezone...", "Presents a list of timezones")
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.showTimezoneDialog, self.setTZOption)

	@script(
		description=_("If pressed once, speaks the time in the selected timezone. If pressed twice, speaks the date in the selected timezone."),
		category=globalCommands.SCRCAT_SYSTEM, # Same category as the NVDA speakDateTime script
		gestures=["kb:NVDA+ALT+T"]
	)
	def script_sayTimezoneTime(self, gesture):
		# For the first two key-presses, we'll fall through to NVDA's default behavior
		if getLastScriptRepeatCount()<2:
			Scripts.script_dateTime(globalCommands.commands, gesture)
			return
		# We'll spawn a new thread here since the first retrieval of the timezone data has a slight delay and it will freeze NVDA for a second or two.
		t = threading.Thread(target=self.sayInTimezone, args=[getLastScriptRepeatCount()])
		t.start()

	def sayInTimezone(self, repeatCount):
		dateFormat = "%A, %B %#d, %Y"
		timeFormat = "%#I:%M %p %Z"
		now = datetime.now(timezone('UTC'))		
		destTimezone = now.astimezone(timezone(self.destTimezone))
		if repeatCount==2:
			ui.message(destTimezone.strftime(timeFormat))
		elif repeatCount==3:
			ui.message(destTimezone.strftime(dateFormat))

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