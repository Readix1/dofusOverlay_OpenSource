import win32process
import win32gui
import win32con
import logging
import pythoncom
import pywintypes
import win32com.client
import time
import threading
import ctypes

from srcOverlay.information import Information 


from pywinauto import Application, keyboard
import pywinauto
import time

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ULONG_PTR),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("data",)
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("data", INPUT_UNION),
    ]


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
            shell.SendKeys("%")
            if win32gui.IsIconic(self.hwnd):  # Vérifie si la fenêtre est réduite
                win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)  # Restaure la fenêtre si elle est réduite
            win32gui.SetForegroundWindow(self.hwnd)
        except pywintypes.error as e :
            logging.error(f"Error when open {self.name} {e}")
            return
        
    def open_test(self):
        try:
            # Se connecter à la fenêtre via son handle (hwnd)
            app = Application().connect(handle=self.hwnd, timeout=5)
            window = app.window(handle=self.hwnd)

            # Vérifier si la fenêtre est minimisée et la restaurer si nécessaire
            if window.is_minimized():
                window.restore()

            # Envoyer une touche Alt pour éviter les restrictions de Windows
            keyboard.send_keys('%')

            # Mettre la fenêtre au premier plan
            window.set_focus()
            window.set_foreground()

            # Pause pour stabiliser l'affichage
            time.sleep(0.5)

        except pywinauto.findwindows.ElementNotFoundError:
            print(f"Erreur : Impossible de trouver la fenêtre avec hwnd={self.hwnd}")
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

        
    def click(self):
        """Simule un clic gauche a la position actuelle du curseur."""
        with self.lock:
            x,y = win32gui.GetCursorPos()

            if win32gui.GetForegroundWindow() != self.hwnd:
                logging.warning(
                    "Impossible de cliquer sur %s: la fenetre n'est pas au premier plan",
                    self.hwnd,
                )
                return

            user32 = ctypes.windll.user32
            button_down = INPUT(type=0)
            button_down.mi.dwFlags = MOUSEEVENTF_LEFTDOWN
            if user32.SendInput(1, ctypes.byref(button_down), ctypes.sizeof(INPUT)) != 1:
                logging.error("SendInput a echoue pour la fenetre %s", self.hwnd)
                return

            time.sleep(0.01)
            button_up = INPUT(type=0)
            button_up.mi.dwFlags = MOUSEEVENTF_LEFTUP
            if user32.SendInput(1, ctypes.byref(button_up), ctypes.sizeof(INPUT)) != 1:
                logging.error("SendInput a echoue pour relacher le bouton sur %s", self.hwnd)
                return

            logging.info(f"click de {self.name}, coord: {x}, {y}")
            
        
        
    def __str__(self):
        return str(self.hwnd) +":" +self.name


if __name__ == "__main__":
    hid=132654
    d = Page_Dofus(hid)
