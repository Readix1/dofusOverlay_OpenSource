import tkinter as tk

class Overlay(tk.Tk):
    def __init__(self, posx, posy, x=44, y=84, alpha=0.8):
        super().__init__()
        self.attributes('-alpha',alpha)
        self.attributes('-topmost', True)
        self.geometry(str(x)+'x'+str(y)+'+'+str(posx)+"+"+str(posy))
        self.wm_resizable(False, False)
        self.overrideredirect(True)
        self._offsetx = 0
        self._offsety = 0
        self.bind('<Button-1>',self.clickwin)
        self.bind('<B1-Motion>',self.dragwin)
        self.bind('<ButtonRelease-1>', self.stop_move)
                
    def dragwin(self, event):
        deltax = event.x - self._offsetx
        deltay = event.y - self._offsety
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry('+{x}+{y}'.format(x=x,y=y))

    def clickwin(self, event):
        self._offsetx = event.x
        self._offsety = event.y
        
    def stop_move(self, event):
        self._offsetx = 0
        self._offsety = 0
    