import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.font as tkfont
import tkinter.scrolledtext as st
import numpy as np
import random
from PIL import Image, ImageTk
from screeninfo import get_monitors

# ================================================================
# Hauptspielbrett - Setup
# ================================================================

scale = 1

# Farben
colors = [
    ["yellow", "#9e9c2b", "#eeec78"],
    ["blue", "#4647a5", "#abadff"],
    ["orange", "#aa7424", "#ffc267"],
    ["green", "#309e2d", "#71ff6c"],
    ["purple", "#9b2895", "#fc7ef5"]
]

nw = "nw"
rh = "rh"
pm = "pm"
zw = "zw"
p1 = "p1"

color_bg = "#e9e8e8"
color_header = "#706d6d"
color_field = "#ebe8e8"

# Automatische Spielfeldgröße
root = tk.Tk()
root.title("RandomCleverGame v1.0.0")

available_fonts = tkfont.families()

if "helvetica" in available_fonts:
    fonttype = "helvetica"
else:
    fonttype = "Consolas"

# Berechnung der Monitor-Auflösung des Hauptbildschirms
primary_monitor = next(m for m in get_monitors() if m.is_primary)
screen_width = primary_monitor.width
screen_height = primary_monitor.height

# Festlegung der Spielfeldgröße
if screen_height < screen_width:
    game_height = int(8/10 * screen_height * scale)
    game_width = int(game_height)
    board_width = int(2/3 * game_height)
else:
    game_width = int(8/10 * screen_width * scale)
    game_height = int(game_width)
    board_width = int(2/3 * game_height)

# Schriftgröße definieren
fontsize_large = int(game_width * 0.018)
fontsize_midlarge = int(game_width * 0.0165)
fontsize_mid = int(game_width * 0.015)
fontsize_small = int(game_width * 0.012)
icon_size = int(fontsize_mid*1.8)
font_large = (fonttype, fontsize_large)
font_midlarge = (fonttype, fontsize_midlarge)
font_mid = (fonttype, fontsize_mid)
font_small = (fonttype, fontsize_small)

# Icons laden
icons = {"nw": ImageTk.PhotoImage(Image.open("icons/nw.png").resize((icon_size, icon_size))),
         "rh": ImageTk.PhotoImage(Image.open("icons/rh.png").resize((icon_size, icon_size))),
         "pm": ImageTk.PhotoImage(Image.open("icons/pm.png").resize((icon_size, icon_size))),
         "zw": ImageTk.PhotoImage(Image.open("icons/zw.png").resize((icon_size, icon_size))),
         "p1": ImageTk.PhotoImage(Image.open("icons/p1.png").resize((icon_size, icon_size))),
         "fuchs": ImageTk.PhotoImage(Image.open("icons/fuchs.png").resize((icon_size, icon_size))),
         "q": ImageTk.PhotoImage(Image.open("icons/q.png").resize((icon_size, icon_size))),
         "2player": ImageTk.PhotoImage(Image.open("icons/2player.png").resize((icon_size, icon_size))),
         "3player": ImageTk.PhotoImage(Image.open("icons/3player.png").resize((icon_size, icon_size))),
         "B": ImageTk.PhotoImage(Image.open("icons/B.png").resize((icon_size, icon_size))),
         "arrow": ImageTk.PhotoImage(Image.open("icons/arrow.png").resize((icon_size, icon_size))),
         "le": ImageTk.PhotoImage(Image.open("icons/le.png").resize((icon_size, icon_size))),
         "re": ImageTk.PhotoImage(Image.open("icons/re.png").resize((icon_size, icon_size))),
         "minus": ImageTk.PhotoImage(Image.open("icons/minus.png").resize((icon_size, icon_size))),
         "leq": ImageTk.PhotoImage(Image.open("icons/leq.png").resize((icon_size, icon_size))),
         "req": ImageTk.PhotoImage(Image.open("icons/req.png").resize((icon_size, icon_size)))}

# Erzeugung des Hauptfensters
canvas = tk.Canvas(root, width=game_width, height=game_height, bg=color_bg)
canvas.pack(side="left")
label = tk.Label(root, text="X: 0, Y: 0", bg="yellow", font=font_large)
label.place(relx=1.0, rely=0.0, anchor='ne')

# Globale Variablen
boni_symbols = [nw, rh, pm, zw, p1]
boni_colors = np.array(colors)[:,0]
black_boni_on_field = []
black_boni_tmp = []
game_history = []
field0_x = None
field1_x = None
field2_x = None
field3_x = None
field4_x = None
w_ = 0.02*board_width
v_ = w_/2

# ================================================================
# Verlauf
# ================================================================

# Erstelle Textfeld für den Verlauf
history_box = st.ScrolledText(root, width=25, height=9 ,font=font_mid, background=color_bg, borderwidth=0, highlightthickness=0)
history_box.place(relx=1, rely=1, anchor='se')
history_box.configure(state="disabled") # Nur lesbar

# Zuordnung von Tags/Präfixen zu lesbaren Bezeichnungen im Verlauf
boni_field_map = {
        "rundenfelder": "Runde",
        "fuchs": "Fuchs",
        "yellow": "Bonus gelb",
        "blue": "Bonus blau",
        "orange": "Bonus orange",
        "green": "Bonus grün",
        "purple": "Bonus lila",
        "black": "Bonus schwarz",
        "nw": "Neuwürfler",
        "rh": "Rückholer",
        "pm": "Plus-Minus 1",
        "zw": "Zauberwürfel",
        "p1": "Plus 1"
    }

def get_field_name(tag):
    if not tag:
        return "unbekanntes Feld"

    dynamic_field_map = {
            "field0": f"Feld {farben[0]}",
            "field1": f"Feld {farben[1]}",
            "field2": f"Feld {farben[2]}",
            "field3": f"Feld {farben[3]}",
            "field4": f"Feld {farben[4]}",
        }
    for prefix, name in dynamic_field_map.items():
        if tag.startswith(prefix):
            return name

    # Statische Zuordnung für Elemente
    for prefix, name in boni_field_map.items():
        if tag.startswith(prefix):
            return name
        
    return tag

def update_history_display():
    history_box.configure(state="normal") # entsperren
    history_box.delete('1.0', tk.END)
    history_box.insert(tk.INSERT, "--- VERLAUF ---\n")
    
    # Zeige nur die letzten 10 Aktionen an
    for i, move in enumerate(game_history):
        raw_field = move.get('field', 'unbekannt')
        field_name = get_field_name(raw_field)
        #display_text = f"{i+1}: {move['type']}, {field_name}, {np.round(move["coords"],0)}"
        display_text = f"{i+1}: {move['type']}, {field_name}"
        history_box.insert(tk.INSERT, display_text + "\n")
    
    history_box.configure(state="disabled") # sperren
    history_box.see(tk.END) # Automatisch nach unten scrollen

# ================================================================
# Klassen
# ================================================================

class Spielfeld:

    def __init__(self, breite, höhe, x0y0):
        """
        breite: (float) Feld-Breite
        höhe:   (float) Feld-Höhe
        x0y0:   (tuple) Koordinaten Ecke oben links (x0, y0)
        """
        self.breite = breite
        self.höhe = höhe
        self.x0y0 = x0y0
    
    def x1y1(self):
        """ berechnet Koordinaten (x1,y1) anhand von Breite und Höhe"""
        x1 = self.x0y0[0] + self.breite
        y1 = self.x0y0[1] + self.höhe
        return (x1, y1)
    
    def cells(self, n_y, n_x, dx0y0=None, dx1y1=None):
        """ Hilffunktion für Schleifen """
        x0, y0 = self.x0y0
        x1, y1 = self.x1y1()
        # Verschiebung
        if dx0y0 is not None:
            x0 = x0 + dx0y0[0]
            y0 = y0 + dx0y0[1]
        if dx1y1 is not None:
            x1 = x1 + dx1y1[0]
            y1 = y1 + dx1y1[1]
        total_width = abs(x1 - x0)
        total_height = abs(y1 - y0)
        cellsize_x = total_width / n_x
        cellsize_y = total_height / n_y
        x0_range = np.linspace(x0, x1, n_x, endpoint=False)
        y0_range = np.linspace(y0, y1, n_y, endpoint=False)
        return x0_range, y0_range, cellsize_x, cellsize_y
    
    def rectangles(self, n_y, n_x, colors_0, offset=0, colors_1="white", version_tag=None, dx0y0=None, dx1y1=None, stepXY=(1,1), dxy=(0,0), gap=0, grid=None, grid_no_tag=True, grid_del=False, grid_color=None, **options):
        """ 
        n_y, n_x:           (int) Anzahl an Zeilen und Spalten
        colors_0, colors_1: (str) Farben von Außen nach Innen
        offset:             (float) Randbreite
        version_tag:        (str) Tag-Stamm tkinter
        dx0y0, dx1y1:       (tupel) Koordinaten im Bezug auf (x0, y0) und (x1, y1)
        stepXY:             (tupel) steps innerhalb der For-Schleife (stepX, stepY)
        dxy:                (tupel) Verschiebung der ersten Zelle um (x,y)
        gap:                (float) Abstand zwischen Kästchen
        grid:               (2D-numpy-array) mit shape des Spielfeldes
            grid_no_tag:        (bool) Felder mit einem "X" oder "" erhalten kein Tag
            grid_del:           (bool) die Felder mit "X" oder "" werden nicht erzeugt
            grid_color:         (str) die Felder werden jetzt in der Farbe color erstellt
        """
        x0_range, y0_range, cellsize_x, cellsize_y = self.cells(n_y, n_x, dx0y0, dx1y1)

        if np.isscalar(colors_0):
            colors0 = np.full((n_y, n_x), colors_0)
        else:
            colors0 = colors_0
        
        if np.isscalar(colors_1):
            colors1 = np.full((n_y, n_x), colors_1)
        else:
            colors1 = colors_1

        for i in range(0, len(x0_range), stepXY[0]):
            x = x0_range[i]
            for j in range(0, len(y0_range), stepXY[1]):
                y = y0_range[j]

                # Tags vergeben
                if version_tag is not None:
                    tag_str0 = f"{version_tag}_{j}_{i}"
                    tag_str1 = str(version_tag)
                    tags = (tag_str0, tag_str1)
                elif colors0[j][i]=="red":
                    tags = "fuchs"
                elif colors0[j][i]=="black":
                    tags = "black"
                elif colors0[j][i] in boni_colors:
                    tags = str(colors0[j][i])
                else:
                    tags = None
                
                # grid
                if (grid is not None) and grid[j][i] in ["X", ""]:
                    if grid_del:
                        continue
                    if grid_no_tag:
                        tags = None
                    if grid_color is not None:
                        colors0[j][i] = grid_color
                       
                # Felder erstellen
                if offset == 0:
                    canvas.create_rectangle(x+dxy[0]+gap, y+dxy[1]+gap, x+cellsize_x+dxy[0]-gap, y+cellsize_y+dxy[1]-gap, fill=colors0[j][i], tags=tags, **options)
                else:
                    canvas.create_rectangle(x+dxy[0]+gap, y+dxy[1]+gap, x+cellsize_x+dxy[0]-gap, y+cellsize_y+dxy[1]-gap, fill=colors0[j][i], **options)
                    canvas.create_rectangle(x+offset+dxy[0]+gap, y+offset+dxy[1]+gap, x+cellsize_x-offset+dxy[0]-gap, y+cellsize_y-offset+dxy[1]-gap, fill=colors1[j][i], tags=tags, **options)
                
                # Füchse
                if tags == "fuchs":
                    img = icons["fuchs"]
                    canvas.create_image(x+cellsize_x/2+dxy[0], y+cellsize_y/2+dxy[1], image=img)
  
                # Schwarze Felder
                if colors0[j][i]=="black":
                    symbol = black_boni_tmp[0]
                    if symbol == nw:
                        img = icons["nw"]
                    elif symbol == rh:
                        img = icons["rh"]
                    elif symbol == zw:
                        img = icons["zw"]
                    elif symbol == pm:
                        img = icons["pm"]
                    elif symbol == p1:
                        img = icons["p1"]
                    # Schwarzen Boni der Sammelliste hinzufügen
                    black_boni_on_field.append(symbol)
                    canvas.create_image(x+cellsize_x/2+dxy[0], y+cellsize_y/2+dxy[1], image=img)

                    # Schwarzen Boni aus der tmp-Liste entfernen
                    black_boni_tmp.pop(0)

                # Zufälliges Bonusfeld im Kopf
                if (version_tag in ["nw", "rh", "zw", "pm", "p1"]) and (i == n_x-2) and (n_x > 2):
                    boni = shuffle(boni_colors, 1)[0]
                    canvas.create_rectangle(x+offset+dxy[0]+gap, y+offset+dxy[1]+gap, x+cellsize_x-offset+dxy[0]-gap, y+cellsize_y-offset+dxy[1]-gap, fill=boni, tags=boni, **options)

    def ovals(self, n_y, n_x, bg_colors, dx0y0=None, dx1y1=None, stepXY=(1,1), dxy=(0,0), gap=0, **options):
        """ analog zu rectangles"""
        x0_range, y0_range, cellsize_x, cellsize_y = self.cells(n_y, n_x, dx0y0, dx1y1)

        if np.isscalar(bg_colors):
            colors = np.full((n_y, n_x), bg_colors)
        else:
            colors = bg_colors
        
        for i in range(0, len(x0_range), stepXY[0]):
            x = x0_range[i]
            for j in range(0, len(y0_range), stepXY[1]):
                y = y0_range[j]
                canvas.create_oval(x+dxy[0]+gap, y+dxy[1]+gap, x+cellsize_x+dxy[0]-gap, y+cellsize_y+dxy[1]-gap, fill=colors[j][i], **options)

    def text(self, n_y, n_x, text_mat, dx0y0=None, dx1y1=None, stepXY=(1,1), dxy=(0,0), **options):
        """ analog zu rectangles """
        x0_range, y0_range, cellsize_x, cellsize_y = self.cells(n_y, n_x, dx0y0, dx1y1)
        
        for i in range(0, len(x0_range), stepXY[0]):
            x = x0_range[i]
            for j in range(0, len(y0_range), stepXY[1]):
                y = y0_range[j]
                canvas.create_text(x+cellsize_x/2+dxy[0], y+cellsize_y/2+dxy[1], text=text_mat[j][i], **options)

    def images(self, n_y, n_x, image_mat, dx0y0=None, dx1y1=None, stepXY=(1,1), dxy=(0,0), **options):
        x0_range, y0_range, cellsize_x, cellsize_y = self.cells(n_y, n_x, dx0y0, dx1y1)

        for i in range(0, len(x0_range), stepXY[0]):
            x = x0_range[i]
            for j in range(0, len(y0_range), stepXY[1]):
                y = y0_range[j]
                img = image_mat[j][i]
                if img is not None:
                    canvas.create_image(x + cellsize_x/2 + dxy[0], y + cellsize_y/2 + dxy[1], image=img, **options)

class Versionen(Spielfeld):
    """ Spielfeld - Unterklasse """
    def __init__(self, spielfeld_, version_tag, farbe=None, version=None, n_y=None, n_x=None):
        # Eigenschaften von spielfeld_
        self.breite = spielfeld_.breite
        self.höhe = spielfeld_.höhe
        self.x0y0 = spielfeld_.x0y0
        # Neue Eigenschaften
        self.farbe = farbe # Farbe des Spielfeldes, z.B "Gelb"
        self.version = version # Version des Spielfeldes, z.B "Clever_1", "Clever_1_c"
        self.n_y = n_y # Anzahl variabler Spalten
        self.n_x = n_x # Anzahl variabler Reihen
        self.dx0y0 = (0, 0)
        self.dx1y1 = (0, 0)
        self.tags = version_tag # legt Tags des Interaktionsgitters fest
        self.punkte_funktion = lambda stats: 0 # Standard: Feld gibt keine Punkte

        # Dynamisch die Methode mit gleichen Namen wie Tag aufrufen: 
        method = getattr(self, version_tag, None)
        if callable(method):
            method()
        """
        getattr nimmt den String und gibt die Methode zurück, falls die Methode nicht existiert, wird None zurückgegeben
        callable prüft, ob die Methode aufrufbar ist
        """
    
    def rundenfelder(self):
        """ Rundenfelder 1 bis 6 """

        n_y, n_x = 1, 6
        boni_list = [[1, 2, 3, 4, 5, 6]]
        boni_list2 = [["nw",None,"p1",None,"B",None,"q",None,"3player",None,"2player"]]
        boni_images2 = [[icons[item] if item is not None else None for item in boni_list2[0]]]
        a = self.breite/12
        super().rectangles(n_y, n_x, color_bg, version_tag=self.tags, dx0y0=(a, w_), dx1y1=(-a, -w_))
        super().text(n_y, n_x, boni_list, dx0y0=(a, w_), dx1y1=(-a, -w_), font=font_large)
        dx = (self.breite-2*a)/(4*n_x)
        super().rectangles(n_y, n_x*2, colors_0="#000000", dx0y0=(a, self.höhe/2+w_), dx1y1=(-a, -w_/2), stepXY=(2,1), dxy=(dx,0))
        super().images(n_y, n_x*2, boni_images2, dx0y0=(a, self.höhe/2+w_), dx1y1=(-a, -w_/2), stepXY=(2,1), dxy=(dx,0))

    def bonifelder(self):
        """ alle Boni-Felder"""
        a = (self.höhe)/5
        
        nw = black_boni[boni_symbols[0]]
        super().rectangles(1, nw, colors_0=color_bg, dx0y0=(0, 0), dx1y1=(0, -4*a), version_tag="nw", offset=v_/2, colors_1=color_field)
        
        rh = black_boni[boni_symbols[1]]
        super().rectangles(1, rh, colors_0=color_bg, dx0y0=(0, a), dx1y1=(0, -3*a), version_tag="rh", offset=v_/2, colors_1=color_field)

        pm = black_boni[boni_symbols[2]]
        super().rectangles(1, pm, colors_0=color_bg, dx0y0=(0, 2*a), dx1y1=(0, -2*a), version_tag="pm", offset=v_/2,colors_1=color_field)

        zw = black_boni[boni_symbols[3]]
        super().rectangles(1, zw, colors_0=color_bg, dx0y0=(0, 3*a), dx1y1=(0, -a), version_tag="zw", offset=v_/2, colors_1=color_field)
        zwtext = ["3", "4", "5", "6", "?", "?", "?"]
        zwtext = shuffle(zwtext, zw)
        super().text(1, zw, [zwtext], dx0y0=(0, 3*a), dx1y1=(0, -a), font=font_large, fill="black")

        p1 = black_boni[boni_symbols[4]]
        super().rectangles(1, p1, colors_0=color_bg, dx0y0=(0, 4*a), dx1y1=(0, 0), version_tag="p1", offset=v_/2, colors_1=color_field)

    # -------------------------------

    def field0_c1(self):
        """ gelbes Feld """
        self.farbe = "Gelb"
        self.version = "C1"

        black_b = shuffle(boni_symbols, 1, add=[boni_symbols[4]])
        black_boni_tmp.extend(black_b)

        # Hintergrund
        super().rectangles(1, 1, colors[0][2], w_/2, colors[0][1])

        # Interaktionsfelder
        a = (self.breite-2*w_)/5
        numbers = list(range(1, 6+1)) * 2
        random.shuffle(numbers)
        grid = [[*numbers[:3], "X"],
                [*numbers[3:5], "X", numbers[5]],
                [numbers[6], "X", *numbers[7:9]],
                ["X", *numbers[9:]]]
        super().rectangles(4, 4, color_field, version_tag=self.tags, dx0y0=(w_, w_), dx1y1=(-a-w_, -a-w_), grid=grid, grid_color=colors[0][2])
        super().text(4, 4, grid, dx0y0=(w_, w_), dx1y1=(-a-w_, -a-w_), font=font_mid, fill="dimgrey")

        # Speichere Eigenschaften
        self.n_x = 4
        self.n_y = 4
        self.dx0y0 = (w_, w_)
        self.dx1y1 = (-a-w_, -a-w_)

        # Punkte
        text = [["17", "17", "17", "17"]]
        b = 4*a+1.5*w_
        super().ovals(1, 4, colors[0][2], dx0y0=(w_,b), dx1y1=(-a-w_,-w_), gap=w_/3)
        super().text(1, 4, text, dx0y0=(w_,b), dx1y1=(-a-w_,-w_), font=font_mid)

        # Boni
        b = 4*a+w_
        b_colors = np.vstack(shuffle(boni_colors, 5, ["black", "red"]))
        super().rectangles(5, 1, dx0y0=(b,w_), dx1y1=(-w_,-w_), colors_0=b_colors, gap=w_/2, dxy=(w_/4,0))   

        # Punktelogik
        def calc_points(stats):
            # stats ist das Dictionary, das get_stats(self) zurückgibt
            punkte_cols = stats["cols_cross"]
            punktewerte = [17, 17, 17, 17]

            punkte = 0
            for i in punkte_cols:
                if i == 3:
                    punkte = punkte + punktewerte[i]

            return punkte
        
        self.punkte_funktion = calc_points

    def field1_c1(self):
        """ blaues Feld """
        self.farbe = "Blau"
        self.version = "C1"

        black_b = shuffle(boni_symbols, 2, add=[boni_symbols[0],boni_symbols[4]])
        black_boni_tmp.extend(black_b)

        # Hintergrund
        super().rectangles(1,1, colors[1][2], w_/2, colors[1][1])

        # Interaktionsfelder
        a = (self.breite-2*w_)/5
        numbers = list(range(2, 12+1))
        random.shuffle(numbers)
        grid = [["", *numbers[:3]],
                [*numbers[3:7]],
                [*numbers[7:]]]
        super().rectangles(3, 4, color_field, version_tag=self.tags, dx0y0=(w_, w_+a), dx1y1=(-w_-a, -w_-a), grid=grid, grid_del=True)
        super().text(3, 4, grid, dx0y0=(w_, w_+a), dx1y1=(-w_-a, -w_-a), font=font_mid, fill="dimgrey")
        
        # Speichere Eigenschaften
        self.n_x = 4
        self.n_y = 3
        self.dx0y0 = (w_, w_+a)
        self.dx1y1 = (-w_-a, -w_-a)

        # Punkte
        text1 = [["1", "4", "8", "12", "20", "28", "36", "44", "52", "60", "68"]]
        text2 = [["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]]
        b = 4*a+1.5*w_
        super().ovals(1,11, colors[1][2], dx0y0=(w_,w_), dx1y1=(-w_, -b-a/2))
        super().text(1,11, text1, dx0y0=(w_,w_), dx1y1=(-w_, -b-a/2), font=font_small)
        super().rectangles(1,11, colors[1][2], dx0y0=(w_, a/2+w_), dx1y1=(-w_, -b-w_/4))
        super().text(1,11, text2, dx0y0=(w_, a/2+w_), dx1y1=(-w_, -b-w_/4), font=font_small)

        # Boni
        b = 4*a+w_
        b_colors = shuffle(boni_colors, 7, ["black", "black", "red"])
        b1_colors = np.vstack([*b_colors[:3]])
        b2_colors = [[*b_colors[3:]]]
        super().rectangles(3, 1, b1_colors, dx0y0=(b, w_+a), dx1y1=(-w_, -w_-a), gap=w_/2, dxy=(w_/4,0))
        super().rectangles(1, 4, b2_colors, dx0y0=(w_, b), dx1y1=(-w_-a, -w_), gap=w_/2, dxy=(0,w_/4))

        # Punktelogik
        def calc_points(stats):
            # stats ist das Dictionary, das get_stats(self) zurückgibt
            total_crosses = stats["total_crosses"]
            punktewerte = [0, 1, 4, 8, 12, 20, 28, 36, 44, 52, 60, 68]
            punkte = punktewerte[total_crosses]
            return punkte
        
        self.punkte_funktion = calc_points        

    def field2_c1(self):
        """ oranges Feld """
        self.farbe = "Orange"
        self.version = "C1"

        black_b = shuffle(boni_symbols, 2, add=[boni_symbols[0],boni_symbols[4]])
        black_boni_tmp.extend(black_b)

        a = (self.breite-2*w_)/12

        # Hintergrund und Pfeil
        super().rectangles(1,1, colors[2][2], w_/2, colors[2][1])
        super().rectangles(1,1, colors[2][2], dx0y0=(w_, 2*w_), dx1y1=(-11*a-w_, -2*w_), gap=0.75*w_)
        super().images(1,1, [[icons["arrow"]]], dx0y0=(w_, 2*w_), dx1y1=(-11*a-w_, -2*w_))

        # Interaktionsfelder
        empty = np.full((7,), "")
        multis = ["x2", "x2", "x2", "x3"]
        text = shuffle(empty, 11, add=multis, pref=["x2", "x3"])
        super().rectangles(1, 11, color_field, version_tag=self.tags, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_))
        super().text(1,11, [text], dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_), font=font_mid, fill="dimgrey")
        
        # Speichere Eigenschaften
        self.n_x = 11
        self.n_y = 1
        self.dx0y0 = (w_+a, 2*w_)
        self.dx1y1 = (-w_, -2*w_)

        # Boni
        b_colors = shuffle(boni_colors, 5, add=["red", "black", "black"])
        empty = np.full((6,), "")
        grid = [shuffle(empty, 11, add=b_colors, pref=["red"], sigma=1/10)]
        super().rectangles(1,11, grid, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_),  grid=grid, grid_del=True, grid_no_tag=False, gap=w_, dxy=(0,0.6*a))

        # Punktelogik
        def calc_points(stats):
            # stats ist das Dictionary, das get_stats(self) zurückgibt
            punkte = stats["total_num"]
            return punkte
        
        self.punkte_funktion = calc_points

    def field3_c1(self):
        """ grünes Feld """
        self.farbe = "Grün"
        self.version = "C1"

        black_b = shuffle(boni_symbols, 2, add=[boni_symbols[0],boni_symbols[4]])
        black_boni_tmp.extend(black_b)

        a = (self.breite-2*w_)/12

        # Hintergrund und Pfeil
        super().rectangles(1,1, colors[3][2], w_/2, colors[3][1])
        super().rectangles(1,1, colors[3][2], dx0y0=(w_, 2*w_), dx1y1=(-11*a-w_, -2*w_), gap=0.75*w_)
        super().images(1,1, [[icons["arrow"]]], dx0y0=(w_, 2*w_), dx1y1=(-11*a-w_, -2*w_))

        # Interaktionsfelder
        text = ["≥1", "≥2", "≥3", "≥4", "≥5", "≥1", "≥2", "≥3", "≥4", "≥5", "≥6"]
        super().rectangles(1, 11, color_field, version_tag=self.tags, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_))
        super().text(1,11, [text], dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_), font=("consolas", fontsize_mid), fill="dimgrey")
        
        # Speichere Eigenschaften
        self.n_x = 11
        self.n_y = 1
        self.dx0y0 = (w_+a, 2*w_)
        self.dx1y1 = (-w_, -2*w_)

        # Boni
        b_colors = shuffle(boni_colors, 5, add=["red", "black", "black"])
        empty = np.full((6,), "")
        grid = [shuffle(empty, 11, add=b_colors, pref=["red"], sigma=1/10)]
        super().rectangles(1,11, grid, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_),  grid=grid, grid_del=True, grid_no_tag=False, gap=w_, dxy=(0,0.6*a))

        # Punkte
        text = ["1", "4", "8", "12", "20", "28", "36", "44", "52", "60", "68"]
        super().ovals(1, 11, colors[3][2], dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_), dxy=(0,-0.6*a), gap=w_)
        super().text(1, 11, [text], dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_), dxy=(0,-0.6*a), font=font_small)

        # Punktelogik
        def calc_points(stats):
            # stats ist das Dictionary, das get_stats(self) zurückgibt
            total_crosses = stats["total_crosses"]
            punktewerte = [0, 1, 4, 8, 12, 20, 28, 36, 44, 52, 60, 68]
            punkte = punktewerte[total_crosses]
            return punkte
        
        self.punkte_funktion = calc_points 

    def field4_c1(self):
        """ lila Feld """
        self.farbe = "Lila"
        self.version = "C1"

        black_b = shuffle(boni_symbols, 4, add=[boni_symbols[0],boni_symbols[4]])
        black_boni_tmp.extend(black_b)
        
        a = (self.breite-2*w_)/12

        # Hintergrund und Pfeil
        super().rectangles(1,1, colors[4][2], w_/2, colors[4][1])
        super().rectangles(1,1, colors[4][2], dx0y0=(w_, 2*w_), dx1y1=(-11*a-w_, -2*w_), gap=0.75*w_)
        super().images(1,1, [[icons["arrow"]]], dx0y0=(w_, 2*w_), dx1y1=(-11*a-w_, -2*w_))

        # Interaktionsfelder
        super().rectangles(1, 11, color_field, version_tag=self.tags, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_))
        
        # Speichere Eigenschaften
        self.n_x = 11
        self.n_y = 1
        self.dx0y0 = (w_+a, 2*w_)
        self.dx1y1 = (-w_, -2*w_)

        # Boni
        b_colors = shuffle(boni_colors, 9, add=["red", "black", "black", "black", "black"])
        empty = np.full((6,), "")
        grid = [shuffle(empty, 11, add=b_colors, pref=["red"], sigma=1/10)]
        super().rectangles(1,11, grid, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_),  grid=grid, grid_del=True, grid_no_tag=False, gap=w_, dxy=(0,0.6*a))

        # Pfeile
        super().ovals(1, 10, colors[4][2], dx0y0=(w_+a, 2*w_), dx1y1=(-w_-a, -2*w_), dxy=(a/2,0), gap=w_)
        
        icon_mat = [[icons["re"] for i in range(10)]]
        super().images(1, 10, icon_mat, dx0y0=(w_+a, 2*w_), dx1y1=(-w_-a, -2*w_), dxy=(a/2,0))

        # Punktelogik
        def calc_points(stats):
            # stats ist das Dictionary, das get_stats(self) zurückgibt
            punkte = stats["total_num"]
            return punkte
        
        self.punkte_funktion = calc_points

    # -------------------------------

    def field0_c2(self):
        """ gelbes Feld """
        self.farbe = "Gelb"
        self.version = "C2"

        black_b = shuffle(boni_symbols, 3, add=[boni_symbols[0], boni_symbols[1], boni_symbols[4]])
        black_boni_tmp.extend(black_b)

        # Hintergrund
        super().rectangles(1, 1, colors[0][2], w_/2, colors[0][1])

        # Interaktionsfelder
        a = (self.breite-2*w_)/6
        numbers = [1, 2, 2, 3, 3, 4, 4, 5, 5, 6]
        random.shuffle(numbers)
        grid = [["", numbers[0], "", numbers[1]],
                [numbers[2], "", numbers[3], ""],
                ["", numbers[4], "", numbers[5]],
                [numbers[6], "", numbers[7], ""],
                ["", numbers[8], "", numbers[9]]]
        super().rectangles(5, 4, color_field, version_tag=self.tags, dx0y0=(a+w_, w_), dx1y1=(-a-w_, -a-w_), grid=grid, grid_color=colors[0][2])
        super().text(5, 4, grid, dx0y0=(a+w_, w_), dx1y1=(-a-w_, -a-w_), font=font_mid, fill="dimgrey")

        # Speichere Eigenschaften
        self.n_x = 4
        self.n_y = 5
        self.dx0y0 = (a+w_, w_)
        self.dx1y1 = (-a-w_, -a-w_)

        # Punkte
        text1 = np.transpose([["3", "10", "21", "36", "55", "75", "96", "118", "141", "165"]])
        text2 = np.transpose([["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]])
         
        b = 5*a+1.5*w_
        super().ovals(10, 1, colors[0][2], dx0y0=(w_/4, w_), dx1y1=(-b-a/2,-w_))
        super().text(10, 1, text1, dx0y0=(w_/4, w_), dx1y1=(-b-a/2,-w_), font=font_small)

        super().rectangles(10,1, colors[0][2], dx0y0=(w_+a/2-w_/4, w_), dx1y1=(-b+w_/4, -w_))
        super().text(10, 1, text2, dx0y0=(w_+a/2, w_), dx1y1=(-b-w_/4, -w_), font=font_small)

        # Boni
        b = 5*a+w_
        b_colors = shuffle(boni_colors, 9, add=["black", "black", "black", "red"])
        b_colors1 = np.vstack(b_colors[0:5])
        b_colors2 = [b_colors[5:]]
        super().rectangles(5, 1, dx0y0=(b,w_), dx1y1=(-w_,-w_-a), colors_0=b_colors1, gap=w_/2, dxy=(w_/4,0))
        super().rectangles(1, 4, dx0y0=(w_+a, b), dx1y1=(-a-w_ ,-w_), colors_0=b_colors2, gap=w_/2, dxy=(0, w_/4))

        # Punktelogik
        def calc_points(stats):
            # stats ist das Dictionary, das get_stats(self) zurückgibt
            total_crosses = stats["total_crosses"]
            punktewerte = [0, 3, 10, 21, 36, 55, 75, 96, 118, 141, 165]
            punkte = punktewerte[total_crosses]
            return punkte
        
        self.punkte_funktion = calc_points 

    def field1_c2(self):
        """ orangenes Feld """
        self.farbe = "Orange"
        self.version = "C2"

        black_b = shuffle(boni_symbols, 1, add=[boni_symbols[4]])
        black_boni_tmp.extend(black_b)

        # Hintergrund
        super().rectangles(1,1, colors[2][2], w_/2, colors[2][1])

        # Interaktionsfelder
        a = (self.breite-2*w_)/6
        numbers = ["1","2","3","4","5","6"]
        grid = [numbers,
                numbers,
                numbers,
                numbers]
        colorfields = [[colors[0][2]]*6,
                       [colors[1][2]]*6,
                       [colors[3][2]]*6,
                       [colors[4][2]]*6]
        super().rectangles(4, 6, colorfields, version_tag=self.tags, dx0y0=(w_, a+w_), dx1y1=(-w_, -a-w_))
        super().text(4, 6, grid, dx0y0=(w_, a+w_), dx1y1=(-w_, -a-w_), font=font_mid, fill="dimgrey")

        # Speichere Eigenschaften
        self.n_x = 6
        self.n_y = 4
        self.dx0y0 = (w_, a+w_)
        self.dx1y1 = (-w_, -a-w_)

        # Punkte
        text1 = [["2", "4", "7", "8", "16", "22"]]
        text2 = [["1", "2", "3", "4", "5", "6"]]

        b = 5*a+1.5*w_
        super().ovals(1, 6, colors[2][2], dx0y0=(w_, b-w_/2), dx1y1=(-w_, -w_-w_/2), gap=0.5*w_)
        super().text(1, 6, text1, dx0y0=(w_, b-w_/2), dx1y1=(-w_, -w_-w_/2), font=font_mid)

        super().rectangles(1, 6, colors[2][2], dx0y0=(w_, b+a/2-w_/4), dx1y1=(-w_, -w_+a/2-w_/4), gap=0.9*w_)
        super().text(1, 6, text2, dx0y0=(w_, b+a/2-w_/4), dx1y1=(-w_, -w_+a/2-w_/4), font=font_mid)

        # Boni
        b = 5*a+w_
        b_colors = [shuffle(boni_colors, 6, add=["black", "red"])]
        super().rectangles(1, 6, dx0y0=(w_, w_), dx1y1=(-w_, -b), colors_0=b_colors, gap=w_/2, dxy=(0 , -w_/4))

        # Punktelogik
        def calc_points(stats):
            punkte_rows = stats["rows_cross"]
            punktewerte = [0, 2, 4, 7, 8, 16, 22]

            punkte = 0
            for i in punkte_rows:
                punkte = punkte + punktewerte[i]

            return punkte

        self.punkte_funktion = calc_points

    def field1_c2_c(self):
        """ orangenes Feld """
        self.farbe = "Orange"
        self.version = "C2_C"

        black_b = shuffle(boni_symbols, 2, add=[boni_symbols[1], boni_symbols[4]])
        black_boni_tmp.extend(black_b)

        # Hintergrund
        super().rectangles(1,1, colors[2][2], w_/2, colors[2][1])

        # Interaktionsfelder
        a = (self.breite-2*w_)/7
        numbers = ["","1","2","3","4","5","6"]
        grid = [numbers,
                numbers,
                numbers,
                numbers]
        colorfields = [[colors[0][2]]*7,
                       [colors[1][2]]*7,
                       [colors[3][2]]*7,
                       [colors[4][2]]*7]
        super().rectangles(4, 7, colorfields, version_tag=self.tags, dx0y0=(w_, a+w_), dx1y1=(-w_, -a-w_))
        super().text(4, 7, grid, dx0y0=(w_, a+w_), dx1y1=(-w_, -a-w_), font=font_mid, fill="dimgrey")

        # Speichere Eigenschaften
        self.n_x = 7
        self.n_y = 4
        self.dx0y0 = (w_, a+w_)
        self.dx1y1 = (-w_, -a-w_)

        # Punkte
        text1 = [["2", "5", "9", "14", "20", "27", "35"]]
        text2 = [["1", "2", "3", "4", "5", "6", "7"]]

        b = 6*a+w_
        super().ovals(1, 7, colors[2][2], dx0y0=(w_, b-w_/2), dx1y1=(-w_, -w_-w_/2), gap=0.5*w_)
        super().text(1, 7, text1, dx0y0=(w_, b-w_/2), dx1y1=(-w_, -w_-w_/2), font=font_mid)

        super().rectangles(1, 7, colors[2][2], dx0y0=(w_, b+a/2-w_/4), dx1y1=(-w_, -w_+a/2-w_/4), gap=0.9*w_)
        super().text(1, 7, text2, dx0y0=(w_, b+a/2-w_/4), dx1y1=(-w_, -w_+a/2-w_/4), font=font_mid)

        # Boni
        b = 6*a+w_
        b_colors = [shuffle(boni_colors, 7, add=["black", "black", "red"])]
        super().rectangles(1, 7, dx0y0=(w_, w_), dx1y1=(-w_, -b), colors_0=b_colors, gap=w_/2, dxy=(0 , -w_/4))

        # Punktelogik
        def calc_points(stats):
            punkte_rows = stats["rows_cross"]
            punktewerte = [0, 2, 5, 9, 14, 20, 27, 35]

            punkte = 0
            for i in punkte_rows:
                punkte = punkte + punktewerte[i]

            return punkte

        self.punkte_funktion = calc_points

    def field2_c2(self):
        """ blaues Feld """
        self.farbe = "Blau"
        self.version = "C2"

        black_b = shuffle(boni_symbols, 4, add=[boni_symbols[0], boni_symbols[1], boni_symbols[4]])
        black_boni_tmp.extend(black_b)

        a = (self.breite-2*w_)/13

        # Hintergrund und Pfeil
        super().rectangles(1, 1, colors[1][2], w_/2, colors[1][1])
        super().rectangles(1, 1, colors[1][2], dx0y0=(w_, 2*w_), dx1y1=(-12*a-w_, -2*w_), gap=0.75*w_)
        super().images(1, 1, [[icons["arrow"]]], dx0y0=(w_, 2*w_), dx1y1=(-12*a-w_, -2*w_))

        # Interaktionsfelder
        super().rectangles(1, 12, color_field, version_tag=self.tags, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_))

        # Speichere Eigenschaften
        self.n_x = 12
        self.n_y = 1
        self.dx0y0 = (w_+a, 2*w_)
        self.dx1y1 = (-w_, -2*w_)

        # Boni
        b_colors = shuffle(boni_colors, 8, add=["red", "black", "black", "black", "black"])
        empty = np.full((4,), "")
        grid = [shuffle(empty, 12, add=b_colors, pref=["red"], sigma=1/10)]
        super().rectangles(1,12, grid, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_),  grid=grid, grid_del=True, grid_no_tag=False, gap=w_, dxy=(0,0.6*a))

        # Punkte
        text = ["1", "3", "6", "10", "15", "21", "28", "36", "45", "55", "66", "78"]
        super().ovals(1, 12, colors[1][2], dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_), dxy=(0, -0.6*a), gap=w_)
        super().text(1, 12, [text], dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_), dxy=(0,-0.6*a), font=font_small)

        # Pfeile
        super().ovals(1, 11, colors[1][2], dx0y0=(w_+a, 2*w_), dx1y1=(-w_-a, -2*w_), dxy=(a/2,0), gap=w_)

        icon_mat = [[icons["leq"] for i in range(11)]]
        super().images(1, 11, icon_mat, dx0y0=(w_+a, 2*w_), dx1y1=(-w_-a, -2*w_), dxy=(a/2,0))

        # Punktelogik
        def calc_points(stats):
            total_N_num = stats["total_N_num"]
            punktewerte = [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78]
            punkte = punktewerte[total_N_num]
            return punkte

        self.punkte_funktion = calc_points

    def field2_c2_c(self):
        """ blaues Feld """
        self.farbe = "Blau"
        self.version = "C2"

        black_b = shuffle(boni_symbols, 4, add=[boni_symbols[0], boni_symbols[1], boni_symbols[4]])
        black_boni_tmp.extend(black_b)

        a = (self.breite-2*w_)/13

        # Hintergrund und Pfeil
        super().rectangles(1, 1, colors[1][2], w_/2, colors[1][1])
        super().rectangles(1, 1, colors[1][2], dx0y0=(w_, 2*w_), dx1y1=(-12*a-w_, -2*w_), gap=0.75*w_)
        super().images(1, 1, [[icons["arrow"]]], dx0y0=(w_, 2*w_), dx1y1=(-12*a-w_, -2*w_))

        # Interaktionsfelder
        super().rectangles(1, 12, color_field, version_tag=self.tags, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_))

        # Speichere Eigenschaften
        self.n_x = 12
        self.n_y = 1
        self.dx0y0 = (w_+a, 2*w_)
        self.dx1y1 = (-w_, -2*w_)

        # Boni
        b_colors = shuffle(boni_colors, 8, add=["red", "black", "black", "black", "black"])
        empty = np.full((4,), "")
        grid = [shuffle(empty, 12, add=b_colors, pref=["red"], sigma=1/10)]
        super().rectangles(1,12, grid, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_),  grid=grid, grid_del=True, grid_no_tag=False, gap=w_, dxy=(0,0.6*a))

        # Punkte
        text = ["1", "3", "6", "10", "15", "21", "28", "36", "45", "55", "66", "78"]
        super().ovals(1, 12, colors[1][2], dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_), dxy=(0, -0.6*a), gap=w_)
        super().text(1, 12, [text], dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_), dxy=(0,-0.6*a), font=font_small)

        # Pfeile
        super().ovals(1, 11, colors[1][2], dx0y0=(w_+a, 2*w_), dx1y1=(-w_-a, -2*w_), dxy=(a/2,0), gap=w_)

        icon_mat = [[icons["req"] for i in range(11)]]
        super().images(1, 11, icon_mat, dx0y0=(w_+a, 2*w_), dx1y1=(-w_-a, -2*w_), dxy=(a/2,0))

        # Punktelogik
        def calc_points(stats):
            total_N_num = stats["total_N_num"]
            punktewerte = [0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78]
            punkte = punktewerte[total_N_num]
            return punkte

        self.punkte_funktion = calc_points

    def field3_c2(self):
        """ grünes Feld """
        self.farbe = "Grün"
        self.version = "C2"

        black_b = shuffle(boni_symbols, 3, add=[boni_symbols[0], boni_symbols[1], boni_symbols[4]])
        black_boni_tmp.extend(black_b)

        a = (self.breite-2*w_)/12

        # Hintergrund und Pfeil
        super().rectangles(1,1, colors[3][2], w_/2, colors[3][1])
        super().rectangles(1,1, colors[3][2], dx0y0=(w_, 2*w_), dx1y1=(-11*a-w_, -2*w_), gap=0.75*w_)
        super().images(1,1, [[icons["arrow"]]], dx0y0=(w_, 2*w_), dx1y1=(-11*a-w_, -2*w_))

        # Interaktionsfelder
        text = ["x2", "x2", "x2", "x1", "x3", "x3", "x3", "x2", "x3", "x1", "x4", "x1"]
        super().rectangles(1, 12, color_field, version_tag=self.tags, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_))
        super().text(1,12, [text], dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_), font=("consolas", fontsize_mid), fill="dimgrey")
        super().ovals(1, 12, colors[3][2], dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_), gap=w_+0.2*w_, stepXY=(2,1),  dxy=(a/2,0))
        img = [[icons["minus"] , None, icons["minus"] , None, icons["minus"] , None, icons["minus"] , None, icons["minus"] , None, icons["minus"] , None, icons["minus"]], None]
        super().images(1, 12, img, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_), dxy=(a/2,0))

        # Speichere Eigenschaften
        self.n_x = 12
        self.n_y = 1
        self.dx0y0 = (w_+a, 2*w_)
        self.dx1y1 = (-w_, -2*w_)

        # Boni
        b_colors = shuffle(boni_colors, 8, add=["red", "black", "black", "black"])
        empty = np.full((4,), "")
        grid = [shuffle(empty, 12, add=b_colors, pref=["red"], sigma=1/10)]
        super().rectangles(1,12, grid, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_),  grid=grid, grid_del=True, grid_no_tag=False, gap=w_, dxy=(0,0.6*a))

        # Punkte
        super().ovals(1, 12, colors[3][2], dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_), gap=w_, stepXY=(2,1),  dxy=(a/2,-0.6*a))
        
        # Punktelogik
        def calc_points(stats):
            # stats ist das Dictionary, das get_stats(self) zurückgibt
            cols_num = stats["cols_num"]

            # Alten Text löschen
            canvas.delete("green_points_c2")

            # Position abrufen, an denen die Ovale sitzen
            x0_range, y0_range, cellsize_x, cellsize_y = self.cells(1, 12, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_))
            dxy = (a/2, -0.6*a)

            # Neue Punkte berechnen und neuen Text einfügen
            # Hier kann nicht super() verwendet werden
            points_list = []
            for i in range(0, 12, 2):
                if (len(cols_num)>i+1) and (cols_num[i]!=0) and (cols_num[i+1]!=0):
                    diff = cols_num[i] - cols_num[i+1]
                    points_list.append(diff)
                    x = x0_range[i]
                    y = y0_range[0]
                    canvas.create_text(x + cellsize_x/2 + dxy[0], y + cellsize_y/2 + dxy[1], text=str(diff), font=font_small, tags="green_points_c2")

            points = sum(points_list)
            return points
        
        self.punkte_funktion = calc_points 

    def field4_c2(self):
        """ lila Feld """
        self.farbe = "Lila"
        self.version = "C2"

        black_b = shuffle(boni_symbols, 4, add=[boni_symbols[0], boni_symbols[1], boni_symbols[4]])
        black_boni_tmp.extend(black_b)

        a = (self.breite-2*w_)/13

        # Hintergrund und Pfeil
        super().rectangles(1,1, colors[4][2], w_/2, colors[4][1])
        super().rectangles(1,1, colors[4][2], dx0y0=(w_, 2*w_), dx1y1=(-12*a-w_, -2*w_), gap=0.75*w_)
        super().images(1,1, [[icons["arrow"]]], dx0y0=(w_, 2*w_), dx1y1=(-12*a-w_, -2*w_))

        # Interaktionsfelder
        text = ["", "", ">1", ">2", ">3", ">4", ">5", ">1", ">2", ">3", ">4", ">5"]
        super().rectangles(1, 12, color_field, version_tag=self.tags, dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_))
        super().text(1,12, [text], dx0y0=(w_+a, 2*w_), dx1y1=(-w_, -2*w_), font=font_mid, fill="dimgrey")

        # Speichere Eigenschaften
        self.n_x = 12
        self.n_y = 1
        self.dx0y0 = (w_+a, 2*w_)
        self.dx1y1 = (-w_, -2*w_)

        # Boni
        b_colors = shuffle(boni_colors, 10, add=["red", "black", "black", "black", "black"])
        grid = [shuffle(b_colors, 10, pref=["red"], sigma=1/10)]
        super().rectangles(1, 10, grid, dx0y0=(w_+3*a, 2*w_), dx1y1=(-w_, -2*w_),  grid=grid, grid_del=True, grid_no_tag=False, gap=w_, dxy=(0,0.6*a))

        # Punktelogik
        def calc_points(stats):
            punkte = stats["total_num"]
            return punkte

        self.punkte_funktion = calc_points

    # -------------------------------

field0_x_list = ["field0_c1", "field0_c2"]
field1_x_list = ["field1_c1", "field1_c2", "field1_c2_c"]
field2_x_list_orange = ["field2_c1"]
field2_x_list_blue = ["field2_c2", "field2_c2_c"]
field3_x_list = ["field3_c1", "field3_c2"]
field4_x_list = ["field4_c1", "field4_c2"]

# ================================================================
# Hilfsfunktionen
# ================================================================

def shuffle(object, result_len, add=None, pref=None, sigma=1/6):
    """
    object: Liste von Objekten
    result_len: Länge der zurückgegebenen Liste
    add: Liste mit Elementen, die hinzugefügt werden
    """

    object = list(object)
    random.shuffle(object)

    if add is not None:
        object = object[:result_len - len(add)] + list(add)
        random.shuffle(object)
    else:
        object = object[:result_len]
    
    # Gauß-Bias für bestimmte Elemente
    """
    preferred: Menge/Liste bevorzugter Elemente
    sigma: Faktor für Gauß-Verteilung (relativ zur Länge)
        sigma=1/6: 68% der bevorzugten Elemte landen im mittlleren Drittel der Liste
    """
    if pref is not None:
        center = (result_len - 1) / 2
        sigma = result_len*sigma
        arr = []
        for item in object:
            if item in pref:
                pos = random.gauss(center, sigma)
            else:
                pos = random.uniform(0, result_len)
            arr.append((pos, item))
        arr = np.array(arr)
        sorted_arr = arr[arr[:, 0].argsort()]
        object = sorted_arr[:, 1].tolist()
    return object 

def update_coords(event):
    """ aktualisiert den Text des Labels mit den aktuellen x/y-Koordinaten """
    label.config(text=f"X: {event.x}, Y: {event.y}")

def complementary_color(color):
    """
    Ermittelt die exakte RGB-Komplementärfarbe.
    Unterstützt: '#RRGGBB' und Tk-Farbnamen.
    """
    if color == color_bg:
        return "crimson"
    elif color == "red":
        return "black"
    elif color == color_field:
        return "crimson"
    
    r, g, b = root.winfo_rgb(color)  # 0–65535
    r //= 256
    g //= 256
    b //= 256

    return f"#{255 - r:02x}{255 - g:02x}{255 - b:02x}"

def count_black_boni(liste):
    "zählt, wie oft jedes Element in der Liste wie oft vorkommt"
    zaehler = {}
    for element in liste:
        if element in zaehler:
            zaehler[element] += 1
        else:
            zaehler[element] = 1
    return zaehler

def get_stats(version_obj):
    """ zählt Anzahl der Kreuze und Zahlen pro Zeile, Spalte und insgesamt im Objekt version_obj (z.B: field0_c1) """
   
    # Attribute des Objekts
    x0_range, y0_range, cell_w, cell_h = version_obj.cells(version_obj.n_y, 
                                                           version_obj.n_x,
                                                           version_obj.dx0y0,
                                                           version_obj.dx1y1)
    
    # Alle Kreuze und Zahlen im Bereich
    all_crosses = canvas.find_withtag("cross")
    all_ovals = canvas.find_withtag("oval")
    all_nums = canvas.find_withtag("num")

    # Dictionary
    stats = {"total_crosses":0, "rows_cross": [], "cols_cross": [], "total_num":0, "total_N_num":0, "rows_num": [], "cols_num": [], "total_ovals":0, "rows_oval": [], "cols_oval": []}

    def sum_nums_in_items(item_list):
        total = 0
        for item_id in (set(all_nums) & set(item_list)):
            if canvas.type(item_id) == "text":
                try:
                    total += int(canvas.itemcget(item_id, "text"))
                except ValueError:
                    continue
        return total

    # Zeilen
    for y in y0_range:
        # Alle IDs im Bereich 
        items = canvas.find_enclosed(x0_range[0]-1, y-1, x0_range[-1]+cell_w+1, y+cell_h+1)
        # Schnittmenge aller IDs UND Kreuze; IDs UND Zahlen
        stats["rows_cross"].append(len(set(items) & set(all_crosses)))
        stats["rows_oval"].append(len(set(items) & set(all_ovals)))
        stats["rows_num"].append(sum_nums_in_items(items))
    
    # Spalten
    total_N_num = 0
    for x in x0_range:
        items = canvas.find_enclosed(x-1, y0_range[0]-1, x+cell_w+1, y0_range[-1]+cell_h+1)
        # Schnittmenge aller IDs UND Kreuze; IDs UND Zahlen
        stats["cols_cross"].append(len(set(items) & set(all_crosses)))
        stats["cols_oval"].append(len(set(items) & set(all_ovals)))
        stats["cols_num"].append(sum_nums_in_items(items))
        anzahl_zahlen = len(set(items) & set(all_nums))
        total_N_num += int(anzahl_zahlen)

    stats["total_crosses"] = sum(stats["rows_cross"])
    stats["total_ovals"] = sum(stats["rows_oval"])
    stats["total_num"] = sum(stats["rows_num"])
    stats["total_N_num"] = total_N_num

    return stats

def get_fuchs_stats():
    """ zählt die Anzahl der angekreuzten Füchse auf dem Spielfeld """
    all_crosses = canvas.find_withtag("cross")
    all_ovals = canvas.find_withtag("oval")
    all_fuchses = canvas.find_withtag("fuchs")
    
    all_cross_ovals = set(all_crosses) | set(all_ovals)

    fuchs = 0
    for fuchs_id in all_fuchses:
        # Position des Fuchses
        coords = canvas.coords(fuchs_id)
        fx = int((coords[0]+coords[2])/2)
        fy = int((coords[1]+coords[3])/2)
        dx = int(np.abs(coords[0]-coords[2])/2)
        dy = int(np.abs(coords[1]-coords[3])/2)
        
        # Sucht nach Objekten um das Fuchs-Zentrum
        items = canvas.find_overlapping(fx-dx, fy-dy, fx+dx, fy+dy)
        
        # Wenn sich in der Auswahl ein Kreuz befindet, zählt der Fuchs als angekreuzt
        if set(items) & set(all_cross_ovals):
            fuchs += 1

    return fuchs

def get_color_stats():
    all_crosses = canvas.find_withtag("cross")
    all_ovals = canvas.find_withtag("oval")

    all_cross_ovals = set(all_crosses) | set(all_ovals)

    stats = {boni_colors[0]: 0, boni_colors[1]: 0, boni_colors[2]: 0, boni_colors[3]: 0, boni_colors[4]: 0, "black": 0}
    all_colors = np.append(boni_colors, ["black"])
    for color in all_colors:
        all_color_ids = canvas.find_withtag(color)

        n_color = 0
        for id in all_color_ids:
            coords = canvas.coords(id)
            fx = int((coords[0]+coords[2])/2)
            fy = int((coords[1]+coords[3])/2)
            dx = int(np.abs(coords[0]-coords[2])/3)
            dy = int(np.abs(coords[1]-coords[3])/3)
            
            # Sucht nach Objekten um das Zentrum
            items = canvas.find_overlapping(fx-dx, fy-dy, fx+dx, fy+dy)
            
            # Wenn sich in der Auswahl ein Kreuz oder Oval befindet, zählt es als angekreuzt
            if set(items) & set(all_cross_ovals):
                n_color += 1
        stats[color] = n_color

    return stats

# ================================================================
# Spielfeld generieren
# ================================================================

ids, boni_ids, runden_ids, fuchs_ids, black_ids = [], [], [], [], []
black_boni = {}

def spielfeld_generieren(seed_wert):
    global black_boni_on_field, black_boni_tmp, game_history, black_boni
    global field0_x, field1_x, field2_x, field3_x, field4_x
    global ids, boni_ids, runden_ids, fuchs_ids, black_ids
    global aktueller_seed
    global farben, spielversionen

    # Canvas komplett leeren & Listen zurücksetzen
    canvas.delete("all")
    black_boni_on_field = [boni_symbols[0], boni_symbols[4], boni_symbols[0], boni_symbols[1], boni_symbols[2], boni_symbols[3]]
    black_boni_tmp = []
    game_history = []
    update_history_display()

    # Seed setzen und anzeigen
    aktueller_seed = seed_wert
    random.seed(seed_wert)

    # ================================================================
    # Statische Felder zeichnen
    # ================================================================

    # Hauptfeld
    main = Spielfeld(board_width, game_height, (0,0))
    main.rectangles(1, 1, "#000000")

    # Würfelfelder
    würfel = Spielfeld(1/9*game_height-v_, game_height*(1/3)-v_, (v_,v_))
    würfel.rectangles(3, 1, color_bg, v_, color_header)

    # Rundenfelder
    runden_breite = board_width-würfel.breite-w_-v_
    runden_höhe = würfel.höhe/4
    rundentext = Spielfeld(runden_breite*(1/4), würfel.höhe/4, (würfel.x1y1()[0]+v_, v_))
    rundentext.rectangles(1, 1, color_bg, v_, "#000000")
    rundentext.text(1, 1, [["Runden"]], font=font_large, fill="white")
    runden = Spielfeld(runden_breite*(3/4), rundentext.höhe, (rundentext.x1y1()[0], rundentext.x0y0[1]))
    runden.rectangles(1, 1, color_bg, v_, color_header)

    # Bonusfelder
    bonustext = Spielfeld(rundentext.breite, würfel.höhe-rundentext.höhe-v_, (rundentext.x0y0[0], (rundentext.x1y1()[1]+v_)))
    bonustext.rectangles(5, 1, color_bg, v_/2, "#000000")
    boni_images = [[icons["nw"]], [icons["rh"]], [icons["pm"]], [icons["zw"]], [icons["p1"]]]
    boni_images_2 = [[icons["B"]], [icons["B"]], [icons["B"]], [icons["B"]], [None]]
    bonustext.images(5, 1, boni_images)
    bonustext.images(5, 1, boni_images_2, dxy=(-3*w_,0))
    bonus = Spielfeld(runden.breite, bonustext.höhe, (bonustext.x1y1()[0], bonustext.x0y0[1]))
    bonus.rectangles(5, 1, color_bg, v_/2, color_header)

    # Farbfelder
    field0 = Spielfeld(board_width*(1/2)-(3/2)*v_, würfel.höhe, (würfel.x0y0[0], würfel.x1y1()[1]+v_))
    field0.rectangles(1,1,color_bg)
    field1 = Spielfeld(field0.breite, field0.höhe, (field0.x1y1()[0]+v_, field0.x0y0[1]))
    field1.rectangles(1,1,color_bg)
    field2 = Spielfeld(board_width-w_, (würfel.höhe)/3-v_, (field0.x0y0[0], field0.x1y1()[1]+v_))
    field2.rectangles(1,1,color_bg)
    field3 = Spielfeld(field2.breite, field2.höhe, (field0.x0y0[0], field2.x1y1()[1]+v_))
    field3.rectangles(1,1,color_bg)
    field4 = Spielfeld(field2.breite, field2.höhe, (field0.x0y0[0], field3.x1y1()[1]+v_))
    field4.rectangles(1,1,color_bg)

    # ================================================================
    # Defintion interaktiver Felder
    # ================================================================

    # wähle zufällige Spielfelder aus
    field0_x_ = shuffle(field0_x_list, 1)[0]
    field1_x_ = shuffle(field1_x_list, 1)[0]
    field3_x_ = shuffle(field3_x_list, 1)[0]
    field4_x_ = shuffle(field4_x_list, 1)[0]

    # Runden und Felder 1,2 instanziieren
    rundenfelder = Versionen(runden, "rundenfelder")
    field0_x = Versionen(field0, field0_x_)
    field1_x = Versionen(field1, field1_x_)

    # Spielfeld 3 basierend auf der Farbe von Spielfeld 2 auswählen
    if field1_x.farbe == "Orange":
        field2_x_ = shuffle(field2_x_list_blue, 1)[0]
    else:
        field2_x_ = shuffle(field2_x_list_orange, 1)[0]

    # Restliche Spielfelder instanziieren
    field2_x = Versionen(field2, field2_x_)
    field3_x = Versionen(field3, field3_x_)
    field4_x = Versionen(field4, field4_x_)
    farben = [field0_x.farbe, field1_x.farbe, field2_x.farbe, field3_x.farbe, field4_x.farbe]
    spielversionen = [field0_x.version, field1_x.version, field2_x.version, field3_x.version, field4_x.version]
    #print("Clever-Version|Farbe:\n    " + "    ".join(f"{i}|{j}" for i, j in zip(spielversionen, farben)) + "\n")

    # Schwarze Boni
    black_boni = count_black_boni(black_boni_on_field)
    boni_canvas = Versionen(bonus, "bonifelder")
    
    # ================================================================
    # ID-Listen
    # ================================================================
    ids = []
    ids.append(canvas.find_withtag(field0_x_))
    ids.append(canvas.find_withtag(field1_x_))
    ids.append(canvas.find_withtag(field2_x_))
    ids.append(canvas.find_withtag(field3_x_))
    ids.append(canvas.find_withtag(field4_x_))
    ids = np.hstack(ids)

    boni_ids = []
    for i in range(5):
        boni_ids.append(canvas.find_withtag(colors[i][0]))
    boni_ids.append(canvas.find_withtag("black"))
    boni_ids = np.hstack(boni_ids)

    runden_ids = []
    runden_ids.append(canvas.find_withtag("rundenfelder"))
    runden_ids = np.hstack(runden_ids)

    fuchs_ids = []
    fuchs_ids.append(canvas.find_withtag("fuchs"))
    fuchs_ids = np.hstack(fuchs_ids)

    black_ids = []
    black_ids.append(canvas.find_withtag("nw"))
    black_ids.extend(canvas.find_withtag("rh"))
    black_ids.extend(canvas.find_withtag("zw"))
    black_ids.extend(canvas.find_withtag("pm"))
    black_ids.extend(canvas.find_withtag("p1"))
    black_ids = np.hstack(black_ids)

    # Punktestand zurücksetzen
    score.set(f" Seed: {aktueller_seed} \n \n Anzahl Punkte: 0 \n -------------------------- \n {farben[0]}: 0 \n {farben[1]}: 0 \n {farben[2]}: 0 \n {farben[3]}: 0 \n {farben[4]}: 0 \n Füchse: 0 \n \n Anzahl Aktionen: 0 \n -------------------------- \n {farben[0]}: 0 \n {farben[1]}: 0 \n {farben[2]}: 0 \n {farben[3]}: 0 \n {farben[4]}: 0 \n \n Anzahl Boni: 0 \n -------------------------- \n Gelb: 0 \n Blau: 0 \n Orange: 0 \n Grün: 0 \n Lila: 0 \n Schwarz: 0 \n Füchse: 0 ")

# ================================================================
# Spielmechanik & Interaktionen
# ================================================================

# Punktefeld
score = tk.StringVar()
score_label = tk.Label(root, textvariable=score, font=font_midlarge, width=int(22), bg=color_bg)
score_label.place(x=(board_width+w_), y=3*w_)

def on_click(event):

    def interaction(id):
        x0, y0, x1, y1 = canvas.coords(id) 
        dx = abs(x1-x0)
        dy = abs(y1-y0)
        da = min(dx,dy)
        x = x0+dx/2
        y = y0+dy/2
        fontsize = int(min(dx, dy)*0.6)

        farbe = canvas.itemcget(id, "fill")
        color = complementary_color(farbe)

        # Tag für Verlauf auslesen
        raw_tags = canvas.gettags(id)
        tags = [t for t in raw_tags if t != "current"]  
        field_tag = tags[1] if len(tags) > 1 else (tags[0] if tags else "unbekannt")
        
        # Ids innerhalb dieser Koordinaten
        items_in_field = canvas.find_enclosed(x0-1, y0-1, x1+1, y1+1)

        # Linksklick = Kreuz
        if event.num == 1:
            cross_id = set(items_in_field) & set(canvas.find_withtag("cross"))
            
            if cross_id:
                for i in cross_id:
                    canvas.delete(i)
                action = {"type": "del x", "field": field_tag, "coords": (x, y)} # Verlauf
            else:
                canvas.create_text(x, y, text="X", fill=color, font=(fonttype, fontsize, "bold"), tags="cross")
                action = {"type": "x", "field": field_tag, "coords": (x, y)} # Verlauf

        # Rechtsklick = Kreis
        elif event.num == 3:
            oval_id = set(items_in_field) & set(canvas.find_withtag("oval"))
            
            if oval_id:
                for i in oval_id:
                    canvas.delete(i)
                action = {"type": "del o", "field": field_tag, "coords": (x, y)} # Verlauf
            else:
                canvas.create_oval(x-da/4, y-da/4, x+da/4, y+da/4, outline=color, width=4, tags="oval")
                action = {"type": "o", "field": field_tag, "coords": (x, y)} # Verlauf
        
        # Mittelklick = Nummer eintragen
        elif event.num == 2:
            num_id = set(items_in_field) & set(canvas.find_withtag("num"))
            
            if num_id:
                for i in num_id:
                    canvas.delete(i)
                action = {"type": "del num", "field": field_tag, "coords": (x,y)}
            else:
                user_input = simpledialog.askstring("", "Bitte Zahl eingeben:", parent=root)
                if user_input is None:  # Abbruch
                    return
                # Prüfen, dass es tatsächlich eine Zahl ist
                try:
                    int(user_input) # Prüft, ob es eine gültige Ganzzahl ist (inkl. negativ)
                except (ValueError, TypeError):
                    return
                
                action = {"type": user_input, "field": field_tag, "coords": (x,y)} # Verlauf
                
                # Textbreite und Texthöhe berechnen
                factor = 0.7
                num_fontsize = int(min(dx, dy)*factor)
                f = tk.font.Font(family=fonttype, size=num_fontsize, weight="bold")
                w = f.measure(user_input)  # Textbreite
                h = f.metrics("linespace") # Texthöhe
                while (w > dx*factor or h > dy*factor) and num_fontsize > 1:
                    num_fontsize -= 1
                    f = tk.font.Font(family=fonttype, size=num_fontsize, weight="bold")
                    w = f.measure(user_input)
                    h = f.metrics("linespace")

                # Text
                f = tkfont.Font(family=fonttype, size=num_fontsize, weight="bold")
                canvas.create_text(x, y, text=user_input, fill=color, font=(fonttype, num_fontsize, "bold"), tags="num")
                
        
        # Verlauf
        game_history.append(action)
        update_history_display()

    # Finde alle Objekte an der Klick-Position (x, y)
    overlapping_ids = canvas.find_overlapping(event.x, event.y, event.x, event.y)
    if not overlapping_ids: return

    for id in reversed(overlapping_ids):

        # Boni-Felder
        if id in boni_ids:
            interaction(id)
            break

        # Interaktionsfelder
        elif id in ids:
            interaction(id)
            break
        
        # Rundenfelder
        elif id in runden_ids:
            interaction(id)
            break

        # Füchse
        elif id in fuchs_ids:
            interaction(id)
            break

        # Schwarze Boni im Boni-Feld
        elif id in black_ids:
            interaction(id)
            break
    
    # Statistik für Punkte und Zahlen
    
    fields = [field0_x, field1_x, field2_x, field3_x, field4_x]
    gesamt_punkte = 0
    punkte_fields = []
    all_actions = []
    for f in fields:
        stats = get_stats(f)
        actions = stats["total_crosses"] + stats["total_N_num"] + stats["total_ovals"]
        all_actions.append(actions)
        # Jedes Feld nutzt seine eigene, interne Logik
        punkte = f.punkte_funktion(stats)
        punkte_fields.append(punkte)
        gesamt_punkte += punkte

    num_fuchs = get_fuchs_stats()
    punkte_fuchs = num_fuchs*min(punkte_fields)
    gesamt_punkte = gesamt_punkte + punkte_fuchs
    gesamt_actions = sum(all_actions)

    color_stats = get_color_stats()
    gesamt_color = color_stats[boni_colors[0]] + color_stats[boni_colors[1]] + color_stats[boni_colors[2]] + color_stats[boni_colors[3]] + color_stats[boni_colors[4]] + color_stats["black"] + num_fuchs
    
    score.set(f" Seed: {aktueller_seed} \n \n Anzahl Punkte:  {gesamt_punkte} \n -------------------------- \n {farben[0]}: {punkte_fields[0]} \n {farben[1]}: {punkte_fields[1]} \n {farben[2]}: {punkte_fields[2]} \n {farben[3]}: {punkte_fields[3]} \n {farben[4]}: {punkte_fields[4]} \n Füchse: {punkte_fuchs} \n \n Anzahl Aktionen: {gesamt_actions} \n -------------------------- \n {farben[0]}: {all_actions[0]} \n {farben[1]}: {all_actions[1]} \n {farben[2]}: {all_actions[2]} \n {farben[3]}: {all_actions[3]} \n {farben[4]}: {all_actions[4]} \n \n Anzahl Boni: {gesamt_color} \n -------------------------- \n Gelb: {color_stats[boni_colors[0]]} \n Blau: {color_stats[boni_colors[1]]} \n Orange: {color_stats[boni_colors[2]]} \n Grün: {color_stats[boni_colors[3]]} \n Lila: {color_stats[boni_colors[4]]} \n Schwarz: {color_stats["black"]} \n Füchse: {num_fuchs}")

# ================================================================
# UI-Steuerungselemente
# ================================================================
def open_setup_window():
    setup_win = tk.Toplevel(root)
    setup_win.title("Spielfeld Steuerung")
    setup_win.geometry(f"320x225")
    setup_win.configure(bg=color_bg)
    
    lbl = tk.Label(setup_win, text="Seed eingeben oder würfeln:", font=font_large, bg=color_bg)
    lbl.pack(pady=10)

    entry = tk.Entry(setup_win, font=font_large, justify="center")
    entry.pack(fill="x", padx=20, pady=5)
    
    # Den aktuellen, beim Start gewählten Seed im Textfeld anzeigen
    entry.insert(0, start_seed)

    def apply_manual_seed():
        """Liest den manuell eingetippten Seed und generiert das Feld."""
        seed_wert = entry.get().strip()
        if not seed_wert:
            # Falls das Feld komplett leer ist, einen neuen zufälligen Seed erzeugen
            seed_wert = str(random.randint(0, 999999))
            entry.delete(0, tk.END)
            entry.insert(0, seed_wert)
        spielfeld_generieren(seed_wert)

    def reroll_seed():
        """Erzeugt eine neue Zufallszahl im Textfeld und baut das Spielfeld um."""
        neuer_seed = str(random.randint(0, 999999))
        entry.delete(0, tk.END)
        entry.insert(0, neuer_seed)
        spielfeld_generieren(neuer_seed)

    # Erste Reihe an Buttons (Generieren und Reroll)
    action_frame = tk.Frame(setup_win, bg=color_bg)
    action_frame.pack(fill="x", pady=10, padx=20)

    generate_btn = tk.Button(action_frame, text="Generieren", font=font_large, bg="#504f4f", fg="white", command=apply_manual_seed)
    generate_btn.pack(side="left", expand=True, fill="x", padx=5)

    reroll_btn = tk.Button(action_frame, text="Reroll", font=font_large, command=reroll_seed)
    reroll_btn.pack(side="right", expand=True, fill="x", padx=5)

    # Zweite Reihe (OK / Schließen-Button unten drunter)
    close_frame = tk.Frame(setup_win, bg=color_bg)
    close_frame.pack(fill="x", pady=5, padx=20)

    ok_btn = tk.Button(close_frame, text="START", font=font_large, command=setup_win.destroy)
    ok_btn.pack(fill="x", padx=5)

# ================================================================
# Generierungung der tkinter Oberfläche
# ================================================================

# Mausbewegung im Fenster überwachen
root.bind('<Motion>', update_coords)

canvas.bind("<Button-1>", on_click)  # Links = Kreuz
canvas.bind("<Button-2>", on_click)  # Mitte = löschen
canvas.bind("<Button-3>", on_click)  # Rechts = Kreis

# 1. Beim allerersten Start direkt ein Spielfeld generieren
start_seed = str(random.randint(0, 999999))
spielfeld_generieren(start_seed)

# 2. Das Steuerungsfenster daneben aufmachen
root.after(100, open_setup_window)

root.mainloop()
