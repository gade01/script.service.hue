# -*- coding: utf-8 -*-

import os
import sys
import time
import logging

import json


from threading import Event

from  resources.lib.qhue import Bridge

from resources.lib import kodiutils
from resources.lib import kodilogging
from resources.lib import settings



###TODO Ewwwww....
from resources.lib.newDefault import MyMonitor
from resources.lib.newDefault import MyPlayer
from resources.lib.newDefault import Hue

from resources.lib import kodiHue                                                                                                                                                          



import xbmc
import xbmcaddon
from xbmcgui import NOTIFICATION_ERROR,NOTIFICATION_WARNING, NOTIFICATION_INFO 

from resources.lib.kodiutils import notification


__addon__ = xbmcaddon.Addon()
__addondir__ = xbmc.translatePath(__addon__.getAddonInfo('profile'))
__cwd__ = __addon__.getAddonInfo('path')

from resources.lib import algorithm
from resources.lib.ambilight_controller import AmbilightController
from resources.lib import bridge
from resources.lib import image
from resources.lib import ui

from resources.lib.settings import Settings
from resources.lib.static_controller import StaticController
from resources.lib.theater_controller import TheaterController
from resources.lib.tools import get_version
from resources.lib import kodilogging

from resources.lib import kodiutils

ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

REMOTE_DBG = True

logger.debug("Kodi Hue: In .(argv={}) service started, version: {}, SYSPATH: {}".format(
    sys.argv, get_version(), sys.path))

ev = Event()
capture = xbmc.RenderCapture()
fmt = capture.getImageFormat()
# BGRA or RGBA
fmtRGBA = fmt == 'RGBA'



##################################################
## RUN
###################
def run():
    logger.debug("Kodi Hue: In .(argv={}) service started, version: {}".format(
        sys.argv, get_version()))

    args = None
    if len(sys.argv) == 2:
        args = sys.argv[1]


    
    ev = Event()
    capture = xbmc.RenderCapture()
    fmt = capture.getImageFormat()
    # BGRA or RGBA
    fmtRGBA = fmt == 'RGBA'

    
    
    
    
    ### CIRCULAR MESS
    settings = Settings()
    
    monitor = MyMonitor(settings)
    mon=xbmc.Monitor()
    hue = Hue(settings, args) #crashing here if bridge ip isnt blank.. beurk
    
    player = MyPlayer()
    
    
    bridgeIP = kodiutils.get_setting("bridgeIp")
    bridgeUser = kodiutils.get_setting("bridgeUser")
    
    
    if not bridgeIP or not bridgeUser:
        logger.debug("Kodi Hue: Hue setup incomplete, starting setup. Bridge IP: {},Bridge User: {}".format(bridgeIP,bridgeUser))
        notification("Kodi Hue", "Bridge not configured. Starting setup", time=5000, icon=NOTIFICATION_WARNING, sound=True)
        kodiHue.setup(mon,True) #Start setup with notifications
        bridgeIP = kodiutils.get_setting("bridgeIp")
        bridgeUser = kodiutils.get_setting("bridgeUser")
        
        
    if not bridgeIP or not bridgeUser:
        
#        notification("Kodi Hue", "Bridge not configured. Starting setup", time=5000, icon=NOTIFICATION_WARNING, sound=True)
        logger.debug("Kodi Hue: Hue initial setup failed, exiting script")
        sys.exit()
        
    
        
    bridge = Bridge(bridgeIP, bridgeUser)
    bridgeAPIVersion = bridge.config()['apiversion']
    if bridgeAPIVersion:
        logger.debug("Kodi Hue: Connection test success. Bridge API Version:".format(bridgeAPIVersion))
    else:
        notification("Kodi Hue", "Bridge connection error. Check settings", time=5000, icon=NOTIFICATION_ERROR, sound=True)
        logger.debug("Kodi Hue: Connection error - could not find Hue API version. Stopping script.")
        sys.exit()
        

    logger.debug("Kodi Hue: Bridge setup. IP: " + str(bridgeIP) + " User: " + str(bridgeUser))
        
   
    
    # create a lights resource
    lights = bridge.lights
    
#    initialLights = lights()

   
    # query the API and print the results
#    logger.debug("Kodi Hue: Qhue.Bridge" + str(bridge()))
    logger.debug("Kodi Hue: Initial test flash")
    bridge.lights[5].state(bri=128, xy=[0.180,0.239],on=True, alert="select")
    
    
#    bridge.lights.state(initialLights)
    
    
    
    
    
    
    sys.exit()
    
#    print(lights())



    logger.debug("Kodi Hue: In run() Hue connected: " + str(hue.connected))
    if not hue.connected:
        notification("Kodi Hue", "Kodi Hue: Bridge not connected. Go to Kodi Hue settings to configure your hue Bridge", time=5000, icon=ADDON.getAddonInfo('icon'), sound=True)
        ##TODO localized string
        ##Connected & configured might not be the same thing...
#    else:
        ##TODO Flash lights!

        
        
    
#    while not hue.connected and not monitor.abortRequested():
#        xbmc.sleep(500)

    if player is None:
        logger.debug('Kodi Hue: In run() could not instantiate player')
        return

    while not monitor.abortRequested() and not hue.connected():
        
        
        if len(hue.ambilight_controller.lights) and not ev.is_set():
            startReadOut = False
            vals = {}
            if player.playingvideo:  # only if there's actually video
                try:
                    vals = capture.getImage(200)
                    if len(vals) > 0 and player.playingvideo:
                        startReadOut = True
                    if startReadOut:
                        screen = image.Screenshot(
                            capture.getImage())
                        hsv_ratios = screen.spectrum_hsv(
                            screen.pixels,
                            hue.settings.ambilight_threshold_value,
                            hue.settings.ambilight_threshold_saturation,
                            hue.settings.color_bias,
                            len(hue.ambilight_controller.lights)
                        )
                        for i in range(len(hue.ambilight_controller.lights)):
                            algorithm.transition_colorspace(
                                hue, hue.ambilight_controller.lights.values()[i], hsv_ratios[i], )
                except ZeroDivisionError:
                    pass

        if monitor.waitForAbort(10):
            logger.debug('Kodi Hue: In run() shutting down')
#            del player  # might help with slow exit.
            break





