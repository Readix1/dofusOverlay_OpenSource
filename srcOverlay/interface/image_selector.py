import tkinter as tk
from customtkinter import CTkToplevel, CTkLabel, CTkButton, CTkFrame, CTkScrollableFrame
from tkinter import StringVar, Frame

from PIL import Image, ImageTk
from customtkinter import CTkImage

class ImageSelector:
    def __init__(self, parent, dofus, image_label):
        self.parent = parent
        self.dofus = dofus
        self.image_label = image_label
        self.selector_window = CTkToplevel(self.parent)
        self.selector_window.title("Sélection d'image")
        self.selector_window.attributes('-topmost', True)  # Toujours au premier plan
        self.selector_window.resizable(False, False)  # Fenêtre non redimensionnable
        
        # Bloque les interactions avec d'autres fenêtres tant que celle-ci est ouverte
        self.selector_window.grab_set()
        self.selector_window.focus_force()

        self.selector_window.bind("<FocusOut>", self.on_focus_out)

        self.background_color = self.selector_window.cget("bg")

        # Ajouter une frame principale avec padding
        self.frame = Frame(self.selector_window, bg=self.background_color)
        self.frame.grid(padx=15, pady=15)

        self.max_columns = 5  # Nombre de colonnes
        self.images_per_column = 4  # Nombre de groupes par colonne
        self.current_row = 0
        self.current_column = 0

        # Charger les images principales
        self.load_additional_images(self.frame, type="head")

        scrollable_frame = CTkScrollableFrame(self.selector_window, height=250)
        scrollable_frame.grid(row=1, column=0, pady=5, sticky="nsew")
        
        scrollable_frame.columnconfigure(0, weight=1)

        for i, _type in enumerate(["icons", "symbols", "char"]):
            additional_images_frame = Frame(scrollable_frame, bg=self.background_color)
            additional_images_frame.loaded = False
            additional_images_frame._type = _type
            
            # Ajouter un bouton pour afficher/masquer les images supplémentaires
            toggle_button = CTkButton(scrollable_frame, text="Afficher les images supplémentaires")
            toggle_button.configure(command=lambda frame=additional_images_frame, toggle_button=toggle_button: self.toggle_additional_images(frame, toggle_button))
            toggle_button.grid(row=i*2, column=0, pady=5)

            # Créer la frame pour les images supplémentaires (initialement cachées)
            additional_images_frame.grid(row=i*2+1, column=0, pady=1)
            additional_images_frame.grid_remove()  # Cacher la section par défaut

            # Charger les images supplémentaires
            # self.load_additional_images(additional_images_frame, type=_type)

    def on_focus_out(self, event):
        if not self.selector_window.focus_get():  # Vérifie si la fenêtre a perdu le focus
            self.selector_window.destroy()

    def load_additional_images(self, frame, type="head"):
        self.current_column = 0
        self.current_row = 0
        self.big_column = 0
        if type == "head":
            self.images_per_column_icons = 4
            self.images_per_row_icons = 3
            columns_group = [3, 6, 12, 9]
            
            for idx, i in enumerate(list(range(1, 19)) + [20]):
                # Chargement des images
                male_path = f"ressources\\img_overlay\\heads/{i}0_1.png"
                female_path = f"ressources\\img_overlay\\heads/{i}1_1.png"
                icon_path = f"ressources\\img_overlay\\icons/{i}0.png"

                image_male = load_image(male_path, (30, 30))
                image_female = load_image(female_path, (30, 30))
                image_icon = load_image(icon_path, (30, 30))

                # Création et positionnement des labels pour icône, mâle et femelle dans la frame supplémentaire
                self.create_image_labels_additionnel(frame, image_icon, icon_path, columns_group,  disposition="big")
                self.create_image_labels_additionnel(frame, image_male, icon_path, columns_group,  disposition="big")
                self.create_image_labels_additionnel(frame, image_female, icon_path, columns_group,  disposition="big")
        elif type == "icons":
            self.images_per_column_icons = 5 
            
            
            icons = [226, 227, 228, 218, 229, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 314, 315, 316, 317, 
                     401, 419, 404, 411, 422, 
                     1000, 405, 1001, 1002, 1003, 
                     318, 402, 
                     403, 406, 407, 408, 409, 410, 412, 413, 414, 415, 416, 417, 418, 420, 421, 423, 425, 426, 427, 
                     428, 429, 430, 433, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 449, 469, 900, 901, 902, 903, 
                     "phoenix"]
            
            columns_group = [1, 5, 6]
            columns_reset = [21]
            
            for idx, icon in enumerate(icons):
                # Chargement des images
                icon_path = f"ressources\\img_overlay\\icons/{icon}.png"
                image_icon = load_image(icon_path, (30, 30))

                # Création et positionnement des labels pour
                self.create_image_labels_additionnel(frame, image_icon, icon_path, columns_group, columns_reset)
        
        elif type == "symbols":
            self.images_per_column_icons = 14
            for idx, classe in enumerate(list(range(1, 19)) + [20]):
                # Chargement des images
                icon_path = f"ressources\\img_overlay\\symbols/symbol_{classe}.png"
                image_icon = load_image(icon_path, (35, 35))
                self.create_image_labels_additionnel(frame, image_icon, icon_path, disposition="horizontal")
                for i in range(2, 16):
                    if i%8==0:
                        continue
                    icon_path = f"ressources\\img_overlay\\heads/{classe}{i//8}_{i%8}.png"
                    image_icon = load_image(icon_path, (30, 30))
                    self.create_image_labels_additionnel(frame, image_icon, icon_path, disposition="horizontal")
                    
        elif type == "char":
            self.images_per_column_icons = 5
            self.images_per_row_icons = 4
            columns_group = [4, 8, 12]
            for idx, classe in enumerate(list(range(1, 19)) + [20]):
                for i in range(0, 2):
                    icon_path = f"ressources\\img_overlay\\char/{classe}_{i}.png"
                    image_icon = load_image(icon_path, (30, 30))
                    self.create_image_labels_additionnel(frame, image_icon, icon_path, columns_group, disposition="big")
                for i in range(0, 2):
                    icon_path = f"ressources\\img_overlay\\head_char/mini_{classe}_{i}.png"
                    image_icon = load_image(icon_path, (30, 30))
                    self.create_image_labels_additionnel(frame, image_icon, icon_path, columns_group, disposition="big")
                
    def create_image_labels_additionnel(self, parent_frame, image_icon, icon_path, columns_group=[], columns_reset=[], disposition="vertical"):
        # Création des labels pour l'icône, le mâle et la femelle
        label_icon = CTkLabel(parent_frame, image=image_icon, text="", compound="top")
        label_icon.image = image_icon
        padx = (26, 6) if self.current_column+self.big_column*self.images_per_row_icons in columns_group else (0, 6)
        label_icon.grid(column=self.current_column+self.big_column*self.images_per_row_icons, row=self.current_row, pady=5, padx=padx)

        label_icon.bind(
            "<Button-1>",
            lambda event, img_path=icon_path: self.update_character_image(img_path),
        )

        # Gérer le changement de colonne et de ligne
        if disposition == "vertical":
            self.current_row += 1
            if self.current_row >= self.images_per_column_icons or self.current_row+self.current_column*self.images_per_column_icons in columns_reset:
                self.current_row = 0
                self.current_column += 1
        elif disposition == "horizontal":
            self.current_column += 1
            if self.current_column >= self.images_per_column_icons or self.current_column in columns_reset:
                self.current_column = 0
                self.current_row += 1
        else:
            self.current_column += 1
            if self.current_column >= self.images_per_row_icons:
                self.current_row += 1
                self.current_column = 0
            if self.current_row >= self.images_per_column_icons:
                self.big_column += 1
                self.current_row = 0
                self.current_column = 0

        # Arrête si le nombre maximum de colonnes est atteint
        if self.current_column >= self.max_columns:
            return


    def toggle_additional_images(self, frame, toggle_button):
        """Afficher ou cacher la section des images supplémentaires."""
        
        if not frame.loaded:
            self.load_additional_images(frame, type=frame._type)
            frame.loaded = True
        
        if frame.winfo_ismapped():
            frame.grid_remove()  # Cacher les images supplémentaires
            toggle_button.configure(text="Afficher les images supplémentaires")
        else:
            frame.grid()  # Afficher les images supplémentaires
            toggle_button.configure(text="Masquer les images supplémentaires")

    def update_character_image(self, image_path):
        """Met à jour l'image du personnage dans l'interface principale."""
        self.dofus.image_path = image_path
        new_image = load_image(image_path, (30, 30))

        # Mettre à jour l'image dans l'interface principale
        self.image_label.configure(image=new_image)
        self.image_label.image = new_image  # Référence pour éviter suppression

        # Fermer la fenêtre de sélection
        self.selector_window.destroy()


def load_image(path, size, rotate=False):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    if rotate:
        img = img.rotate(180)  # Rotation de 180 degrés
    return CTkImage(img, size=size)


if __name__ == "__main__":
    import sys
    sys.path.append(r'd:\all\bot\python\pythondof\dofusOverlay_OP/')
    from srcOverlay.Page_Dofus import Page_Dofus
    
    pages_dofus = [Page_Dofus(1, ini=1), Page_Dofus(0, ini=2), Page_Dofus(4, ini=4)]
    pages_dofus[0].name = "test1"
    pages_dofus[1].classe = "feca"
    pages_dofus[1].name = "Indimo"
    pages_dofus[2].name = "Readix"
    ihm = ImageSelector(None, pages_dofus, None)
    ihm.selector_window.mainloop()
