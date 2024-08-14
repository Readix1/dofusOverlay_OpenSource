import win32process
import win32gui
import win32api
import win32con
import logging
import pythoncom
import pywintypes
import win32com.client
import time

from srcOverlay.initiative import Initiative 

class Page_Dofus():
    def __init__(self, hwnd, handler=None,ini=0):
        self.hwnd = hwnd
        self.ini = ini
        _,self.pid = win32process.GetWindowThreadProcessId(hwnd)
        self.name=""
        self.set_name()
        self.set_initiative()
        logging.info(f"nom: {self.name}, hwnd: {hwnd}")
        self.handler = handler
    
    def set_name(self):
        name = win32gui.GetWindowText(self.hwnd)
        lname = name.split(" - ")
        if(len(lname) == 1):
            self.name = ""
        else:
            self.name = lname[0]
        
    def get_infos(self):
        return self.hwnd, self.pid, self.name
       
    def set_initiative(self):
        self.ini = Initiative.getIni(self.name)

    
    def update_name(self):
        tmp_name = self.name
        self.set_name()
        if tmp_name != self.name:
            self.set_initiative()
        return tmp_name != self.name
    
    def open(self):
        try :
            pythoncom.CoInitialize()
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('^')
            win32gui.ShowWindow(self.hwnd,3)
            win32gui.SetForegroundWindow(self.hwnd)
        except pywintypes.error as e :
            logging.error(f"Error when open {self.name} {e}")
            return
        
            
    def press(self, lParam):
        win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        time.sleep(0.1)
        win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, None, lParam)
        
    def __str__(self):
        return str(self.hwnd) +":" +self.name


if __name__ == "__main__":
    hid=132654
    d = Page_Dofus(hid)
