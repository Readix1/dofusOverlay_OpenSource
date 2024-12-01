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
        
        self.shortcut_dict = self.build_shortcut_dict()
    
    def func_correspondance(self, shortcut, dofus_name=None):
        if shortcut == None:
            return lambda : self.dofus_handler.open_specific_page(dofus_name)
        if shortcut == "next_win":
            return self._switch_next_win
        elif shortcut == "prev_win":
            return self._switch_previous_win
        elif shortcut == "next_turn":
            return self.next_turn
        elif shortcut == "focus_dofus":
            return self._open_current
        elif shortcut == "reorganizer":
            return self.dofus_handler.open_reorganize
        elif shortcut == "actualise":
            return self.dofus_handler.actualise
        elif shortcut == "stop":
            return self.ask_stop
        else: 
            logging.error(f"shortcut {shortcut} not found")
        
    def build_shortcut_dict(self):
        dict_res = {}
        for name, shortcut in self.config["keyboard_bindings"].items():
            dict_res[shortcut] = self.func_correspondance(name)
            
        for dofus in self.dofus_handler.dofus:
            if dofus.shortcut != "":
                dict_res[dofus.shortcut] = self.func_correspondance(None, dofus.name)    
        
        return dict_res
    
    def update_shortcut(self, shortcut_name, shortcut, specific_page=False):
        if specific_page==False:
            self.shortcut_dict[shortcut] = self.func_correspondance(shortcut_name)
            self.config["keyboard_bindings"][shortcut_name] = shortcut
        else:
            self.shortcut_dict[shortcut] = self.func_correspondance(None, shortcut_name)
            
                   
    def on_press(self,key):
        try:
            if '_name_' not in key.__dict__:
                return
            if key.name == "shift":
                self.current=1
            elif "ctrl"in key.name:
                self.current=2
            
        except:
            logging.error('erreur on press dofusManager')
            
    def on_release(self,key):
        key_name = ""
        if '_name_' in key.__dict__ :
            key_name = key.name
        elif key.char:
            if ord(key.char) < 32:
                key_char = chr(ord('a') + ord(key.char) - 1)
                key_name = key_char
            else:
                key_name = str(key.char)
        
        if key_name == "shift" or "ctrl"in key_name:
            self.current=0
        else:
            if self.current==1:
                key_name = "shift+" + key_name
            elif self.current==2:
                key_name = "ctrl+" + key_name
                
            if key_name in self.shortcut_dict:
                self.shortcut_dict[key_name]()
        
        return self.running
    

            
        
    def save_config(self):
        with open("ressources/config.json", 'r') as file:
            temp_config = json.load(file)
            
        temp_config["keyboard_bindings"]['prev_win'] = self.config["keyboard_bindings"]['prev_win']
        temp_config["keyboard_bindings"]['next_win'] = self.config["keyboard_bindings"]['next_win']
        
        with open("ressources/config.json", 'w') as file:
            json.dump(temp_config, file, indent=4)
            
    def get_shortcut(self, ):
        return self.config["keyboard_bindings"]['prev_win'], self.config["keyboard_bindings"]['next_win']


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
        self.running = False
        
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
    