import sys
sys.path.append(r'd:\all\bot\python\pythondof\dofusOverlay_OP/')
from srcOverlay.interface.overlay import Overlay
from srcOverlay.interface.reorganiser import Reorganiser

from threading import RLock
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk

from customtkinter import CTkImage


import queue


dict_head = {"feca":10, "osamodas":20, "enutrof":30, "sram":40, "xelor":50, "ecaflip":60, "eniripsa":70, 
             "iop":80, "cra":90, "sadida":100, "sacrieur":110, "pandawa":120, "roublard":130, "zobal":140, 
             "steamer":150, "eliotrope":160, "huppermage":170, "ouginak":180, "forgelance":200}

class DofusGuideOverlay(Overlay):
    def __init__(self, config, order, open_dofus_methode=None, dh=None, head_width=25, orientation=0):
        width = 50
        height = 400
        
        Overlay.__init__(self, 25, 100, x=width, y=height, alpha=1)
        self.bind("<<Destroy>>", lambda e: self.destroy())
        
        self.height = height
        self.orientation = "horizontal" if orientation == 1 else "vertical"
        self.open_dofus_methode=open_dofus_methode
        self.dh = dh
        
        self.head_width = max(20, head_width)
        self.width = self.head_width + 25
        self.background_color = "#1b1a1d"
        self.configure(bg="red")  # Fond noir
        self.wm_attributes("-transparentcolor", "red")
        
        self.is_dragging = False
        self.able_to_drag = True
        self.dragging_index = None  # Indice de l'image en cours de drag
        self.drag_image = None  # Référence à l'image temporaire
        self.reorganise = None
        self.current_shown = 0
        self.is_visible = True
    
        self.perso = dict()
        self.order = []
        self.hwnds = []
        
        self.lock = RLock()
        self.config_json = config
        
        self.init_canvas()
        self.update_order(order)
        
        self.task_queue = queue.Queue()
        self.after(100, self.process_queue)
        
    def init_canvas(self):
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="red", highlightthickness=0)
        self.canvas.pack()
        
        self.rect_bg = draw_rounded_rectangle(self.canvas , 0, 0, self.width, self.height, 23, fill=self.background_color)
        
        
        if self.orientation == "vertical":
            x = self.width/2
            y = 12+4
        else :
            x = 12+4
            y = self.width/2
        self.btn_next = self.open_button_image(self.canvas, x, y, self.config_json['img']['path2']+"bouton.png", (20, 20))
        self.btn_next.bind("<Button-1>", lambda e : self.open_reorganize(self.order))
        
        self.btn_next.bind("<Enter>", lambda e, widget=self.btn_next: self.disable_drag(e, widget))  # Désactiver le drag au survol
        self.btn_next.bind("<Leave>", lambda e: self.enable_drag(e))  # Réactiver le drag après avoir quitté
        
        self.chevrons = dessiner_chevron(self.canvas, 50, 70, self.orientation, size=self.head_width/2)
        
    def process_queue(self):
        """Vérifie la file et exécute les tâches dans le thread principal."""
        while not self.task_queue.empty():
            task = self.task_queue.get()  # Récupérer une tâche
            task()  # Exécuter la tâche dans le thread principal
        # Replanifier la vérification de la file
        self.after(100, self.process_queue)


    def resize(self):
        if self.orientation == "horizontal":
            w = self.get_position(len(self.order))[0] - int(self.head_width/2)
            self.geometry(f"{w}x{self.width}")
            self.canvas.config(width=w, height=self.width)
            self.canvas.coords(
                self.rect_bg,
                get_rounded_rectangle_coords(0, 0, w, self.width, 23)
            )
        else:  # Orientation verticale
            h = self.get_position(len(self.order))[1] - int(self.head_width/2)
            self.geometry(f"{self.width}x{h}")
            self.canvas.config(width=self.width, height=h)
            self.canvas.coords(
                self.rect_bg,
                get_rounded_rectangle_coords(0, 0, self.width, h, 23)
            )
    
        
    def dragwin(self, event):
        if self.is_dragging:  # Vérifie si un drag est permis
            deltax = event.x - self._offsetx
            deltay = event.y - self._offsety
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry('+{x}+{y}'.format(x=x,y=y))

    def clickwin(self, event):
        if self.able_to_drag:  
            self.is_dragging = True
            self._offsetx = event.x
            self._offsety = event.y
            
    def stop_move(self, event):
        self.is_dragging = False
        self.x = 0
        self.y = 0
        
    def stop(self):
        self.event_generate("<<Destroy>>", when="tail")
    
    def getHwnd(self):        
        if self.reorganise:
            return [int(self.frame(),base=16), int(self.reorganise.frame(),base=16)]
        return [int(self.frame(),base=16)]
    
    def update_perso(self, indice):
        with self.lock:
            position = self.get_position(indice)
            
            if self.orientation == "vertical":
                if position:
                    x, y = position
                    # Coordonner les sommets du chevron (triangle orienté vers la droite)
                    decal_x = self.head_width/2 +12
                    
                    points1 = [
                        x + decal_x, y
                    ]
                    

            else:
                if position:
                    x, y = position
                    # Coordonner les sommets du chevron (triangle orienté vers le bas)
                    decal_y = self.head_width/2 +12
                    
                    points1 = [
                        x, y + decal_y
                    ]

            self.canvas.coords(self.chevrons, points1)  # Ajuster les coordonnées
            self.canvas.itemconfig(self.chevrons, state="normal")  # Rendre visible

            self.current_shown = indice
        
    def update_visibility(self, hwnd):
        with self.lock:
            if hwnd in self.hwnds+self.getHwnd():
                if not self.is_visible:
                    self.deiconify()
                    self.is_visible = True
            
            elif self.is_visible:
                self.withdraw()
                self.is_visible = False

    def update_order(self, order):
        with self.lock:
            self.order = order
            self.hwnds = [d.hwnd for d in order]
                
            # Supprimer toutes les images existantes du canvas
            # for i, dofus in enumerate(self.order):
            #     if dofus in self.perso:
            #         label_avatar = self.perso[dofus]
            #         if label_avatar.window_id !=i:
            #             # if hasattr(label_avatar, "window_id"):  # Vérifier si l'attribut existe
            #             self.canvas.delete(label_avatar.window_id)  # Supprimer l'objet Canvas
            #             label_avatar.destroy()  # Détruire le widget associé
            # # self.perso.clear()

            # for i, dofus in enumerate(order):
            #     if dofus in self.perso:
            #         label_avatar = self.perso[dofus]
            #         if label_avatar.window_id !=i:
            #             self.create_image(dofus, i)  # Recrée un nouvel avatar pour chaque élément
            #     else:
            #         self.create_image(dofus, i)
                    
            for i, dofus in enumerate(order):
                self.create_image(dofus, i)
            
            self.update_perso(self.current_shown)
            self.resize()
        
    def create_image(self, dofus, indice):
        if dofus.image_path:
            path = dofus.image_path
        else:
            path = self.config_json['img']['path2']+get_image_path(classe=dofus.classe)
            dofus.image_path = path
            
        img = load_image(path, (self.head_width, self.head_width))
        
        label_avatar = tk.Label(self, image=img, bg=self.background_color)
        
        window_id = self.canvas.create_window(
            self.get_position(indice), window=label_avatar
        )
        
        label_avatar.image = img
        label_avatar.window_id = window_id
        self.perso[dofus] = label_avatar
        
        label_avatar.bind("<Control-1>", lambda e, dofus=dofus : self.unselect_char(dofus))
        
        label_avatar.bind("<Enter>", lambda e, widget=self.perso[dofus] : self.disable_drag(e, widget))  # Désactiver le drag au survol
        label_avatar.bind("<Leave>", self.enable_drag)  # Réactiver le drag après avoir quitté
        
        label_avatar.bind("<ButtonPress-1>", lambda e, i=indice: self.start_drag(e, i, window_id))
        label_avatar.bind("<B1-Motion>", lambda e, dofus=dofus : self.drag(e, dofus))
        label_avatar.bind("<ButtonRelease-1>", lambda e: self.stop_drag(e))
        
        self.update_selected_status(dofus)

        label_avatar.config(cursor="hand2")
        
    def disable_drag(self, event, widget):
        self.able_to_drag = False  # Désactiver le drag en dehors des labels
        widget.config(cursor="hand2")


    def enable_drag(self, event):
        self.able_to_drag = True  # Réactiver le drag après avoir quitté les labels
        self.canvas.config(cursor="")
        
    def start_drag(self, event, index, window_id):
        """Commence le drag d'une image."""
        self.dragging_index = index
        self._offset_x = event.x
        self._offset_y = event.y
        self.canvas.config(cursor="hand2")
        self.select(index)

    def drag(self, event, dofus):
        """Déplace l'image en cours de drag."""
        # if self.drag_image is not None:
        if self.is_valid_drop_zone(event.x, event.y):
            self.perso[dofus].config(cursor="hand2")  # Zone valide
        else:
            self.perso[dofus].config(cursor="no")  # Zone non valide

    def stop_drag(self, event):
        """Stoppe le drag et réorganise les images."""
        if self.dragging_index is not None:
            # Détecter la nouvelle position selon l'orientation
            mouse_coord = event.x if self.orientation == "horizontal" else event.y
            new_index = self.get_drop_index(mouse_coord, self.dragging_index)

            if new_index is not None and new_index != self.dragging_index:
                # Réorganiser self.order
                moved_item = self.order[self.current_shown]
                self.order.insert(new_index, self.order.pop(self.dragging_index))
                
                # Réinitialiser les indices `ini` pour chaque élément
                for i, dofus in enumerate(self.order):
                    dofus.ini = len(self.order) - i
                
                # Mettre à jour `self.current_shown` pour correspondre au nouvel index
                self.current_shown = self.order.index(moved_item)
                if self.dh:
                    self.dh.current_shown = self.current_shown

                # Mettre à jour l'affichage avec le nouvel ordre
                self.update_order(self.order)

            # Réinitialiser les variables de drag
            self.dragging_index = None
            self.dragging_window_id = None
            self.canvas.config(cursor="hand2")


    def get_drop_index(self, mouse_coord, current_index):
        """Détermine l'indice cible où l'image est déposée, selon l'orientation."""
        for i, _ in enumerate(self.order):
            x, y = self.get_position(i)
            ref_coord = x if self.orientation == "horizontal" else y
            current_ref_coord = self.get_position(current_index)[0] if self.orientation == "horizontal" else self.get_position(current_index)[1]
            dimension = self.head_width

            if ref_coord <= mouse_coord + int(current_ref_coord) <= ref_coord + dimension:
                return i
        # Si la souris est en dehors, retourner None
        return None

    def is_valid_drop_zone(self, mouse_x, mouse_y):
        """Détermine si la position (mouse_x, mouse_y) est dans une zone valide."""
        if self.orientation == "horizontal":
            return self.get_drop_index(mouse_x, self.dragging_index) is not None
        else:
            return self.get_drop_index(mouse_y, self.dragging_index) is not None

    
    def open_reorganize(self, order):
        self.order = order
        
        if self.dh:
            if not(self.reorganise):
                self.reorganise = Reorganiser(self.order, self, self.dh)
            else:
                self.reorganise.actualise()
                self.reorganise.deiconify()
        else:
            print("reorganise already open")
            
    def ask_open_reorganize(self, order):
        self.task_queue.put(lambda order=order: self.open_reorganize(order))
    
    def unselect_char(self, dofus):
        dofus.selected = not dofus.selected
        
        self.update_selected_status(dofus)
    
    def ask_update_selected_status(self, dofus):
        self.task_queue.put(lambda dofus=dofus: self.update_selected_status(dofus))
    
    def update_selected_status(self, dofus):
        if dofus.selected:
            self.perso[dofus].config(background=self.background_color)
        else:
            self.perso[dofus].config(background="grey")
            
    def get_position(self, indice):
        if self.orientation == "horizontal":
            return (48 + int(self.head_width/2) + (self.head_width + 10) * indice, 5+self.head_width/2)  # Disposition en ligne
        else:  # Orientation verticale par défaut
            return (5+self.head_width/2, 39+int(self.head_width/2) + (self.head_width + 10) * indice)
    
    def select(self, indice):
        if self.open_dofus_methode:
            self.open_dofus_methode(indice)
            
    def open_button_image(self, canvas, x, y, path, size, **kwargs):
        img = load_image(path, size, rotate=0 if self.orientation == "vertical" else -90)
        # button = canvas.create_image(x, y, image=img)
        
        label_avatar = tk.Label(self, image=img, bg=self.background_color)
        
        canvas.create_window(
            (x, y), window=label_avatar
        )
        
        self.bouton_img = img
        
        return label_avatar
    


def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
    """Dessine un rectangle arrondi sur un Canvas et affiche les points en vert au-dessus."""
    points = [
        (x1 + radius, y1),
        (x2 - radius, y1),
        (x2, y1),
        (x2, y1 + radius),
        (x2, y2 - radius),
        (x2, y2),
        (x2 - radius, y2),
        (x1 + radius, y2),
        (x1, y2),
        (x1, y2 - radius),
        (x1, y1 + radius),
        (x1, y1),
    ]
    # Aplatir les tuples de points
    rect= canvas.create_polygon(points, smooth=True, **kwargs)
    
    # Afficher les points en vert au-dessus du rectangle
    # for point in points:
    #     canvas.create_oval(point[0] - 2, point[1] - 2, point[0] + 2, point[1] + 2, fill="green", outline="green")
    
    return rect

# Charger les images des avatars
def load_image(path, size, rotate=0):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    if rotate:
        img = img.rotate(rotate)  # Rotation de 180 degrés
    # return CTkImage(img, size=size)
    return ImageTk.PhotoImage(img)

def get_rounded_rectangle_coords(x1, y1, x2, y2, radius):
    """Retourne les points pour ajuster un rectangle arrondi."""
    points = [
        (x1 + radius, y1),
        (x2 - radius, y1),
        (x2, y1),
        (x2, y1 + radius),
        (x2, y2 - radius),
        (x2, y2),
        (x2 - radius, y2),
        (x1 + radius, y2),
        (x1, y2),
        (x1, y2 - radius),
        (x1, y1 + radius),
        (x1, y1),
    ]
    return [coord for point in points for coord in point]  # Aplatir les tuples

def dessiner_chevron(canvas, x, y, orientation="vertical", size=12):
    """Dessine un chevron `<` sur un Canvas."""
    if orientation == "vertical":
        return canvas.create_text(x, y, text="<", fill="white", font=(font.families()[1], 12, "bold"), state="hidden")
    else:
        return canvas.create_text(x, y, text="^", fill="white", font=(font.families()[1], 12, "bold"), state="hidden")

def get_image_path(classe="iop"):
    if classe.lower() in dict_head:
        return f"heads/{dict_head[classe.lower()]}_1.png"
    return "icons/1004.png"
    

if __name__ == "__main__":
    import json
    from srcOverlay.Page_Dofus import Page_Dofus
    
    pages_dofus = [Page_Dofus(1, ini=1), Page_Dofus(0, ini=2), Page_Dofus(4, ini=4)]
    pages_dofus[0].name = "test1"
    pages_dofus[0].classe = "iop"
    pages_dofus[1].name = "Indimo"
    pages_dofus[1].classe = "cra"
    pages_dofus[2].name = "Readix"
    
    with open("ressources/config.json",encoding="utf-8") as file:
        config = json.load(file)
        
    ihm = DofusGuideOverlay(config, pages_dofus, orientation=0)
    # ihm = DofusGuideOverlay(config, pages_dofus, orientation="vertical")
    ihm.mainloop()