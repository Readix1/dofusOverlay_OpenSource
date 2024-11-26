import tkinter as tk
from PIL import Image, ImageTk
from tkinter import Tk, font

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
root.geometry("100x800+1000+200")  # Dimensions de la fenêtre
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
canvas = tk.Canvas(root, width=100, height=800, bg="red", highlightthickness=0)
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
def draw_rounded_button(canvas, x1, y1, x2, y2, radius, text, font=("Arial", 12, "bold"), **kwargs):
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
    canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=text, fill="white", font=font)
    
    return button

# Dessiner le bouton arrondi
diameter = 22
offset = 12
for i, ft in enumerate(font.families()[20:40]):
    btn_next = draw_rounded_button(canvas, 25 - offset, 10+i*diameter, 25 + diameter - offset, 10 + diameter+i*diameter, 25, ">", fill="gray", font=(ft, 12, "bold"))

# Si vous souhaitez l'utiliser avec des événements (clics, etc.),
# vous pouvez ajouter un gestionnaire d'événements sur le bouton comme ceci :

# Lancement de la boucle principale
root.mainloop()
