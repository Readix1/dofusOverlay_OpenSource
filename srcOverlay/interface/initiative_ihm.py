

from tkinter import Toplevel, Frame, Label, Entry, Checkbutton, StringVar, Button, Tk, IntVar
import json




class Initiative_ihm(Toplevel):
    def __init__(self, hwnd, names, overlay):
        super().__init__()
        
        self.overlay = overlay
        
        self.wm_resizable(False, False)
        self.attributes('-topmost', True)
        self.overrideredirect(True)
        self.geometry('+'+str(500)+"+"+str(500))
        
        self.hwnd_dict = {name: hwnd for name, hwnd in zip(names, hwnd)}
        
        self.ini_dict = dict()
        self.check_dict = dict()
        
        with open("ressources/initiative.json", "r") as f:
            self.initiative = json.load(f)
        
        print(self.initiative)
        
        ### Header
        header_frame = Frame(self)
        header_frame.pack(padx=3, pady=3, expand=True, fill="x")
        
        param_button = Button(header_frame, text="*")
        param_button.pack(side="left")
        
        header_label = Label(header_frame, text="Reorganizer", font=("Arial", 25, "bold"))
        header_label.pack(side="left", expand=True, fill="x")
        
        close_button = Button(header_frame, text="X", command=self.destroy)
        close_button.pack(side="right",)
        
        ### Personnage
        personnage_frame = Frame(self)
        personnage_frame.pack(padx=3, pady=3)
        
        personnage_label = Label(personnage_frame, text="Personnage", font=("Arial", 12, "underline"))
        personnage_label.grid(row=0, column=1)
        
        initiative_label = Label(personnage_frame, text="Initiative",  font=("Arial", 12, "underline"))
        initiative_label.grid(row=0, column=2)
        
        for i, name in enumerate(names):
            personnage = Label(personnage_frame, text=name)
            personnage.grid(row=i+1, column=1)
            
            v = StringVar()
            v.set(self.initiative[name]) if name in self.initiative else v.set(0)
            self.ini_dict[name] = v
            initiative = Entry(personnage_frame, width=6, textvariable=v)
            initiative.grid(row=i+1, column=2)
            
            
            CheckVar1 = IntVar()
            CheckVar1.set(1)
            self.check_dict[name] = CheckVar1
            check = Checkbutton(personnage_frame, variable=CheckVar1, )
            check.grid(row=i+1, column=3)
            
        personnage_frame.columnconfigure(2, minsize=50, weight=0)
        
        enter_button = Button(personnage_frame, text="Enter", command=self.enter)
        enter_button.grid(row=len(names)+1, column=1, columnspan=3)
        
        
        
    
        self._offsetx = 0
        self._offsety = 0
        self.bind('<Button-1>',self.clickwin)
        self.bind('<B1-Motion>',self.dragwin)
        
    def dragwin(self,event):
        deltax = event.x - self._offsetx
        deltay = event.y - self._offsety
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry('+{x}+{y}'.format(x=x,y=y))

    def clickwin(self,event):
        self._offsetx = event.x
        self._offsety = event.y
        
        
    def enter(self):
        for name, v in self.ini_dict.items():
            if self.check_dict[name].get() == 1:
                self.initiative[name] = int(v.get())
                
        with open("ressources/initiative.json", "w") as f:
            json.dump(self.initiative, f)
            
        # print(sorted(self.ini_dict.keys(), key=lambda x: int(self.ini_dict[x].get()), reverse=True))
        name_ordered = [name for name in sorted(self.ini_dict.keys(), key=lambda x: int(self.ini_dict[x].get()), reverse=True) if self.check_dict[name].get() == 1]
        hwnd_ordered = [self.hwnd_dict[name] for name in name_ordered]
        if self.overlay:
            self.overlay.update_order(hwnd_ordered, name_ordered)
            self.overlay.reorganise = None
            
        self.destroy()

if __name__ == "__main__":
    ihm = Initiative_ihm([397488, 528600, 1511090, 2426032], ['Tc-hupper', 'Tc-arc', 'Tc-panda', 'Tc-fecaa'], None)
    ihm.mainloop()