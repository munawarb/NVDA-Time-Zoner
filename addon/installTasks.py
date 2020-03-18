import os
import globalVars
import addonHandler
def onInstall():
	configFilePath = os.path.abspath(os.path.join(globalVars.appArgs.configPath, "addons", "timezone", "globalPlugins", "timezone.json"))
	if os.path.isfile(configFilePath):	
		os.rename(configFilePath, os.path.abspath(os.path.join(globalVars.appArgs.configPath, "addons", "timezone" + addonHandler.ADDON_PENDINGINSTALL_SUFFIX, "globalPlugins", "timezone.json")))