'''
Created on May 12, 2019


'''

import logging

import xbmc
import xbmcaddon
import xbmcgui

import pyxbmct
import qhue


#import kodiHue
from language import get_string as _




ADDON = xbmcaddon.Addon()
logger = logging.getLogger(__name__)


class CreateSceneUI(pyxbmct.AddonDialogWindow):
    '''
    classdocs
    '''

    def __init__(self,bridge=qhue.Bridge):
        '''
        Constructor
        '''
        xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
        
        self.bridge=bridge
        self.hueLights=bridge.lights
        
        super(CreateSceneUI, self).__init__(_("Create Hue Scene"))
        
        self.setGeometry(600, 500, 10, 4)
        self.setControls()
        #self.populateLights()
        self.setNavigation()
        # self.set_info_controls()
        # self.set_active_controls()
        # self.set_navigation()
        # Connect a key action (Backspace) to close the window.
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
        self.doModal()
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')

    def setControls(self):
        
        self.textbox = pyxbmct.TextBox()
        self.placeControl(self.textbox, 0, 0, 2, 4)
        self.textbox.setText(_("Create a Hue Scene from current light state") + "\n" + 
                             _("Adjust lights to desired setting in the Hue App to create a new scene" + "\n" + 
                             _("Fade time must be saved as part of the scene.")  
                               ))
        
        #####################
        self.placeControl(pyxbmct.Label(_("Scene Name:")), 2, 0,)
        
        self.sceneName = pyxbmct.Edit(_('Scene Name'))
        self.placeControl(self.sceneName, 3, 0,columnspan=2)
        # Additional properties must be changed after (!) displaying a control.
        self.sceneName.setText(_("Enter Scene Name"))
        
        
        ############ Transition Time
        
        
        self.placeControl(pyxbmct.Label(_("Transition Time:")), 4, 0)        
        
        transitionTimeDefault = 10
        self.transitionTimeLabel = pyxbmct.Label(_("{} secs.").format(transitionTimeDefault))
        self.placeControl(self.transitionTimeLabel, 5, 0)
                #

        # Slider
        self.transitionTimeSlider = pyxbmct.Slider()
        self.placeControl(self.transitionTimeSlider, 5, 1)
        self.transitionTimeSlider.setPercent(transitionTimeDefault)
        # Connect key and mouse events for slider update feedback.
        self.connectEventList([pyxbmct.ACTION_MOVE_LEFT,
                               pyxbmct.ACTION_MOVE_RIGHT,
                               pyxbmct.ACTION_MOUSE_DRAG,
                               pyxbmct.ACTION_MOUSE_LEFT_CLICK],
                              self.sliderUpdate)
        
        
        
        #####
        #list_label = pyxbmct.Label(_("Lights:"))
        self.placeControl(pyxbmct.Label(_("Lights:")), 2, 2)
        #
        self.list_item_label = pyxbmct.Label('', textColor='0xFF808080')
        self.placeControl(self.list_item_label, 4, 2)
        # List
        self.listLights = pyxbmct.List()
        self.placeControl(self.listLights, 3, 2, rowspan=6, columnspan=2)
        # Add items to the list
        items = ['Item {0}'.format(i) for i in range(1, 15)]
        
        
        
        self.listLights.addItems(self.getLights())
        # Connect the list to a function to display which list item is selected.
        self.connect(self.listLights, lambda: xbmc.executebuiltin('Notification(Note!,{0} selected.)'.format(
            self.listLights.getListItem(self.listLights.getSelectedPosition()).getLabel())))
        # Connect key and mouse events for list navigation feedback.
        self.connectEventList(
            [pyxbmct.ACTION_MOVE_DOWN,
             pyxbmct.ACTION_MOVE_UP,
             pyxbmct.ACTION_MOUSE_WHEEL_DOWN,
             pyxbmct.ACTION_MOUSE_WHEEL_UP,
             pyxbmct.ACTION_MOUSE_MOVE],
            self.listUpdate)
        
        

        # Bottom Buttons
        
        self.buttonSave = pyxbmct.Button(_('Save'))
        self.placeControl(self.buttonSave, 9, 0)
        
        self.buttonClose = pyxbmct.Button(_('Cancel'))
        self.placeControl(self.buttonClose, 9, 3)
        # Connect control to close the window.
        self.connect(self.buttonClose, self.close)
        
    def setNavigation(self):
        # Set navigation between controls
        self.sceneName.controlDown(self.transitionTimeSlider)
        self.sceneName.controlRight(self.listLights)
        
        self.transitionTimeSlider.controlUp(self.sceneName)
        self.transitionTimeSlider.controlDown(self.buttonSave)
        
        self.buttonSave.controlUp(self.transitionTimeSlider)
        self.buttonSave.controlRight(self.buttonClose)
        
        self.buttonClose.controlLeft(self.buttonSave)

        # Set initial focus
        self.setFocus(self.sceneName)            


    def getLights(self):
        
        items=[]
        index=[]
        lights = {}
        listItems=[]
        hueLights = self.hueLights()
        
        for light in hueLights:
            hLight=hueLights[light]
            hLightName=hLight['name']
            
            #logger.debug("In selectHueGroup: {}, {}".format(hgroup,name))
            lights[light] = xbmcgui.ListItem(label=str(hLightName))
            listItems.append(xbmcgui.ListItem(label2=light,label=str(hLightName))  )
            #index.append(light)
            #items.append(xbmcgui.ListItem(label=hLightName))
        
        return listItems 
        
        
            
    def sliderUpdate(self):
        # Update slider value label when the slider nib moves
        try:
            if self.getFocus() == self.transitionTimeSlider:
                self.transitionTimeLabel.setLabel(_('{} secs.').format(int(self.transitionTimeSlider.getPercent())))
        except (RuntimeError, SystemError):
            pass

    def listUpdate(self):
        # Update list_item label when navigating through the list.
        try:
            if self.getFocus() == self.list:
                self.list_item_label.setLabel(self.list.getListItem(self.list.getSelectedPosition()).getLabel())
            else:
                self.list_item_label.setLabel('')
        except (RuntimeError, SystemError):
            pass        
                        
        
