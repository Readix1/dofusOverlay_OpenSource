import win32process
import win32gui
import win32api
import win32con
import logging
import pythoncom
import pywintypes
import win32com.client
import time
import threading

from srcOverlay.information import Information 

class Page_Dofus():
    def __init__(self, hwnd, handler=None,ini=0):
        self.hwnd = hwnd
        _,self.pid = win32process.GetWindowThreadProcessId(hwnd)
        
        self.name=""
        self.classe=""
        self.image_path = ""
        self.shortcut = ""
        self.ini = ini
        
        self.selected = True
        
        logging.info(f"nom: {self.name}, hwnd: {hwnd}")
        self.handler = handler
        self.lock = threading.Lock()
        
    def serialize(self):
        if self.name == "":
            return {}
        
        dict_res = {"classe":self.classe, "ini":self.ini, "image_path":self.image_path}
        if self.shortcut != "":
            dict_res.update({"shortcut":self.shortcut})
        
        return {self.name:dict_res}
    
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
            self.image_path = ""
        else:
            self.name = lname[0]
            if len(lname)>1 and not any(char.isdigit() for char in lname[1]) and not any(char.isdigit() for char in lname[0]) and self.classe == "":
                self.classe = lname[1]

       
    def update_name(self):
        tmp_name = self.name
        tmp_classe = self.classe
        self.set_name()
        if tmp_name != self.name or (tmp_classe and tmp_classe != self.classe):
            self.get_info()
            if self.handler and self.shortcut != "":
                self.handler.update_shortcut(self.name, self.shortcut, True)
        return tmp_name != self.name or tmp_classe != self.classe
    
    def open(self):
        try :
            pythoncom.CoInitialize()
            shell = win32com.client.Dispatch("WScript.Shell")
            # shell.SendKeys(self.char)
            shell.SendKeys("")
            win32gui.ShowWindow(self.hwnd,3)
            win32gui.SetForegroundWindow(self.hwnd)
        except pywintypes.error as e :
            logging.error(f"Error when open {self.name} {e}")
            return
        
    def click(self):
        """A ne pas utiliser avant l'aval d'ankama

        Args:
            x (_type_): _description_
            y (_type_): _description_
            pause (float, optional): _description_. Defaults to 0.3.
            manyTry (bool, optional): _description_. Defaults to False.
        """
        with self.lock:
            x,y = win32gui.GetCursorPos()
            curr_h = win32gui.GetForegroundWindow()
            realx,realy = win32gui.ScreenToClient(curr_h,(x,y))
            lParam = win32api.MAKELONG(realx,realy)
            win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
            time.sleep(0.01)
            win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, None, lParam)
            
            # time.sleep(0)
            
            logging.info(f"click de {self.name}, coord: {x}, {y}")
            
        
        
    def __str__(self):
        return str(self.hwnd) +":" +self.name


if __name__ == "__main__":
    hid=132654
    d = Page_Dofus(hid)
