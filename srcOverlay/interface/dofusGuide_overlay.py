import sys
sys.path.append(r'd:\all\bot\python\pythondof\dofusOverlay_OP/')
from srcOverlay.interface.overlay import Overlay
from srcOverlay.interface.reorganiser import Reorganiser

from threading import RLock
import tkinter as tk
from tkinter import font
from PIL import Image,ImageTk


dict_head = {"feca":10, "osamodas":20, "enutrof":30, "sram":40, "xelor":50, "ecaflip":60, "eniripsa":70, 
             "iop":80, "cra":90, "sadida":100, "sacrieur":110, "pandawa":120, "roublard":130, "zobal":140, 
             "steamer":150, "eliotrope":160, "huppermage":170, "ouginak":180, "forgelance":200}

class DofusGuideOverlay(Overlay):
    def __init__(self, config, order, open_dofus_methode=None, dh=None, width = 50, height = 400):
        Overlay.__init__(self, 25, 100, x=width, y=height, alpha=1)
        self.bind("<<Destroy>>", lambda e: self.destroy())
        
        self.width = width
        self.head_width = 25
        self.background_color = "#1b1a1d"
        
        self.configure(bg="red")  # Fond noir
        self.wm_attributes("-transparentcolor", "red")
        
        self.is_dragging = False
        self.able_to_drag = True
        
        self.dragging_index = None  # Indice de l'image en cours de drag
        self.drag_image = None  # Référence à l'image temporaire
                
        self.perso = dict()
        self.order = []
        self.hwnds = []
        
        
        self.lock = RLock()
        self.config_json = config
        
        self.reorganise = None
        
        self.canvas = tk.Canvas(self, width=width, height=height, bg="red", highlightthickness=0)
        self.canvas.pack()
        
        self.rect_bg = draw_rounded_rectangle(self.canvas , 0, 0, width, height, 23, fill=self.background_color)
        
        # Dessiner le bouton arrondi
        btn_next = draw_rounded_button(self.canvas, width/2, 12+4, 11, ">", fill="gray", outline=self.background_color, width=1, font=(font.families()[20], 12, "bold"))
        self.canvas.tag_bind(btn_next[0], "<Button-1>", lambda e : self.open_reorganize(self.order))
        self.canvas.tag_bind(btn_next[1], "<Button-1>", lambda e : self.open_reorganize(self.order))
        
        self.canvas.tag_bind(btn_next[0], "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(btn_next[0], "<Leave>", lambda e: self.canvas.config(cursor=""))
        self.canvas.tag_bind(btn_next[1], "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
        self.canvas.tag_bind(btn_next[1], "<Leave>", lambda e: self.canvas.config(cursor=""))
        
        self.chevrons = dessiner_chevron(self.canvas, 50, 70)
        
        self.current_shown = 0
        
        self.is_visible = True
        
        self.open_dofus_methode=open_dofus_methode
        self.dh = dh
        
        self.update_order(order)
    
    def extend_button(self, *args):
        print("extend_button")
        self.update_order(self.order + self.order)

    def resize(self):
        h = self.get_position(len(self.order))[1]-15
        self.geometry(f"{self.width}x{h}")  # Redimensionner la fenêtre
        
        self.canvas.config(width=self.width, height=h)  # Mettre à jour les dimensions du Canvas
        self.canvas.coords(
            self.rect_bg,
            self.get_rounded_rectangle_coords(0, 0, self.width, h, 23)
        )
        pass
    
    def get_rounded_rectangle_coords(self, x1, y1, x2, y2, radius):
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
        self.lock.acquire()
        position = self.get_position(indice)
        
        if position:
            x, y = position
            # Coordonner les sommets du chevron (triangle orienté vers la droite)
            decal_x = 24
            
            points1 = [
                x + decal_x, y
            ]

            
            self.canvas.coords(self.chevrons, points1)  # Ajuster les coordonnées
            self.canvas.itemconfig(self.chevrons, state="normal")  # Rendre visible

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
        self.lock.release()
        
    def create_image(self, dofus, indice):
        path = self.config_json['img']['path2']+get_image_path(type=dofus.type, 
                                                                classe=dofus.classe, sexe=dofus.sexe, head=dofus.head)

        img = ImageTk.PhotoImage(Image.open(path).resize((self.head_width, self.head_width), Image.LANCZOS))
        
        label_avatar = tk.Label(self, image=img, bg=self.background_color)
        
        window_id = self.canvas.create_window(
            self.get_position(indice), window=label_avatar
        )
        
        label_avatar.bind("<Control-1>", lambda e, dofus=dofus : self.select_char(dofus))
        
        label_avatar.bind("<Enter>", lambda e, dofus=dofus : self.disable_drag(e, dofus))  # Désactiver le drag au survol
        label_avatar.bind("<Leave>", self.enable_drag)  # Réactiver le drag après avoir quitté
        
        label_avatar.bind("<ButtonPress-1>", lambda e, i=indice: self.start_drag(e, i, window_id))
        label_avatar.bind("<B1-Motion>", lambda e, dofus=dofus : self.drag(e, dofus))
        label_avatar.bind("<ButtonRelease-1>", lambda e: self.stop_drag(e))

        label_avatar.config(cursor="hand2")
        
        label_avatar.image = img
        label_avatar.window_id = window_id
        self.perso[dofus] = label_avatar
        
    def disable_drag(self, event, dofus):
        self.able_to_drag = False  # Désactiver le drag en dehors des labels
        self.perso[dofus].config(cursor="hand2")


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
        if self.is_valid_drop_zone(event.x, event.y):
            self.perso[dofus].config(cursor="hand2")  # Zone valide
        else:
            self.perso[dofus].config(cursor="no")  # Zone non valide

    def stop_drag(self, event):
        """Stoppe le drag et réorganise les images."""
        if self.dragging_index is not None:
            # Détecter la nouvelle position
            new_index = self.get_drop_index(event.y, self.dragging_index)
            if new_index is not None and new_index != self.dragging_index:
                # Réorganiser self.order
                moved_item = self.order[self.current_shown]
                self.order.insert(new_index, self.order.pop(self.dragging_index))
                
                for i, dofus in enumerate(self.order):
                    dofus.ini = len(self.order)-i
                    
                # Mettre à jour `self.current_shown` pour qu'il corresponde au nouvel index de l'élément affiché
                self.current_shown = self.order.index(moved_item)
                if self.dh:
                    self.dh.current_shown = self.current_shown

                self.update_order(self.order)  # Mettre à jour l'affichage avec le nouvel ordre

            # Réinitialiser les variables de drag
            self.dragging_index = None
            self.dragging_window_id = None
            self.canvas.config(cursor="hand2")

    def get_drop_index(self, mouse_y, current_index):
        """Détermine l'indice cible où l'image est déposée."""
        for i, _ in enumerate(self.order):
            x, y = self.get_position(i)
            if y <= mouse_y+int(self.get_position(current_index)[1]) <= y + self.head_width:
                return i
        # Si la souris est en dehors, retourner None ou l'indice final
        # if mouse_y > self.get_position(len(self.order) - 1)[1]:
        #     return len(self.order) - 1
        return None

    def is_valid_drop_zone(self, x, y):
        """Détermine si la position (x, y) est dans une zone valide."""
        # Par exemple, vérifier si la souris est dans un rectangle défini comme une zone valide
        return self.get_drop_index(y, self.dragging_index)!=None # and 17 <=x+int(self.get_position(self.dragging_index)[0]) <= 17+self.head_width
    
    def open_reorganize(self, order):
        self.order = order
        if not(self.reorganise) and self.dh:
            self.reorganise = Reorganiser(self.order, self, self.dh)
    
    def select_char(self, dofus):
        dofus.selected = not dofus.selected
        
        if dofus.selected:
            self.perso[dofus].config(background=self.background_color)
        else:
            self.perso[dofus].config(background="grey")
            
    def get_position(self, indice):
        return (17, 51+(self.head_width+10)*indice)
    
    def select(self, indice):
        if self.open_dofus_methode:
            self.open_dofus_methode(indice)
    


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
def load_image(path, size):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)


def draw_rounded_button(canvas, cx, cy, radius, text, font=("Arial", 12, "bold"), color="white", **kwargs):
    """
    Dessine un bouton rond avec du texte à l'intérieur sur un Canvas.

    :param canvas: Instance de Canvas où dessiner le bouton.
    :param cx: Coordonnée X du centre du cercle.
    :param cy: Coordonnée Y du centre du cercle.
    :param radius: Rayon du cercle.
    :param text: Texte à afficher au centre du bouton.
    :param font: Police utilisée pour le texte.
    :param kwargs: Autres arguments pour personnaliser l'apparence (e.g., fill, outline).
    """
    # Dessiner le cercle
    button = canvas.create_oval(
        cx - radius, cy - radius, cx + radius, cy + radius, **kwargs
    )
    
    # Ajouter le texte au centre du cercle
    txt_button = canvas.create_text(cx, cy, text=text, fill=color, font=font)
    
    return button, txt_button

def dessiner_chevron(canvas, x, y):
    """Dessine un chevron `<` sur un Canvas."""
    return canvas.create_text(x, y, text="<", fill="white", font=(font.families()[1], 12, "bold"), state="hidden")


def get_head_number(classe):
    if classe in dict_head:
        return str(dict_head[classe])
    return "10"

def get_image_path(type="head", classe="iop", sexe=0, head=1):
    prefixes_dict = {"head":"heads/", "icon":"icons/", "symbol":"symbols/symbol_", "head_char":"head_char/mini_",
               "char":"char/", "compagnon_char":"compagnon/big_", "compagnon":"compagnon/square_"}
    
    gender = 1 if sexe=="femelle" else 0
    classe = classe.lower()
    
    prefix=""
    sufix=""
    if type in prefixes_dict:
        prefix += prefixes_dict[type]
    
    if type=="head":
        if classe in dict_head:
            sufix = str(dict_head[classe]+gender)+"_"+str(head)+".png"
            
    elif type=="icon":
        if classe in dict_head:
            sufix = str(dict_head[classe])+".png"
    
    elif type=="symbol":
        sufix = str(int(dict_head[classe]/10))+".png"
        
    elif type=="head_char" or type=="char":
        sufix = f"{int(dict_head[classe]/10)}_{gender}.png"
        
    elif type=="compagnon_char" or type=="compagnon":
        sufix = f"{head}." + ("png" if type=="compagnon" else "jpg")
            
    if not sufix:
        prefix=""
        sufix="icons/1004.png"
    
    return prefix + sufix
    

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
        
    ihm = DofusGuideOverlay(config, pages_dofus)
    ihm.mainloop()