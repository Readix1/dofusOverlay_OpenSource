from tkinter import IntVar, StringVar
from customtkinter import CTkToplevel, CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCheckBox, CTkComboBox, CTkFont

from pynput import keyboard

class Reorganiser(CTkToplevel):
    def __init__(self, pages_dofus, overlay, dh):
        super().__init__()
        
        self.overlay = overlay
        self.dh = dh
        
        self.wm_resizable(False, False)
        self.attributes('-topmost', True)
        self.overrideredirect(True)
        self.geometry(f"{850}x{600}+{500}+{200}")
        
        self.pages_dofus = sorted(pages_dofus, key=lambda x: x.ini, reverse=True)
        
        self.personnage_frame = None
        self.dragging_row = None  # For drag and drop rows
        self.disable_window_drag = False  # New: Control window drag based on context
        self.current=0
        
        self.ini_dict = {}
        self.check_dict = {}
        self.class_dict = {}
        self.gender_dict = {}
        
        self.row_widgets = []
        
        self.principal_frame = CTkFrame(self)
        self.principal_frame.pack(padx=10, pady=10, expand=True, fill="both")
        
        # self.principal_frame.grid_columnconfigure(0, weight=2, minsize=100)
        self.principal_frame.grid_rowconfigure(0, weight=1)
        self.principal_frame.grid_columnconfigure(1, weight=1, minsize=50)
        
        self.tab_frame = CTkFrame(self.principal_frame, border_width=2)
        self.tab_frame.grid(row=0, column=0, sticky="nsew")
        
        self.button_frame = CTkFrame(self.principal_frame)
        self.button_frame.grid(row=0, column=1, sticky="nsew")
        
        # Header buttons
        principal_button_frame = CTkFrame(self.button_frame)
        principal_button_frame.pack(fill="both")
        
        corner_button_frame = CTkFrame(principal_button_frame, border_width=1)
        corner_button_frame.pack(side="top", anchor="ne")
        
        frame = CTkFrame(corner_button_frame)
        frame.pack(padx=4, pady=8)
        
        close_button = CTkButton(frame, text="X", command=self.close, width=20, height=20)
        close_button.pack(side="right")
        reduce_button = CTkButton(frame, text="_", command=self.reduce, width=20, height=20)
        reduce_button.pack(side="right")
        
        actualise_button = CTkButton(principal_button_frame, text="Actualiser", command=self.actualise)
        actualise_button.pack(side="bottom", anchor="sw", padx=20, pady=5)
        launch_button = CTkButton(principal_button_frame, text="Lancer", command=self.enter)
        launch_button.pack(side="bottom", anchor="sw", padx=20, pady=5)
        
        # Save buttons
        save_load_button_frame = CTkFrame(self.button_frame)
        save_load_button_frame.pack(fill="both",)
        
        save_button = CTkButton(save_load_button_frame, text="Save", command=self.save, width=40, height=40)
        save_button.pack(side="left", anchor="nw", padx=(20, 5), pady=10)
        
        load_button = CTkButton(save_load_button_frame, text="Load", width=40, height=40 , command=self.load)
        load_button.pack(side="left", anchor="nw", pady=10)
        
        # raccourci Précédent / Suivant
        raccourci_frame = CTkFrame(self.button_frame)
        raccourci_frame.pack(fill="both",)
        
        self.next = load_image("ressources/img_overlay/next.png", (20, 20))
        self.previous = load_image("ressources/img_overlay/next.png", (20, 20), rotate=True)
        
        raccourci_frame.grid_columnconfigure(0, weight=1)
        raccourci_frame.grid_columnconfigure(1, weight=1)
        
        self.previous_button = CTkButton(raccourci_frame, text="Précédent", command=self.update_previous_shortcut, image=self.previous)
        self.previous_button.grid(row=0, column=0, padx=(20, 5), pady=10)
        
        
        self.next_button = CTkButton(raccourci_frame, text="Suivant", command=self.update_next_shortcut, image=self.next, compound="right")
        self.next_button.grid(row=0, column=1,  pady=10, padx=(0, 10))

        shortcuts = self.dh.get_shortcut()
        
        self.update_previous_button(shortcuts[0])
        self.update_next_button(shortcuts[1])
        
                
        self.create_table()
        
        # Window drag
        self.bind('<Button-1>', self.clickwin)
        self.bind('<B1-Motion>', self.dragwin)
        self.bind('<ButtonRelease-1>', self.release_dragwin)
        
    def update_previous_button(self, shortcut):
        self.previous_shortcut = shortcut
        self.previous_button.configure(text=shortcut)
        
    def update_next_button(self, shortcut):
        self.next_shortcut = shortcut
        self.next_button.configure(text=shortcut)
        
    def update_previous_shortcut(self):
        self.previous_button.configure(text="")

        # Démarrer un listener pour écouter les touches du clavier
        self.start_update_shortcut_listener(self.previous_button, "previous_shortcut")
        if self.previous_shortcut:
            self.dh.update_shortcut("prev_win", self.previous_shortcut)
            
    
    def update_next_shortcut(self):
        self.next_button.configure(text="")

        # Démarrer un listener pour écouter les touches du clavier
        self.start_update_shortcut_listener(self.next_button, "next_shortcut")
        if self.next_shortcut:
            self.dh.update_shortcut("next_win", self.next_shortcut)
    
    def start_update_shortcut_listener(self, button, shortcut_attr_name):
        def on_press(key):
            try:
                key_name = ""
                if '_name_' in key.__dict__ :
                    key_name = key.name
                elif key.char:
                    if ord(key.char) < 32:
                        key_char = chr(ord('a') + ord(key.char) - 1)
                        key_name = key_char
                    else:
                        key_name = str(key.char)
                
                if key_name == "shift":
                    self.current=1
                elif "ctrl"in key_name:
                    self.current=2
                else:
                    prefix = ""
                    if self.current==1:
                        prefix+="shift+"
                    elif self.current==2:
                        prefix+="ctrl+"
                        
                    shortcut_name = prefix+str(key_name)
                    setattr(self, shortcut_attr_name, shortcut_name)
                    button.configure(text=shortcut_name)
                    if shortcut_name and "next" in shortcut_attr_name:
                        self.dh.update_shortcut("next_win", shortcut_name)
                    else:
                        self.dh.update_shortcut("prev_win", shortcut_name)
                    
                    self.current=0
                    return False

                
            except AttributeError as e:
                print(f"special key {key}", e)
                return False
        
            
        def on_release(key):
            if '_name_' in key.__dict__ :
                print(key.name)
                if key.name == "shift" or "ctrl"in key.name:
                    self.current=0

        # Démarrer le listener
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
    
    def actualise(self):
        self.pages_dofus = sorted(self.dh.dofus, key=lambda x: x.ini, reverse=True)
        self.create_rows()
        self.update_ini()
        shortcuts = self.dh.get_shortcut()
        
        self.update_previous_button(shortcuts[0])
        self.update_next_button(shortcuts[1])
        
        
    def create_rows(self):
        for widget in self.row_widgets:
            widget.destroy()
        
        # Create rows
        self.row_widgets = []
        for i, dofus in enumerate(self.pages_dofus):
            self.create_row(i, dofus)

    def create_table(self):
        if self.personnage_frame:
            self.personnage_frame.destroy()

        self.personnage_frame = CTkFrame(self.tab_frame)
        self.personnage_frame.pack(padx=10, pady=10, fill="x")

        # Create headers
        header_frame = CTkFrame(self.personnage_frame)
        # header_frame.pack(fill="x", padx=5, pady=5)
        header_frame.grid(padx=5, pady=5, row=0, column=0, sticky="nsew")
        headers = ["", "Personnage", "Classe", "Sexe", "Initiative", "Actif"]
        column_widths = [20, 150, 120, 80, 60, 40]
        for i, (header, width) in enumerate(zip(headers, column_widths)):
            label = CTkLabel(header_frame, text=header, width=width, font=("Arial", 12, "underline"),)
            label.grid(row=0, column=i, padx=5, sticky="w")

        self.create_rows()

    def create_row(self, index, dofus):
        row_frame = CTkFrame(self.personnage_frame, height=40)
        # row_frame.pack(fill="x", padx=5, pady=2)
        row_frame.grid(padx=5, pady=2, row=index+1, column=0, sticky="nsew")
        
        row_frame.identifier = dofus.name
        
        # Drag button
        move_button = CTkButton(row_frame, text="↕", width=20, height=20)
        move_button.pack(side="left", padx=5)
        move_button.bind('<Button-1>', lambda e, identifier=dofus.name: self.start_row_drag(e, identifier))
        move_button.bind('<B1-Motion>', self.perform_row_drag)
        move_button.bind('<ButtonRelease-1>', self.stop_row_drag)

        # Personnage label
        personnage_label = CTkLabel(row_frame, text=dofus.name, width=150)
        personnage_label.pack(side="left", padx=5)

        # Classe combo box
        class_var = StringVar(value=dofus.classe)
        self.class_dict[dofus] = class_var
        class_combobox = CTkComboBox(row_frame, variable=class_var, width=120,
                                    values= sorted([name.capitalize() for name in ["sacrieur", "cra", "iop", "ecaflip", "eliotrope", "eniripsa", 
                                                "enutrof", "feca", "huppermage", "osamodas", "pandawa", "roublard", 
                                                "sadida", "sram", "steamer", "xelor", "zobal", "ouginak", "forgelance"]]))
        class_combobox.pack(side="left", padx=5)

        # Sexe combo box
        gender_var = StringVar(value=dofus.sexe)
        self.gender_dict[dofus] = gender_var
        gender_combobox = CTkComboBox(row_frame, variable=gender_var, values=["male", "femelle"], width=80)
        gender_combobox.pack(side="left", padx=5)

        # Initiative entry
        ini_var = StringVar(value=dofus.ini)
        self.ini_dict[dofus] = ini_var
        initiative_entry = CTkEntry(row_frame, textvariable=ini_var, width=60)
        initiative_entry.pack(side="left", padx=5)

        # Checkbox
        checkbox_frame = CTkFrame(row_frame, width=40)
        checkbox_frame.pack(expand=True, side="left", fill="both", padx=5)
        check_var = IntVar(value=dofus.selected)
        self.check_dict[dofus] = check_var
        active_checkbox = CTkCheckBox(checkbox_frame, variable=check_var, text="", width=0, height=0, checkbox_width=20, checkbox_height=20)
        active_checkbox.pack(anchor="nw", expand=True, padx=10, pady=10)

        self.row_widgets.append(row_frame)

    def perform_row_drag(self, event):
        if self.dragging_row is None:
            return

        # Calculer l'offset total par rapport à l'origine du déplacement
        y_position = event.y
        row_height = self.row_widgets[0].winfo_height()

        # Calculer le nouvel index basé sur la hauteur des lignes
        new_index = max(0, min(len(self.row_widgets) - 1, self.dragging_row - 1 + y_position // row_height))

        # Si l'index change, réorganiser les widgets
        if new_index != self.dragging_row - 1:
            # Échanger les widgets dans la liste
            self.row_widgets.insert(new_index, self.row_widgets.pop(self.dragging_row - 1))
            
            # Réorganiser l'affichage des lignes
            for idx, widget in enumerate(self.row_widgets):
                widget.grid(row=idx + 1, column=0, sticky="nsew")
            
            # Mettre à jour l'index courant
            self.dragging_row = new_index + 1

    # Dragging rows
    def start_row_drag(self, event, identifier):
        self.disable_window_drag = True  # Disable window drag
        self.dragging_row = [i for i, widget in enumerate(self.row_widgets) if widget.identifier == identifier][0] + 1
        
        self._offsety = event.y

    def stop_row_drag(self, event):
        self.dragging_row = None
        self.disable_window_drag = False  # Re-enable window drag
        
        self.update_ini()
        
    def update_ini(self):
        dict_ini = {widget.identifier:len(self.pages_dofus)-i for i, widget in enumerate(self.row_widgets)}
        
        for dofus in self.pages_dofus:
            if dofus.name in dict_ini:
                self.ini_dict[dofus].set(dict_ini[dofus.name])
    
    # Dragging window
    def clickwin(self, event):
        if not self.disable_window_drag:  # Drag window only if no row interaction
            self._offsetx = event.x
            self._offsety = event.y
    
    def dragwin(self, event):
        if not self.disable_window_drag:  # Drag window only if no row interaction
            deltax = event.x - self._offsetx
            deltay = event.y - self._offsety
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry(f'+{x}+{y}')
    
    def release_dragwin(self, event):
        self._offsetx = 0
        self._offsety = 0
    
    def close(self):
        if self.dh:
            self.dh.stop()
        else:
            self.destroy()
        
    def reduce(self):
        # if self.overlay:
        #     self.overlay.reorganise = None
        self.withdraw()
    
    def enter(self):
        for dofus in self.pages_dofus:
            dofus.ini = int(self.ini_dict[dofus].get())
            dofus.classe = self.class_dict[dofus].get()
            dofus.sexe = self.gender_dict[dofus].get()
            dofus.selected = self.check_dict[dofus].get()
            
            if self.overlay:
                self.overlay.ask_update_selected_status(dofus)
            
        # if self.overlay:
        #     self.overlay.reorganise = None
            
        if self.dh:
            self.dh.update_order()

            
        self.withdraw()


    def save(self):
        if self.dh:
            self.dh.save_dofus_info()
    
    def load(self):
        if self.dh:
            self.dh.load_dofus_info()
            self.create_rows()
            
from PIL import Image, ImageTk
from customtkinter import CTkImage
            
def load_image(path, size, rotate=False):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    if rotate:
        img = img.rotate(180)  # Rotation de 180 degrés
    return CTkImage(img)

if __name__ == "__main__":
    import sys
    sys.path.append(r'd:\all\bot\python\pythondof\dofusOverlay_OP/')
    from srcOverlay.Page_Dofus import Page_Dofus
    
    pages_dofus = [Page_Dofus(1, ini=1), Page_Dofus(0, ini=2), Page_Dofus(4, ini=4)]
    pages_dofus[0].name = "test1"
    pages_dofus[1].name = "Indimo"
    pages_dofus[2].name = "Readix"
    ihm = Reorganiser(pages_dofus, None, None)
    ihm.mainloop()
