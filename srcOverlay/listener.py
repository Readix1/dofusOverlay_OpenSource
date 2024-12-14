from threading import Thread
import time
import win32gui
import logging

class Listener(Thread):
    def __init__(self, dh):
        Thread.__init__(self)
        
        self.dh = dh
        self.current_hwnd = None
        
    def run(self):
        while self.dh.running:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd != self.current_hwnd:
                self.current_hwnd = hwnd
                self.dh.update_shown(hwnd)
            time.sleep(0.3)
        logging.info("Listener stopped")
        
               

           