import tkinter as tk
from PIL import Image, ImageTk

# Fonction pour dessiner un rectangle aux coins arrondis
def draw_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
    """Dessine un rectangle arrondi sur un Canvas."""
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
    return canvas.create_polygon(points, smooth=True, **kwargs)

# Initialisation de la fenêtre principale
root = tk.Tk()
root.title("Overlay")
root.geometry("100x200+1000+200")  # Dimensions de la fenêtre
root.configure(bg="red")  # Fond noir
root.wm_attributes("-transparentcolor", "red")
root.overrideredirect(True)  # Supprime la barre de titre
root.attributes('-topmost', True)

# Variable pour empêcher le drag en dehors des labels
root.is_dragging = False
root.able_to_drag = False

# Permet de déplacer la fenêtre avec la souris
def start_move(event):
    if root.able_to_drag:  
        root.is_dragging = True
        root.x = event.x
        root.y = event.y

def move_window(event):
    if root.is_dragging:  # Vérifie si un drag est permis
        x = root.winfo_x() + event.x - root.x
        y = root.winfo_y() + event.y - root.y
        root.geometry(f"+{x}+{y}")

def stop_move(event):
    root.is_dragging = False
    root.x = 0
    root.y = 0

root.bind("<Button-1>", start_move)
root.bind("<B1-Motion>", move_window)
root.bind('<ButtonRelease-1>', stop_move)

# Cadre principal avec Canvas
canvas = tk.Canvas(root, width=100, height=200, bg="red", highlightthickness=0)
canvas.pack()

# Dessiner un rectangle arrondi comme fond
draw_rounded_rectangle(canvas, 0, 0, 50, 100, 23, fill="black")

# Charger les images des avatars
def load_image(path, size):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)

# Images de démonstration (remplacez avec vos fichiers)
avatar1 = load_image("ressources\\img_overlay\\heads\\10_1.png", (30, 30))  # Remplacez "avatar1.png"
avatar2 = load_image("ressources\\img_overlay\\heads\\30_1.png", (30, 30))  # Remplacez "avatar2.png"

# Fonction pour dessiner un bouton arrondi sur un Canvas
def draw_rounded_button(canvas, x1, y1, x2, y2, radius, text, **kwargs):
    """Dessine un bouton arrondi avec du texte à l'intérieur sur un Canvas."""
    # Dessiner le rectangle arrondi
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
    button = canvas.create_polygon(points, smooth=True, **kwargs)
    
    # Ajouter le texte au centre du bouton
    canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, fill="white", font=("Arial", 12, "bold"))
    
    return button

# Dessiner le bouton arrondi
diameter = 22
offset = 12
btn_next = draw_rounded_button(canvas, 25 - offset, 10, 25 + diameter - offset, 10 + diameter, 25, ">", fill="gray")

# Si vous souhaitez l'utiliser avec des événements (clics, etc.),
# vous pouvez ajouter un gestionnaire d'événements sur le bouton comme ceci :
canvas.tag_bind(btn_next, "<Button-1>", lambda event: invert_avatars())  # Lors du clic sur "Next", inverse les avatars

# Positions des avatars
avatar_positions = {
    "avatar1": (17, 55),
    "avatar2": (17, 55+30+5),
}

# Avatar 1
label_avatar1 = tk.Label(root, image=avatar1, bg="black")
avatar1_window = canvas.create_window(*avatar_positions["avatar1"], window=label_avatar1)  # Positionné dans le Canvas

# Avatar 2
label_avatar2 = tk.Label(root, image=avatar2, bg="black")
avatar2_window = canvas.create_window(*avatar_positions["avatar2"], window=label_avatar2)  # Positionné dans le Canvas

# Fonction pour inverser les positions des avatars
def invert_avatars():
    print("Inversion des avatars")
    
    # Récupérer les positions actuelles des avatars
    pos_avatar1 = avatar_positions["avatar1"]
    pos_avatar2 = avatar_positions["avatar2"]
    
    # Inverser les positions
    avatar_positions["avatar1"] = pos_avatar2
    avatar_positions["avatar2"] = pos_avatar1
    
    # Repositionner les avatars
    canvas.coords(avatar1_window, *avatar_positions["avatar1"])
    canvas.coords(avatar2_window, *avatar_positions["avatar2"])

# Dessiner un chevron initialement (par défaut hors écran)
def dessiner_chevron(canvas, x, y, taille, couleur):
    """Dessine un chevron `<` sur un Canvas."""
    # Points du chevron
    p1 = (x, y)  # Pointe du chevron
    p2 = (x + taille, y - taille)  # Sommet haut droit
    p3 = (x + taille, y + taille)  # Sommet bas droit
    
    # Dessiner les lignes du chevron
    return canvas.create_line(p1, p2, fill=couleur, smooth=True, width=3), canvas.create_line(p1, p3, fill=couleur, smooth=True, width=3)

chevrons = dessiner_chevron(canvas, 50, 70, 20, "white")

# Fonction pour déplacer le chevron vers l'avatar cliqué
def select_avatar(avatar_name):
    position = avatar_positions.get(avatar_name)
    if position:
        x, y = position
        # Coordonner les sommets du chevron (triangle orienté vers la droite)
        decal_x = 23
        len = 6
        
        points1 = [
            x + len + decal_x, y - len,       
            x + decal_x, y , 
        ]
        
        points2 = [
            x + len + decal_x, y + len,       
            x + decal_x, y    
        ]
        
        canvas.coords(chevrons[0], points1)  # Ajuster les coordonnées
        canvas.coords(chevrons[1], points2)  # Ajuster les coordonnées
        canvas.itemconfig(chevrons[0], state="normal")  # Rendre visible
        canvas.itemconfig(chevrons[1], state="normal")  # Rendre visible

# Désactiver le drag lorsque vous survolez ou cliquez sur un label
def disable_drag(event):
    root.able_to_drag = False  # Désactiver le drag en dehors des labels

def enable_drag(event):
    root.able_to_drag = True  # Réactiver le drag après avoir quitté les labels

# Associer les clics sur les avatars
label_avatar1.bind("<Button-1>", lambda event: select_avatar("avatar1"))
label_avatar1.bind("<Enter>", disable_drag)  # Désactiver le drag au survol
label_avatar1.bind("<Leave>", enable_drag)  # Réactiver le drag après avoir quitté

label_avatar2.bind("<Button-1>", lambda event: select_avatar("avatar2"))
label_avatar2.bind("<Enter>", disable_drag)  # Désactiver le drag au survol
label_avatar2.bind("<Leave>", enable_drag)  # Réactiver le drag après avoir quitté

# Lancement de la boucle principale
root.mainloop()
