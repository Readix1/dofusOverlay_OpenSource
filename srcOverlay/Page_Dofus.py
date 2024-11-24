import win32process
import win32gui
import win32api
import win32con
import logging
import pythoncom
import pywintypes
import win32com.client
import time

from srcOverlay.information import Information 

class Page_Dofus():
    def __init__(self, hwnd, handler=None,ini=0):
        self.hwnd = hwnd
        _,self.pid = win32process.GetWindowThreadProcessId(hwnd)
        
        self.name=""
        self.classe=""
        self.sexe="male"
        self.ini = ini
        
        self.selected = True
        
        logging.info(f"nom: {self.name}, hwnd: {hwnd}")
        self.handler = handler
        
    def serialize(self):
        if self.name == "":
            return {}
        return {self.name:{ "classe":self.classe, "sexe":self.sexe, "ini":self.ini}}
    
    def get_info(self):
        if self.name == "":
            return
        Information.getInfo(self)
    
    def set_name(self):
        name = win32gui.GetWindowText(self.hwnd)
        lname = name.split(" - ")
        if any(char.isdigit() for char in lname[0]):#(len(lname) == 1):
            self.name = ""
            self.classe = ""
            self.ini = 0
        else:
            self.name = lname[0]
            if not any(char.isdigit() for char in lname[1]) and not any(char.isdigit() for char in lname[0]) and self.classe == "":
                self.classe = lname[1]

       
    def update_name(self):
        tmp_name = self.name
        tmp_classe = self.classe
        self.set_name()
        if tmp_name != self.name or (tmp_classe and tmp_classe != self.classe):
            self.get_info()
        return tmp_name != self.name or tmp_classe != self.classe
    
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
        
        
        
    def __str__(self):
        return str(self.hwnd) +":" +self.name


if __name__ == "__main__":
    hid=132654
    d = Page_Dofus(hid)
