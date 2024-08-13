from threading import Thread
import time
import win32gui
import logging

class Listener(Thread):
    def __init__(self,manager,interface):
        Thread.__init__(self)
        
        self.manager = manager
        self.interface = interface
        
    def run(self):
        while self.manager.running:
            hwnd = win32gui.GetForegroundWindow()
            self.interface.update_perso_and_visibility(hwnd)
            time.sleep(0.3)
        logging.info("Listener stopped")
        
               

           