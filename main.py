import tkinter as tk
from typing import List
import random
import math
from tkinter.constants import *
from PIL import ImageTk, Image
from tkextrafont import Font

class Player():
    def __init__(self, name, rating):
        self.name = name
        self.rating = rating
        self.previously_played = []


class MatchMaker:
    def __init__(self):
        self.known_players = {}
        self.round = 0

    def get_round(self):
        return self.round

    def players_with_known(self, players):
        players_with_known = []
        for player in players:
            known_player = self.known_players.get(player.name)
            if known_player is None:
                known_player = player
            players_with_known.append(known_player)
        return players_with_known

    def get_matches(self, players: List[Player]):
        self.round += 1
        players_with_known = self.players_with_known(players)
        pairings = []
        while len(players_with_known) > 1:
            current = random.choice(players_with_known)
            players_with_known.remove(current)
            rating_differences = list(map(lambda x: abs(x.rating - current.rating), players_with_known))
            weightings = list(map(lambda x: min(max(10 * math.e ** (-(x / 800) ** 2), 1), 10), rating_differences))
            opponent = random.choices(players_with_known, weights=weightings, k=1)[0]
            i = 0
            while opponent.name in current.previously_played and i < 10:
                opponent = random.choices(players_with_known, weights=weightings, k=1)[0]
                i += 1
            if opponent.name in list(map(lambda x: x.name, current.previously_played)):
                not_played = list(set(players_with_known) - set(current.previously_played))
                if len(not_played) > 0:
                    opponent = random.choice(not_played)
            current.previously_played.append(opponent)
            opponent.previously_played.append(current)
            current.previously_played = current.previously_played[-5:]
            opponent.previously_played = opponent.previously_played[-5:]
            players_with_known.remove(opponent)
            self.known_players.update({current.name: current, opponent.name: opponent})
            pairings.append([current, opponent])

        if len(players_with_known) == 1:
            pairings.append([players_with_known[0], Player("Oversidder", 0)])
        return pairings


class PlayersBody(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.entries = []
        self.buttons = []
        self.rows = 16
        self.columns = 4

        # create the table of widgets
        for row in range(self.rows):
            self.add_row(row)

        # adjust column weights so they all expand equally
        for column in range(self.columns):
            self.grid_columnconfigure(column, weight=1)
        # designate a final, empty row to fill up any extra space
        # self.grid_rowconfigure(self.rows, weight=1)

    def button_frame(self, i):
        button_frame = tk.Frame(self)
        delete = tk.Button(button_frame, text=" - ", command=lambda: self.delete_row(i))
        add = tk.Button(button_frame, text=" + ", command=lambda: self.add_row(i))
        delete.pack(side="left")
        add.pack(side="left")
        return button_frame

    def add_row(self, row):
        # Name entry
        name = tk.Entry(self, validate="key")

        # Rating entry
        rating = tk.Entry(self, validate="key", validatecommand=(self.register(self.validate_rating), "%P"))

        # Skip entry
        skipping = tk.BooleanVar()
        skip = tk.Checkbutton(self, variable=skipping, onvalue=True, offvalue=False)

        self.entries.insert(row, [name, rating, (skipping, skip)])
        for entry in self.entries:
            name, rating, (skipping, skip) = entry
            name.grid_forget()
            rating.grid_forget()
            skip.grid_forget()
        for button_frame in self.buttons:
            button_frame.grid_forget()
        self.buttons = []
        for i, entry in enumerate(self.entries):
            name, rating, (skipping, skip) = entry
            button_frame = self.button_frame(i + 1)
            self.buttons.append(button_frame)
            name.grid(row=i, column=0, stick="nsew")
            rating.grid(row=i, column=1, stick="nsew")
            skip.grid(row=i, column=2, stick="nsew")
            button_frame.grid(row=i, column=3, stick="nsew")

    def delete_row(self, i):
        if len(self.entries) > 1:
            for entry in self.entries:
                name, rating, (skipping, skip) = entry
                name.grid_forget()
                rating.grid_forget()
                skip.grid_forget()
            for button_frame in self.buttons:
                button_frame.grid_forget()
            self.buttons = []
            del self.entries[i - 1]
            for i, entry in enumerate(self.entries):
                name, rating, (skipping, skip) = entry
                button_frame = self.button_frame(i + 1)
                self.buttons.append(button_frame)
                name.grid(row=i, column=0, stick="nsew")
                rating.grid(row=i, column=1, stick="nsew")
                skip.grid(row=i, column=2, stick="nsew")
                button_frame.grid(row=i, column=3, stick="nsew")

    def get(self):
        '''Return a list of lists, containing the data in the table'''
        result = []
        for entry in self.entries:
            current_row = []
            current_row.append(entry[0].get())
            rating = entry[1].get()
            if not (len(rating) > 0):
                current_row.append(0)
            else:
                current_row.append(int(rating))
            current_row.append(entry[2][0].get())
            result.append(current_row)
        return result

    def validate_rating(self, P):
        '''Perform input validation.

        Allow only an empty value, or a value that can be converted to a float
        '''
        if P.strip() == "":
            return True

        try:
            f = int(P)
        except ValueError:
            self.bell()
            return False
        return True

class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = tk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = PlayersBody(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


class PlayersUI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        header = PlayersHeader(parent)
        body = VerticalScrolledFrame(parent)
        footer = PlayersFooter(parent, body.interior.get)
        header.pack(side="top", fill="both")  # , expand=True)
        body.pack(side="top", fill="both", expand=True)
        footer.pack(side="top", fill="both")  # , expand=True)


class PlayersHeader(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        names = ["Navn", "Rating", "Udebliver", ""]
        frame = tk.Frame(self)
        frame.pack(side="top", fill="both", expand=True)
        for i, title in enumerate(names):
            l = tk.Label(frame, text=title, font='Helvetica 16 bold')
            l.grid(row=0, column=i)
            frame.grid_columnconfigure(i, weight=1)


class PlayersFooter(tk.Frame):
    def __init__(self, parent, get):
        tk.Frame.__init__(self, parent)
        self.get = get
        self.new_round_btn = tk.Button(self, text="Ny runde", font='Helvetica 16 bold', command=self.new_round)
        self.new_round_btn.pack()
        self.matchmaker = MatchMaker()

    def new_round(self):
        entries = list(filter(lambda x: len(x[0]) > 0 and x[1] >= 0 and not x[2], self.get()))
        players = list(map(lambda x: Player(x[0], x[1]), entries))
        round = self.matchmaker.get_round()
        win = tk.Toplevel(self)
        win.geometry("1280x720")
        win.title(f"Runde {round}")
        bg = ImageTk.PhotoImage(file="bg.png")
        canvas = tk.Canvas(win, width=700, height=3500)
        canvas.pack(fill=BOTH, expand=True)
        canvas.create_image(0, 0, image=bg, anchor='nw')
        matches = self.matchmaker.get_matches(players)

        global width_before
        width_before = 0
        global height_before
        height_before = 0

        def resize_image(e):
            global image, resized, image2, height_before, width_before

            if e.height != height_before or e.width != width_before:
                # open image to resize it
                image = Image.open("bg.png")
                # resize the image with width and height of root
                resized = image.resize((e.width, e.height), Image.LANCZOS)

                image2 = ImageTk.PhotoImage(resized)
                canvas.create_image(0, 0, image=image2, anchor='nw')
                canvas.create_text(math.floor(e.width*2/6), math.floor(e.height*1/15), anchor="center", text="Hvid", font=("Josefin Sans", 36), fill='#FFFFFF')
                canvas.create_text(math.floor(e.width*4/6), math.floor(e.height*1/15), anchor="center", text="Sort", font=("Josefin Sans", 36), fill='#FFFFFF')
                for i, match in enumerate(matches):
                    canvas.create_text(math.floor(e.width * 1 / 6), math.floor(e.height * 2 / 15)+i*45, anchor="center",
                                       text=f"Bræt {i+1}", font=("Josefin Sans", 26), fill='#FFFFFF')
                    canvas.create_text(math.floor(e.width * 2 / 6), math.floor(e.height * 2 / 15)+i*45, anchor="center",
                                       text=f"({match[0].rating}) {match[0].name}", font=("Josefin Sans", 26), fill='#FFFFFF')
                    canvas.create_text(math.floor(e.width * 3 / 6), math.floor(e.height * 2 / 15)+i*45, anchor="center",
                                       text=f"vs", font=("Josefin Sans", 26), fill='#FFFFFF')
                    canvas.create_text(math.floor(e.width * 4 / 6), math.floor(e.height * 2 / 15)+i*45, anchor="center",
                                       text=f"{match[1].name} ({match[1].rating})", font=("Josefin Sans", 26), fill='#FFFFFF')
                width_before = e.width
                height_before = e.height
        win.bind("<Configure>", resize_image)


root = tk.Tk()
JOSEFIN = Font(file="JosefinSans-Bold.ttf", family="Josefin Sans")
root.geometry("1000x500")
root.title("Bønderne MatchMaker by ChrIT")
PlayersUI(root)
root.mainloop()
