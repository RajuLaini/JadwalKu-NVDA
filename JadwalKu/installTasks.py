# -*- coding: UTF-8 -*-

import addonHandler

addonHandler.initTranslation()

def onInstall():
	for addon in addonHandler.getAvailableAddons():
		if addon.manifest['name'] == "JadwalKu":
			addon.requestRemove()
