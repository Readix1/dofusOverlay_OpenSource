from tkinter import IntVar, StringVar, Frame
from customtkinter import CTkToplevel, CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCheckBox, CTkComboBox, CTkFont

from pynput import keyboard

from PIL import Image, ImageTk
from customtkinter import CTkImage

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
        self.previous_shortcut="Précédent"
        self.next_shortcut="Suivant"
        
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
        self.previous_shortcut = shortcut
        self.previous_button.configure(text=shortcut)
        
    def update_next_button(self, shortcut):
        self.next_shortcut = shortcut
        self.next_button.configure(text=shortcut)
        
    def update_previous_shortcut(self):
        self.previous_button.configure(text="")

        # Démarrer un listener pour écouter les touches du clavier
        self.start_update_shortcut_listener(self.previous_button, "previous_shortcut")
        if self.dh and self.previous_shortcut:
            self.dh.update_shortcut("prev_win", self.previous_shortcut)
            
    
    def update_next_shortcut(self):
        self.next_button.configure(text="")

        # Démarrer un listener pour écouter les touches du clavier
        self.start_update_shortcut_listener(self.next_button, "next_shortcut")
        if self.dh and self.next_shortcut:
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
                elif key_name == "esc":
                    button.configure(text=getattr(self, shortcut_attr_name))
                    self.current=0
                    return False
                else:
                    prefix = ""
                    if self.current==1:
                        prefix+="shift+"
                    elif self.current==2:
                        prefix+="ctrl+"
                        
                    shortcut_name = prefix+str(key_name)
                    setattr(self, shortcut_attr_name, shortcut_name)
                    button.configure(text=shortcut_name)
                    if self.dh:
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
        shortcut_var = StringVar(value=dofus.name)
        shortcut_label = CTkLabel(row_frame, text=shortcut_var.get(), width=120)
        shortcut_label.pack(side="left", padx=5)

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
    
    def open_image_selector(self, dofus, image_label):
        """Ouvre une nouvelle fenêtre pour sélectionner une image."""
        selector_window = CTkToplevel(self)
        selector_window.title("Sélection d'image")
        # selector_window.geometry("600x200")  # Taille ajustée pour inclure le padding
        selector_window.attributes('-topmost', True)  # Toujours au premier plan

        # Bloque les interactions avec d'autres fenêtres tant que celle-ci est ouverte
        selector_window.grab_set()
        selector_window.focus_force()

        def on_focus_out(event):
            if not selector_window.focus_get():  # Vérifie si la fenêtre a perdu le focus
                selector_window.destroy()

        selector_window.bind("<FocusOut>", on_focus_out)  # Lier l'événement
        
        background_color = selector_window.cget("bg")

        # Ajout d'une frame avec padding
        frame = Frame(selector_window, bg=background_color)
        frame.grid(padx=15, pady=15)  # Espacement autour de la frame

        max_columns = 5  # Nombre de colonnes
        images_per_column = 4  # Nombre de groupes par colonne
        current_row = 0
        current_column = 0

        for idx, i in enumerate(list(range(1, 19)) + [20]):
            # Chargement des images
            male_path = "ressources\\img_overlay\\" + f"heads/{i}0_1.png"
            female_path = "ressources\\img_overlay\\" + f"heads/{i}1_1.png"
            icon_path = "ressources\\img_overlay\\" + f"icons/{i}0.png"
            
            
            image_male = load_image(male_path, (30, 30))
            image_female = load_image(female_path, (30, 30))
            image_icon = load_image(icon_path, (30, 30))

            # Création et positionnement des labels pour icône, mâle et femelle
            label_icon = CTkLabel(frame, image=image_icon, text="", compound="top")
            label_icon.image = image_icon  # Référence pour éviter suppression
            
            padx = (0, 6) if current_column == 0 else (26, 6)
            label_icon.grid(column=current_column * 3, row=current_row, pady=5, padx=padx)

            label_male = CTkLabel(frame, image=image_male, text="", compound="top")
            label_male.image = image_male
            label_male.grid(column=current_column * 3 + 1, row=current_row, pady=5, padx=(3, 3))

            label_female = CTkLabel(frame, image=image_female, text="", compound="top")
            label_female.image = image_female
            label_female.grid(column=current_column * 3 + 2, row=current_row, pady=5, padx=(3, 3))

            # Ajout d'une action au clic sur l'image mâle
            label_male.bind(
                "<Button-1>",
                lambda event, img_path=male_path: self.update_character_image(dofus, img_path, selector_window, image_label),
            )
            
            label_female.bind(
                "<Button-1>",
                lambda event, img_path=female_path: self.update_character_image(dofus, img_path, selector_window, image_label),
            )
            
            label_icon.bind(
                "<Button-1>",
                lambda event, img_path=icon_path: self.update_character_image(dofus, img_path, selector_window, image_label),
            )

            # Gérer le changement de colonne et de ligne
            current_row += 1
            if current_row >= images_per_column:
                current_row = 0
                current_column += 1

                # Arrête si le nombre maximum de colonnes est atteint
                if current_column >= max_columns:
                    break
                
            # Ajouter une séparation de 15 unités entre les colonnes
            if current_column > 0:
                frame.grid_columnconfigure(current_column, minsize=15)



    def update_character_image(self, dofus, image_path, window, image_label):
        """Met à jour l'image d'un personnage dans l'interface principale."""
        # Charger la nouvelle image
        dofus.image_path = image_path
        new_image = load_image(image_path, (30, 30))

        # Mettre à jour le bouton dans l'interface principale
        button = image_label
        button.configure(image=new_image)
        button.image = new_image  # Référence pour éviter suppression

        # Ferme la fenêtre de sélection
        window.destroy()

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
            dofus.ini = int(self.ini_dict[dofus].get())
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
    import sys
    sys.path.append(r'd:\all\bot\python\pythondof\dofusOverlay_OP/')
    from srcOverlay.Page_Dofus import Page_Dofus
    
    pages_dofus = [Page_Dofus(1, ini=1), Page_Dofus(0, ini=2), Page_Dofus(4, ini=4)]
    pages_dofus[0].name = "test1"
    pages_dofus[1].classe = "feca"
    pages_dofus[1].name = "Indimo"
    pages_dofus[2].name = "Readix"
    ihm = Reorganiser(pages_dofus, None, None)
    ihm.mainloop()
