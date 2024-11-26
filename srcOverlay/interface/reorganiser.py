from tkinter import IntVar, StringVar
from customtkinter import CTkToplevel, CTkFrame, CTkLabel, CTkEntry, CTkButton, CTkCheckBox, CTkComboBox

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
        reduce_button = CTkButton(frame, text="_", command=self.close, width=20, height=20)
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
        
        
        self.create_table()
        
        # Window drag
        self.bind('<Button-1>', self.clickwin)
        self.bind('<B1-Motion>', self.dragwin)
        self.bind('<ButtonRelease-1>', self.release_dragwin)
    
    def actualise(self):
        self.create_rows()
        self.update_ini()
        
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
        check_var = IntVar(value=1)
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
            self.ini_dict[dofus].set(dict_ini[dofus.name])
            # dofus.ini = int(self.ini_dict[dofus].get())
    
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
        if self.overlay:
            self.overlay.reorganise = None
        self.destroy()
    
    def enter(self):
        for dofus in self.pages_dofus:
            dofus.ini = int(self.ini_dict[dofus].get())
            dofus.classe = self.class_dict[dofus].get()
            dofus.sexe = self.gender_dict[dofus].get()
            
            print(dofus.name, dofus.ini, dofus.classe, dofus.sexe)
        
        if self.overlay:
            self.overlay.reorganise = None
            
        if self.dh:
            self.dh.update_order()
        self.destroy()


    def save(self):
        if self.dh:
            self.dh.save_dofus_info()
    
    def load(self):
        if self.dh:
            self.dh.load_dofus_info()
            self.create_rows()
        

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
