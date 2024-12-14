from srcOverlay.interface.overlay import Overlay
from srcOverlay.interface.reorganiser import Reorganiser

from threading import RLock
import tkinter as tk
from PIL import Image,ImageTk

class DofusOverlay(Overlay):
    def __init__(self, config, order, open_dofus_methode=None, dh=None):
        Overlay.__init__(self, config["overlay"]['posx'],config["overlay"]["posy"], alpha=config["overlay"]['opacity'])
        self.bind("<<Destroy>>", lambda e: self.destroy())
        self.perso = dict()
        self.order = []
        self.hwnds = []
        
        
        self.lock = RLock()
        self.config_json = config
        
        self.reorganise = None
        
        self.frame_perso = tk.Frame(self, background="white")
        self.frame_perso.pack(side="left",padx=0, pady=0)
        
        self.current_shown = 0
        
        self.update_order(order)
        
        self.is_visible = True
        
        self.open_dofus_methode=open_dofus_methode
        self.dh = dh
        
        
    def stop(self):
        self.event_generate("<<Destroy>>", when="tail")
    
    def getHwnd(self):        
        if self.reorganise:
            return [int(self.frame(),base=16), int(self.reorganise.frame(),base=16)]
        return [int(self.frame(),base=16)]
    
    def update_perso(self, indice):
        self.lock.acquire()
        for i, dofus in enumerate(self.order):
            if(i==indice):
                self.perso[dofus].config(borderwidth=2, relief="solid")

            else:
                self.perso[dofus].config(borderwidth=2, relief="flat")

        self.current_shown = indice
        self.lock.release()
        
    def update_visibility(self, hwnd):
        self.lock.acquire()
        if hwnd in self.hwnds+self.getHwnd():
            if not self.is_visible:
                self.deiconify()
                self.is_visible = True
        
        elif self.is_visible:
            self.withdraw()
            self.is_visible = False
        self.lock.release()

    def update_order(self, order):
        self.lock.acquire()

        self.order = order
        self.hwnds = [d.hwnd for d in order]
        
        lorder = len(order)
        l = lorder * 84
        h = 84
        self.geometry(str(l)+"x"+str(h))
        
        #clear
        for child in self.frame_perso.winfo_children():
            child.destroy()
        self.frame_perso.config(width=1)
        
        #building new
        for i, dofus in enumerate(order):
            self.create_image(dofus, i)
        
        self.update_perso(self.current_shown)
        self.update()
        self.lock.release()
        
    def create_image(self, dofus, indice):

        if dofus.classe:
            path = self.config_json['img']['path']+dofus.classe+'_'+dofus.sexe+".png"
        else:
            path = self.config_json['img']['path']+"autre_0.png"
        img = ImageTk.PhotoImage(Image.open(path).resize((70,70)))
        f = tk.Label(self.frame_perso,image=img, background="white")
        f.bind("<Button-1>", lambda e, indice=indice : self.select(indice))
        f.bind("<Control-1>", lambda e, dofus=dofus : self.select_char(dofus))
        f.image = img
        f.pack(side="left",padx=5, pady=5)
        self.perso[dofus] = f
    
    def open_reorganize(self, order):
        print("open_reorganize")
        if not self.reorganise:
            self.reorganise = Reorganiser(order, self, self.dh)
            
    
    def select_char(self, dofus):
        dofus.selected = not dofus.selected
        
        if dofus.selected:
            self.perso[dofus].config(background="white")
        else:
            self.perso[dofus].config(background="grey")
    
    def select(self, indice):
        if self.open_dofus_methode:
            self.open_dofus_methode(indice)

        