import sys
sys.path.append(r'd:\all\bot\python\pythondof\dofusOverlay_OP/')

from tkinter import IntVar, StringVar, Frame
from customtkinter import CTkToplevel, CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCheckBox, CTkComboBox, CTkFont, CTkImage

from pynput import keyboard, mouse

from PIL import Image
from srcOverlay.interface.image_selector import ImageSelector

from threading import Lock

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
        
        self.listener_lock = Lock()
        self.keyboard_listener = None
        self.mouse_listener = None
        self.listeners_active = False
        
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
        
        self.refresh_img = load_image("ressources/img_overlay/refresh.png", (20, 20))
        actualise_button = CTkButton(principal_button_frame, text="Actualiser", command=self.actualise, image=self.refresh_img)
        actualise_button.pack(side="bottom", anchor="sw", padx=20, pady=5)
        
        self.launch_img = load_image("ressources/img_overlay/start.png", (20, 20))
        launch_button = CTkButton(principal_button_frame, text="Lancer", command=self.enter, image=self.launch_img)
        launch_button.pack(side="bottom", anchor="sw", padx=20, pady=5)
        
        # Save buttons
        save_load_button_frame = CTkFrame(self.button_frame)
        save_load_button_frame.pack(fill="both",)
        
        self.save_img = load_image("ressources/img_overlay/save.png", (20, 20))
        save_button = CTkButton(save_load_button_frame, text="Save", command=self.save, width=40, height=40, image=self.save_img)
        save_button.pack(side="left", anchor="nw", padx=(20, 5), pady=10)
        
        self.load_img = load_image("ressources/img_overlay/load.png", (20, 20))
        load_button = CTkButton(save_load_button_frame, text="Load", width=40, height=40 , command=self.load, image=self.load_img)
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

        if self.dh:
            shortcuts = self.dh.get_shortcut()
            
            self.update_previous_button(shortcuts[0])
            self.update_next_button(shortcuts[1])
        
                
        self.create_table()
        
        # Window drag
        self.bind('<Button-1>', self.clickwin)
        self.bind('<B1-Motion>', self.dragwin)
        self.bind('<ButtonRelease-1>', self.release_dragwin)
        
    def update_previous_button(self, shortcut):
        self.previous_button.configure(text=shortcut)
        
    def update_next_button(self, shortcut):
        self.next_button.configure(text=shortcut)
        
    def update_previous_shortcut(self):
        self.previous_button.configure(text="")

        # Démarrer un listener pour écouter les touches du clavier
        self.start_update_shortcut_listener(self.previous_button, "prev_win")
            
    
    def update_next_shortcut(self):
        self.next_button.configure(text="")

        # Démarrer un listener pour écouter les touches du clavier
        self.start_update_shortcut_listener(self.next_button, "next_win")
        
    def update_specific_shortcut(self, button, shortcut_attr_name):
        button.configure(text="")
        
        # Démarrer un listener pour écouter les touches du clavier
        self.start_update_shortcut_listener(button, shortcut_attr_name, specific_page=True)
    
    def start_update_shortcut_listener(self, button, shortcut_attr_name, specific_page=False):
        
        if self.listeners_active==True:
            print("Listeners déjà actifs. Ignorer la réactivation.")
            return
        
        self.listeners_active = True
        
        def stop_listeners():
            # Arrêter les listeners actifs
            if hasattr(self, 'keyboard_listener') and self.keyboard_listener:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
            if hasattr(self, 'mouse_listener') and self.mouse_listener:
                self.mouse_listener.stop()
                self.mouse_listener = None
            self.listeners_active = False
            return False

        def start_keyboard_listener():
            self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
            self.keyboard_listener.start()

        def start_mouse_listener():
            self.mouse_listener = mouse.Listener(on_click=on_click)
            self.mouse_listener.start()
        
        def on_press(key):
            with self.listener_lock:  # Bloquer l'accès avec le verrou
                try:
                    key_name = ""
                    if '_name_' in key.__dict__:
                        key_name = key.name
                    elif key.char:
                        if ord(key.char) < 32:
                            key_char = chr(ord('a') + ord(key.char) - 1)
                            key_name = key_char
                        else:
                            key_name = str(key.char)

                    if key_name == "shift":
                        self.current = 1
                    elif "ctrl" in key_name:
                        self.current = 2
                    elif key_name == "esc":
                        # if not specific_page:
                        #     button.configure(text=getattr(self, shortcut_attr_name))
                        # else:
                        for dofus in self.pages_dofus:
                            if dofus.name == shortcut_attr_name:
                                dofus.shortcut = ""
                                break
                        button.configure(text="Aucun")
                        if self.dh:
                            self.dh.update_shortcut(shortcut_attr_name, "", specific_page)
                        self.current = 0
                        return stop_listeners()
                    else:
                        prefix = ""
                        if self.current == 1:
                            prefix += "shift+"
                        elif self.current == 2:
                            prefix += "ctrl+"

                        shortcut_name = prefix + str(key_name)

                        if not specific_page:
                            setattr(self, shortcut_attr_name, shortcut_name)
                            button.configure(text=shortcut_name)
                            if self.dh:
                                if shortcut_name and "next" in shortcut_attr_name:
                                    self.dh.update_shortcut("next_win", shortcut_name)
                                else:
                                    self.dh.update_shortcut("prev_win", shortcut_name)
                        else:
                            for dofus in self.pages_dofus:
                                if dofus.name == shortcut_attr_name:
                                    dofus.shortcut = shortcut_name
                                    break
                            button.configure(text=shortcut_name)
                            if self.dh:
                                self.dh.update_shortcut(shortcut_attr_name, shortcut_name, specific_page)

                        self.current = 0
                        return stop_listeners()

                except AttributeError as e:
                    print(f"special key {key}", e)
                    return False
        
            
        def on_release(key):
            if '_name_' in key.__dict__ :
                print(key.name)
                if key.name == "shift" or "ctrl"in key.name:
                    self.current=0
        
        def on_click(x, y, key, pressed):
            if pressed and ( key.name=="x2" or key.name=="x1" ):
                with self.listener_lock:  # Bloquer pendant l'action de clic
                    shortcut_name = f"{key.name}"
                    if not specific_page:
                        setattr(self, shortcut_attr_name, shortcut_name)
                        button.configure(text=shortcut_name)
                        if self.dh:
                            if shortcut_name and "next" in shortcut_attr_name:
                                self.dh.update_shortcut("next_win", shortcut_name)
                            else:
                                self.dh.update_shortcut("prev_win", shortcut_name)
                    else:
                        for dofus in self.pages_dofus:
                            if dofus.name == shortcut_attr_name:
                                dofus.shortcut = shortcut_name
                                break
                        button.configure(text=shortcut_name)
                        if self.dh:
                            self.dh.update_shortcut(shortcut_attr_name, shortcut_name, specific_page)

                    self.current = 0
                    return stop_listeners()

        start_keyboard_listener()

        start_mouse_listener()
    
    def actualise(self):
        self.pages_dofus = sorted(self.dh.dofus, key=lambda x: x.ini, reverse=True)
        self.create_rows()
        self.update_ini()
        
        if self.dh:
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
        headers = ["", "Personnage", "Classe", "Raccourci", "Initiative", "Actif"]
        column_widths = [20, 200, 35, 120, 60, 40]
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
        personnage_label = CTkLabel(row_frame, text=dofus.name, width=200)
        personnage_label.pack(side="left", padx=5)
        
        # Image label
        
        image_path = dofus.image_path if dofus.image_path else "ressources\\img_overlay\\"+get_image_path(dofus.classe)
        
        image = load_image(image_path, (30, 30))
        image_label = CTkLabel(row_frame, image=image, width=35, text="")
        image_label.image = image  # Référence pour éviter suppression
        image_label.pack(side="left", padx=5)
        
        image_label.bind("<Button-1>", lambda event, dofus=dofus, image_label=image_label: self.open_image_selector(dofus, image_label))

        
        # Raccourci label
        shortcut_var = StringVar(value="Aucun" if dofus.shortcut == "" else dofus.shortcut)
        shortcut_label = CTkLabel(row_frame, text=shortcut_var.get(), width=120)
        shortcut_label.pack(side="left", padx=5)

        shortcut_label.bind("<Button-1>", lambda event, dofus=dofus, shortcut_label=shortcut_label: self.update_specific_shortcut(shortcut_label, dofus.name))

        # Initiative entry
        ini_var = StringVar(value=dofus.ini)
        self.ini_dict[dofus] = ini_var
        initiative_entry = CTkEntry(row_frame, textvariable=ini_var, width=60, )
        initiative_entry.pack(side="left", padx=5)

        # Checkbox
        checkbox_frame = CTkFrame(row_frame, width=40)
        checkbox_frame.pack(expand=True, side="left", fill="both", padx=5)
        check_var = IntVar(value=dofus.selected)
        self.check_dict[dofus] = check_var
        active_checkbox = CTkCheckBox(checkbox_frame, variable=check_var, text="", width=0, height=0, checkbox_width=20, checkbox_height=20)
        active_checkbox.pack(anchor="nw", expand=True, padx=10, pady=10)

        self.row_widgets.append(row_frame)
    
    def open_image_selector(self, dofus, image_label):
        """Ouvre une nouvelle fenêtre pour sélectionner une image."""
        ImageSelector(self, dofus, image_label, resizable=False)



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
        self.withdraw()
    
    def enter(self):
        for dofus in self.pages_dofus:
            dofus.ini = int(self.ini_dict[dofus].get() if self.ini_dict[dofus].get() else 0)
            dofus.selected = self.check_dict[dofus].get()
            
            if self.overlay:
                self.overlay.ask_update_selected_status(dofus)
            
            
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
            

            
def load_image(path, size, rotate=False):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    if rotate:
        img = img.rotate(180)  # Rotation de 180 degrés
    return CTkImage(img, size=size)

dict_head = {"feca":10, "osamodas":20, "enutrof":30, "sram":40, "xelor":50, "ecaflip":60, "eniripsa":70, 
             "iop":80, "cra":90, "sadida":100, "sacrieur":110, "pandawa":120, "roublard":130, "zobal":140, 
             "steamer":150, "eliotrope":160, "huppermage":170, "ouginak":180, "forgelance":200}


def get_image_path(classe="iop"):
    if classe in dict_head:
        return f"heads/{dict_head[classe]}_1.png"
    return "icons/1004.png"

if __name__ == "__main__":
    from srcOverlay.Page_Dofus import Page_Dofus
    
    pages_dofus = [Page_Dofus(1, ini=1), Page_Dofus(0, ini=2), Page_Dofus(4, ini=4)]
    pages_dofus[0].name = "test1"
    pages_dofus[1].classe = "feca"
    pages_dofus[1].name = "Indimo"
    pages_dofus[2].name = "Readix"
    ihm = Reorganiser(pages_dofus, None, None)
    ihm.mainloop()
