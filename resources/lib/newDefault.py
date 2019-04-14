'''
Created on Apr. 8, 2019

@author: Kris
'''
import os
import sys
import logging
import time
from threading import Event


import xbmc
import xbmcaddon


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





class Hue:
    theater_controller = None
    ambilight_controller = None
    static_controller = None

    def __init__(self, settings, args):
        self.settings = settings
        self.connected = False

        try:
            params = dict(arg.split("=") for arg in args.split("&"))
        except Exception:
            params = {}

        if params == {}:
            # if there's a bridge IP, try to talk to it.
            if self.settings.bridge_ip not in ["-", "", None]:
                result = bridge.user_exists(
                    self.settings.bridge_ip,
                    self.settings.bridge_user
                )
                if result:
                    self.connected = True
                    self.update_controllers()
        elif params['action'] == "discover":
            ui.discover_hue_bridge(self)
            self.update_controllers()
        elif params['action'] == "reset_settings":
            os.unlink(os.path.join(__addondir__, "settings.xml"))
        elif params['action'] == "setup_theater_lights":
            xbmc.executebuiltin('NotifyAll({}, {})'.format(
                ADDON.getAddonInfo('id'), 'start_setup_theater_lights'))
        elif params['action'] == "setup_theater_subgroup":
            xbmc.executebuiltin('NotifyAll({}, {})'.format(
                ADDON.getAddonInfo('id'), 'start_setup_theater_subgroup'))
        elif params['action'] == "setup_ambilight_lights":
            xbmc.executebuiltin('NotifyAll({}, {})'.format(
                ADDON.getAddonInfo('id'), 'start_setup_ambilight_lights'))
        elif params['action'] == "setup_static_lights":
            xbmc.executebuiltin('NotifyAll({}, {})'.format(
                ADDON.getAddonInfo('id'), 'start_setup_static_lights'))
        else:
            # not yet implemented
            pass

        if self.connected:
            if self.settings.misc_initialflash:
                self.ambilight_controller.flash_lights()
                self.theater_controller.flash_lights()
                self.static_controller.flash_lights()

    def update_controllers(self):
        self.ambilight_controller = AmbilightController(
            bridge.get_lights_by_ids(
                self.settings.bridge_ip,
                self.settings.bridge_user,
                self.settings.ambilight_group.split(',')),
            self.settings
        )

        self.theater_controller = TheaterController(
            bridge.get_lights_by_ids(
                self.settings.bridge_ip,
                self.settings.bridge_user,
                self.settings.theater_group.split(',')),
            self.settings
        )

        self.static_controller = StaticController(
            bridge.get_lights_by_ids(
                self.settings.bridge_ip,
                self.settings.bridge_user,
                self.settings.static_group.split(',')),
            self.settings
        )

        logger.debug(
            'Kodi Hue: In Hue.update_controllers() instantiated following '
            'controllers {} {} {}'.format(
                self.theater_controller,
                self.ambilight_controller,
                self.static_controller,
            )
        )






class MyMonitor(xbmc.Monitor):

    def __init__(self, settings):
        xbmc.Monitor.__init__(self)
        self.settings = settings
        

#    def onSettingsChanged(self):
#        hue.settings.readxml()
#        logger.debug('Kodi Hue: In onSettingsChanged() {}'.format(hue.settings))
#        hue.update_controllers()

    def onNotification(self, sender, method, data):
        logger.debug('Kodi Hue: In onNotification(sender={}, method={}, data={})'
                .format(sender, method, data))
        if sender == ADDON.getAddonInfo('id'):
            if method == 'Other.start_setup_theater_lights':
                ret = ui.multiselect_lights(
                    self.settings.bridge_ip,
                    self.settings.bridge_user,
                    'Select Theater Lights',
                    ','.join([self.settings.ambilight_group,
                              self.settings.static_group]),
                    self.settings.theater_group
                )
                self.settings.update(theater_group=ret)
                hue.update_controllers()
            if method == 'Other.start_setup_theater_subgroup':
                ret = ui.multiselect_lights(
                    self.settings.bridge_ip,
                    self.settings.bridge_user,
                    'Select Theater Subgroup',
                    ','.join([self.settings.ambilight_group,
                              self.settings.static_group]),
                    self.settings.theater_subgroup
                )
                self.settings.update(theater_subgroup=ret)
                hue.update_controllers()
            if method == 'Other.start_setup_ambilight_lights':
                ret = ui.multiselect_lights(
                    self.settings.bridge_ip,
                    self.settings.bridge_user,
                    'Select Ambilight Lights',
                    ','.join([self.settings.theater_group,
                              self.settings.static_group]),
                    self.settings.ambilight_group
                )
                self.settings.update(ambilight_group=ret)
                hue.update_controllers()
            if method == 'Other.start_setup_static_lights':
                ret = ui.multiselect_lights(
                    self.settings.bridge_ip,
                    self.settings.bridge_user,
                    'Select Static Lights',
                    ','.join([self.settings.theater_group,
                              self.settings.ambilight_group]),
                    self.settings.static_group
                )
                self.settings.update(static_group=ret)
                hue.update_controllers()


class MyPlayer(xbmc.Player):
    duration = 0
    playingvideo = False
    playlistlen = 0
    movie = False

    def __init__(self):
        logger.debug('Kodi Hue: In MyPlayer.__init__()')
        xbmc.Player.__init__(self)

    def onPlayBackStarted(self):
        logger.debug('Kodi Hue: In MyPlayer.onPlayBackStarted()')
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        self.playlistlen = playlist.size()
        self.playlistpos = playlist.getposition()
        self.playingvideo = True
        self.duration = self.getTotalTime()
        state_changed("started", self.duration)

    def onPlayBackPaused(self):
        logger.debug('Kodi Hue: In MyPlayer.onPlayBackPaused()')
        state_changed("paused", self.duration)
        if self.isPlayingVideo():
            self.playingvideo = False

    def onPlayBackResumed(self):
        logger.debug('Kodi Hue: In MyPlayer.onPlayBackResume()')
        state_changed("resumed", self.duration)
        if self.isPlayingVideo():
            self.playingvideo = True
            if self.duration == 0:
                self.duration = self.getTotalTime()

    def onPlayBackStopped(self):
        logger.debug('Kodi Hue: In MyPlayer.onPlayBackStopped()')
        state_changed("stopped", self.duration)
        self.playingvideo = False
        self.playlistlen = 0

    def onPlayBackEnded(self):
        logger.debug('Kodi Hue: In MyPlayer.onPlayBackEnded()')
        # If there are upcoming plays, ignore
        if self.playlistpos < self.playlistlen-1:
            return

        self.playingvideo = False
        state_changed("stopped", self.duration)


def state_changed(state, duration):
    logger.debug('Kodi Hue: In state_changed(state={}, duration={})'.format(
        state, duration))

    if (xbmc.getCondVisibility('Window.IsActive(screensaver-atv4.xml)') or
            xbmc.getCondVisibility('Window.IsActive(screensaver-video-main.xml)')):
        return

    if duration < hue.settings.misc_disableshort_threshold and hue.settings.misc_disableshort:
        return

    if state == "started":
        # start capture when playback starts
        capture_width = 32  # 100
        capture_height = capture_width / capture.getAspectRatio()
        if capture_height == 0:
            capture_height = capture_width  # fix for divide by zero.
        capture.capture(int(capture_width), int(capture_height))

    if state == "started" or state == "resumed":
        ev.set()
        hue.theater_controller.on_playback_start()
        hue.ambilight_controller.on_playback_start()
        hue.static_controller.on_playback_start()
        ev.clear()

    elif state == "paused":
        ev.set()
        hue.theater_controller.on_playback_pause()
        hue.ambilight_controller.on_playback_pause()
        hue.static_controller.on_playback_pause()

    elif state == "stopped":
        ev.set()
        hue.theater_controller.on_playback_stop()
        hue.ambilight_controller.on_playback_stop()
        hue.static_controller.on_playback_stop()

