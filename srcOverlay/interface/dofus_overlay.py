from srcOverlay.interface.overlay import Overlay
from srcOverlay.interface.initiative_ihm import Initiative_ihm

from threading import RLock
import tkinter as tk
from PIL import Image,ImageTk
import win32gui
import win32com
import pythoncom


class DofusOverlay(Overlay):
    def __init__(self,config, order, order_name, open_dofus_methode=None, dh=None):
        Overlay.__init__(self, config["overlay"]['posx'],config["overlay"]["posy"], alpha=config["overlay"]['opacity'])
        self.bind("<<Destroy>>", lambda e: self.destroy())
        self.imagePath = {k:config['img']['path']+v['classe']+'_'+v['sexe']+".png" for k,v in config['img'].items() if k != 'path'}
        self.perso = dict()
        self.unselected_perso=[]
        self.order = []
        self.lock = RLock()
        
        self.reorganise = None
        
        self.frame_perso = tk.Frame(self, background="white")
        self.frame_perso.pack(side="left",padx=0, pady=0)
        
        self.curr_hwnd = 0
        
        self.update_order(order,order_name)
        
        self.is_visible = True
        
        self.open_dofus_methode=open_dofus_methode
        self.dh = dh
        
        
    def stop(self):
        self.event_generate("<<Destroy>>", when="tail")
    
    def getHwnd(self):        
        return [int(self.frame(),base=16)]
    
    def update_perso(self,hwnd):
        self.lock.acquire()
        for h in self.perso:
            if(h==hwnd):
                self.perso[h].config(borderwidth=2, relief="solid")

            else:
                self.perso[h].config(borderwidth=2, relief="flat")

        self.curr_hwnd = hwnd
        self.lock.release()
        
    def update_perso_and_visibility(self,hwnd):
        self.lock.acquire()
        if hwnd in list(self.perso.keys()):
            if hwnd != self.curr_hwnd:
                for h in self.perso:
                    if(h==hwnd):
                        self.perso[h].config(borderwidth=2, relief="solid")
                    else:
                        self.perso[h].config(borderwidth=2, relief="flat")
                        
                self.curr_hwnd = hwnd
        if hwnd in list(self.perso.keys())+self.getHwnd():
            if not self.is_visible:
                self.deiconify()
                self.is_visible = True
        
        elif self.is_visible:
            self.withdraw()
            self.is_visible = False
        self.lock.release()

    def update_order(self, order, order_name):
        self.lock.acquire()
        if(self.order == order_name):
            self.lock.release()
            return
        self.order = order_name
        self.perso = dict()
        lorder = len(order)
        l = lorder * 84
        h = 84
        self.geometry(str(l)+"x"+str(h))
        
        #clear
        for child in self.frame_perso.winfo_children():
            child.destroy()
        self.frame_perso.config(width=1)
        
        #building new
        for hwnd,n in zip(order, order_name):
            if(n not in self.imagePath):
                n = ""
            path = self.imagePath[n]
            img = ImageTk.PhotoImage(Image.open(path).resize((70,70)))
            f = tk.Label(self.frame_perso,image=img, background="white")
            f.bind("<Button-1>", lambda e,hid=hwnd : self.select(hid))
            f.bind("<Control-1>", lambda e, hid=hwnd : self.select_char(hid))
            f.image = img
            f.pack(side="left",padx=5, pady=5)
            self.perso[hwnd] = f
        
        self.update_perso(self.curr_hwnd)
        self.update()
        self.lock.release()
    
    def open_reorganize(self, order, order_name):
        print("open_reorganize")
        if not self.reorganise:
            self.reorganise = Initiative_ihm(order, order_name, self)
            
    
    def select_char(self, hwnd):
        if hwnd in self.unselected_perso:
            self.unselected_perso.remove(hwnd)
            self.perso[hwnd].config(background="white")
        else:
            self.unselected_perso.append(hwnd)
            self.perso[hwnd].config(background="grey")
    
    def get_selected_pages(self):
        return [hwnd for hwnd in self.perso if hwnd not in self.unselected_perso]
    
    def select(self,hwnd):
        if self.open_dofus_methode:
            self.open_dofus_methode(hwnd)
        else:
            pythoncom.CoInitialize()
            win32gui.SetForegroundWindow(hwnd)
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys('^')
            win32gui.ShowWindow(self.hwnd,3)
            self.update_perso(hwnd)

        