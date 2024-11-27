import json
import win32api
try:
    from srcOverlay.Observer import Observer
except:
    from Observer import Observer
import win32gui
import time
import win32con
from pynput import keyboard as kb
import logging

from pynput import mouse as ppmouse


import pydirectinput


class DofusManager(Observer):
    def __init__(self, config, dofus_handler):
        Observer.__init__(self,["stop","switch_page", "reorganise"])  
        self.config=config
        self.mode = "combat"
        self.dofus_handler = dofus_handler
        self.running = True
        self.current=0
        
        self.keyboard_thread = kb.Listener(on_press=self.on_press, on_release=self.on_release)
        self.keyboard_thread.start()
        
        
        self.mouse = ppmouse.Controller()
        self.listener = ppmouse.Listener(
            on_click=self.on_click)
        self.listener.start()
        
    def on_press(self,key):
        try:
            if '_name_' not in key.__dict__:
                return
            if key.name == self.config["keyboard_bindings"]['prev_win']:
                self.current=1
            if key.name == self.config["keyboard_bindings"]['stop']:
                self.ask_stop()
            
        except:
            logging.error('erreur on press dofusManager')
            
    def on_release(self,key):
        if '_name_' in key.__dict__ :
            if key.name == self.config["keyboard_bindings"]['prev_win']:
                self.current=0
            elif key.name == self.config["keyboard_bindings"]['stop']:
                self.ask_stop()
                return False
            elif key.name == self.config["keyboard_bindings"]['next_win'] and self.current==0:
                self._switch_next_win()
            elif key.name == self.config["keyboard_bindings"]['next_win'] and self.current==1:
                self._switch_previous_win()
            elif key.name == self.config["keyboard_bindings"]['next_turn']:
                self.next_turn()
            elif key.name == self.config["keyboard_bindings"]['focus_dofus']:
                self._open_current()
            elif key.name == self.config["keyboard_bindings"]['reorganizer']:
                self.dofus_handler.open_reorganize()
            elif key.name == self.config["keyboard_bindings"]['actualise']:
                self.dofus_handler.actualise()
        return self.running

    def on_click(self, x,y,button, pressed):
        if(self.allow_event() and ( button.name=="x2" or button.name=="x1" ) and pressed==False):
            self.mouse.click(ppmouse.Button.left, 1)
            self._switch_next_win()                
        return self.running

           
            
    def allow_event(self):
        tmp = win32gui.GetForegroundWindow()
        return self.dofus_handler.is_dofus_window(tmp)
       

    def ask_stop(self):
        self.dofus_handler.stop()
        
    def stop_manager(self):
        self.listener.stop()
        self.keyboard_thread.stop()
        self.running = False
    
    def next_turn(self):
        time.sleep(0.2)
        self._switch_next_win()

    def _switch_previous_win(self):
        if( not self.allow_event()):
            return
        self.dofus_handler.open_previous_page()
    
    def _switch_next_win(self):
        if( not self.allow_event()):
            return
        self.dofus_handler.open_next_page()

    def _open_current(self):
        self.dofus_handler.open_current_page()
       
    

 

def keyDown(hid, key):
    """win32con.VK_NUMPAD9"""
    win32api.SendMessage(hid, win32con.WM_KEYDOWN, key, 0)
    win32api.SendMessage(hid, win32con.WM_KEYUP, key, 0) 
        
if __name__ == "__main__":
    with open("config.json") as file:
        config = json.load(file) 
    
    DM = DofusManager(config)
    # DM.start()
    # time.sleep(2)
    # DM.reset_page()
    