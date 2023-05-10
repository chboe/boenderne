import tkinter as tk
import random
import math
from tkinter.constants import *
from PIL import ImageTk, Image
import sys, os
import pandas as pd
import uuid

SESSION_ID = str(uuid.uuid4())
SAVE_PATH = os.path.expanduser('Documents/Boenderne')
PLAYERS = pd.DataFrame({
    'id': pd.Series(dtype='str'),
    'name': pd.Series(dtype='str'),
    'rating': pd.Series(dtype='int'),
    'oversidder': pd.Series(dtype='boolean')
})
MATCHES = pd.DataFrame({
    'sessionId': pd.Series(dtype='str'),
    'round': pd.Series(dtype='int'),
    'p1Id': pd.Series(dtype='str'),
    'p2Id': pd.Series(dtype='str'),
    'winnerId': pd.Series(dtype='str'),
    'p1Rating': pd.Series(dtype='int'),
    'p2Rating': pd.Series(dtype='int')
})


def load_db():
    global PLAYERS
    global MATCHES
    if os.path.exists(os.path.join(SAVE_PATH, 'PLAYERS.csv')):
        PLAYERS = pd.read_csv(os.path.join(SAVE_PATH, 'PLAYERS.csv'), index_col=0,
                              dtype={'id': str, 'name': str, 'rating': int, 'oversidder': bool})
    if os.path.exists(os.path.join(SAVE_PATH, 'MATCHES.csv')):
        MATCHES = pd.read_csv(os.path.join(SAVE_PATH, 'MATCHES.csv'), keep_default_na=False, index_col=0,
                              dtype={'sessionId': str, 'round': int, 'p1Id': str, 'p2Id': str, 'winnerId': str,
                                     'p1Rating': int, 'p2Rating': int})


def save_db():
    global PLAYERS
    global MATCHES

    if not os.path.isdir(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    PLAYERS.to_csv(path_or_buf=os.path.join(SAVE_PATH, 'PLAYERS.csv'))
    MATCHES.to_csv(path_or_buf=os.path.join(SAVE_PATH, 'MATCHES.csv'))


def compute_rating_change(p1Rating, p2Rating, outcome):
    e = 1 / (1 + 10 ** ((p2Rating - p1Rating) / 400))
    return max(int(math.floor(32 * (outcome - e))), 0)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Player():
    def __init__(self, id, name, rating, oversidder=False):
        self.id = id
        self.name = name
        self.rating = rating
        self.oversidder = oversidder


class MatchMaker:
    def __init__(self):
        self.known_players = {}
        self.round = 0

    def get_round(self):
        return self.round

    def get_not_played(self, pId):
        base = PLAYERS.loc[PLAYERS['oversidder'] == False]
        opponents_as_p1 = list(
            MATCHES.loc[(MATCHES['sessionId'] == SESSION_ID) & (MATCHES['p1Id'] == pId), 'p2Id'].values)
        opponents_as_p2 = list(
            MATCHES.loc[(MATCHES['sessionId'] == SESSION_ID) & (MATCHES['p2Id'] == pId), 'p1Id'].values)
        all_opponents = opponents_as_p1 + opponents_as_p2
        res = list(base.loc[~base['id'].isin(all_opponents), 'id'].values)
        return res

    def has_played_recently(self, p1Id, p2Id):
        recent_matches = MATCHES.loc[(MATCHES['sessionId'] == SESSION_ID) & (
                ((MATCHES['p1Id'] == p1Id) & (MATCHES['p2Id'] == p2Id)) |
                ((MATCHES['p1Id'] == p2Id) & (MATCHES['p2Id'] == p1Id))) & (self.round - MATCHES['round']) < 5]
        return len(recent_matches.index) > 0

    def get_matches(self):
        self.round += 1
        players = list(
            map(lambda x: Player(x[0], x[1], x[2]), list(PLAYERS.loc[PLAYERS['oversidder'] == False].values)))
        pairings = []
        while len(players) > 1:
            current = random.choice(players)
            players.remove(current)
            rating_differences = list(map(lambda x: abs(x.rating - current.rating), players))
            weightings = list(map(lambda x: min(max(10 * math.e ** (-(x / 800) ** 2), 1), 10), rating_differences))
            opponent = random.choices(players, weights=weightings, k=1)[0]
            i = 0
            while self.has_played_recently(current.id, opponent.id) and i < 0:
                opponent = random.choices(players, weights=weightings, k=1)[0]
                i += 1
            if self.has_played_recently(current.id, opponent.id):
                not_played = list(filter(lambda x: x.id in self.get_not_played(current.id), players))
                if len(not_played) > 0:
                    opponent = random.choice(not_played)
            players.remove(opponent)
            pairings.append([current, opponent])

        if len(players) == 1:
            pairings.append([players[0], Player("Oversidder", "Oversidder", 0)])
        return pairings


class PlayersBody(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.entries = []
        self.buttons = []
        self.columns = 4

        # create the table of widgets
        self.refresh_entries()

        # adjust column weights so they all expand equally
        for column in range(self.columns):
            self.grid_columnconfigure(column, weight=1)
        # designate a final, empty row to fill up any extra space
        # self.grid_rowconfigure(self.rows, weight=1)

    def refresh_df(self):
        global PLAYERS
        PLAYERS.drop(PLAYERS.index, inplace=True)
        for name, rating, skipping, id in self.get():
            new_row = pd.DataFrame({'id': id, 'name': name, 'rating': rating, 'oversidder': skipping}, index=[0])
            PLAYERS = pd.concat([new_row, PLAYERS.loc[:]]).reset_index(drop=True)
        PLAYERS.sort_values(by=['name'], inplace=True)

    def refresh_entries(self):
        for i in range(len(self.entries)):
            for name, rating, skip, skipping, id in self.entries:
                name.grid_forget()
                rating.grid_forget()
                skip.grid_forget()
            for button_frame in self.buttons:
                button_frame.grid_forget()
            self.buttons = []
            self.entries = []
        if len(PLAYERS.index) > 0:
            for i, player in enumerate(list(map(lambda x: Player(x[0], x[1], x[2], x[3]), list(PLAYERS.values)))):
                self.add_row(i, player)
        else:
            self.add_row(0)

    def button_frame(self, i):
        button_frame = tk.Frame(self)
        delete = tk.Button(button_frame, text=" - ", command=lambda: self.delete_row(i))
        add = tk.Button(button_frame, text=" + ", command=lambda: self.add_row(i))
        delete.pack(side="left")
        add.pack(side="left")
        return button_frame

    def add_row(self, row, player=None):
        # Name entry
        name = tk.Entry(self, validate="key")
        if player is not None:
            name.insert(0, player.name)

        # Rating entry
        rating = tk.Entry(self, validate="key", validatecommand=(self.register(self.validate_rating), "%P"))
        if player is not None:
            rating.insert(0, player.rating)

        # Skip entry
        skipping = tk.BooleanVar()
        skip = tk.Checkbutton(self, variable=skipping, onvalue=True, offvalue=False)
        if player is not None:
            skipping.set(player.oversidder)

        currId = str(uuid.uuid4())
        if player is not None:
            currId = player.id

        self.entries.insert(row, [name, rating, skip, skipping, currId])
        for name, rating, skip, skipping, id in self.entries:
            name.grid_forget()
            rating.grid_forget()
            skip.grid_forget()
        for button_frame in self.buttons:
            button_frame.grid_forget()
        self.buttons = []
        for i, (name, rating, skip, skipping, id) in enumerate(self.entries):
            button_frame = self.button_frame(i + 1)
            self.buttons.append(button_frame)
            name.grid(row=i, column=0, stick="nsew")
            rating.grid(row=i, column=1, stick="nsew")
            skip.grid(row=i, column=2, stick="nsew")
            button_frame.grid(row=i, column=3, stick="nsew")

    def delete_row(self, i):
        if len(self.entries) > 1:
            for name, rating, skip, skipping, id in self.entries:
                name.grid_forget()
                rating.grid_forget()
                skip.grid_forget()
            for button_frame in self.buttons:
                button_frame.grid_forget()
            self.buttons = []
            del self.entries[i - 1]
            for i, (name, rating, skip, skipping, id) in enumerate(self.entries):
                button_frame = self.button_frame(i + 1)
                self.buttons.append(button_frame)
                name.grid(row=i, column=0, stick="nsew")
                rating.grid(row=i, column=1, stick="nsew")
                skip.grid(row=i, column=2, stick="nsew")
                button_frame.grid(row=i, column=3, stick="nsew")

    def get(self):
        '''Return a list of lists, containing the data in the table'''
        result = []
        for name, rating, skip, skipping, id in self.entries:
            current_row = []
            current_row.append(name.get())
            rating = rating.get()
            if not (len(rating) > 0):
                current_row.append(0)
            else:
                current_row.append(int(rating))
            current_row.append(skipping.get())
            current_row.append(id)
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
        footer = PlayersFooter(parent, body.interior)
        header.pack(side="top", fill="both")  # , expand=True)
        body.pack(side="top", fill="both", expand=True)
        footer.pack(side="top", fill="both")  # , expand=True)


class ResultsFrame(tk.Frame):
    def __init__(self, parent, pairings, body, round):
        tk.Frame.__init__(self, parent)
        self.entries = []
        self.parent = parent
        self.body = body
        self.round = round
        self.pairings = pairings
        p1Header = tk.Label(self, text="Spiller 1")
        p1Header.grid(row=0, column=1)
        drawHeader = tk.Label(self, text="Uafgjort")
        drawHeader.grid(row=0, column=3)
        p2Header = tk.Label(self, text="Spiller 2")
        p2Header.grid(row=0, column=5)
        for i in range(7):
            self.grid_columnconfigure(i, weight=1)
        for i, match in enumerate(pairings):
            if match[0].id != 'Oversidder' and match[1].id != 'Oversidder':
                p1WinVar = tk.BooleanVar()
                p2WinVar = tk.BooleanVar()
                drawVar = tk.BooleanVar()

                def reset_p1():
                    p2WinVar.set(False)
                    drawVar.set(False)

                def reset_p2():
                    p1WinVar.set(False)
                    drawVar.set(False)

                def reset_draw():
                    p1WinVar.set(False)
                    p2WinVar.set(False)

                p1 = tk.Checkbutton(self, variable=p1WinVar, command=reset_p1)
                p1.grid(row=i + 1, column=0)
                p1Name = tk.Label(self, text=match[0].name)
                p1Name.grid(row=i + 1, column=1)
                draw = tk.Checkbutton(self, variable=drawVar, command=reset_draw)
                draw.grid(row=i + 1, column=3)
                p2 = tk.Checkbutton(self, variable=p2WinVar, command=reset_p2)
                p2.grid(row=i + 1, column=6)
                p2Name = tk.Label(self, text=match[1].name)
                p2Name.grid(row=i + 1, column=5)
                self.entries.append([i, p1WinVar, p2WinVar, drawVar])

        self.grid_columnconfigure(0, weight=1)
        save = tk.Button(self, text="Gem", command=self.save)
        save.grid(row=len(pairings) + 1, column=3)

    def save(self):
        global PLAYERS
        global MATCHES

        if len(self.entries) > 0 and not all(list(map(lambda x: x[1].get() or x[2].get() or x[3].get(), self.entries))):
            return

        for matchIndex, p1WinVar, p2WinVar, drawVar in self.entries:
            if p1WinVar.get():
                winnerId = self.pairings[matchIndex][0].id
                p1Outcome = 1
                p2Outcome = 0
            elif p2WinVar.get():
                winnerId = self.pairings[matchIndex][1].id
                p1Outcome = 0
                p2Outcome = 1
            else:
                winnerId = ""
                p1Outcome = 0.5
                p2Outcome = 0.5

            new_row = pd.DataFrame({
                'sessionId': SESSION_ID,
                'round': self.round,
                'p1Id': self.pairings[matchIndex][0].id,
                'p2Id': self.pairings[matchIndex][1].id,
                'winnerId': winnerId,
                'p1Rating': self.pairings[matchIndex][0].rating,
                'p2Rating': self.pairings[matchIndex][1].rating}, index=[0])
            MATCHES = pd.concat([new_row, MATCHES.loc[:]]).reset_index(drop=True)

            if 'Oversidder' != self.pairings[matchIndex][0].id and 'Oversidder' != self.pairings[matchIndex][1].id:
                p1NewRating = compute_rating_change(self.pairings[matchIndex][0].rating,
                                                    self.pairings[matchIndex][1].rating, p1Outcome)
                p2NewRating = compute_rating_change(self.pairings[matchIndex][1].rating,
                                                    self.pairings[matchIndex][0].rating, p2Outcome)
                PLAYERS.loc[PLAYERS['id'] == self.pairings[matchIndex][0].id, 'rating'] = self.pairings[matchIndex][
                                                                                              0].rating + p1NewRating
                PLAYERS.loc[PLAYERS['id'] == self.pairings[matchIndex][1].id, 'rating'] = self.pairings[matchIndex][
                                                                                              1].rating + p2NewRating

        self.body.refresh_entries()
        save_db()
        self.parent.destroy()
        self.parent.update()


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
    def __init__(self, parent, body):
        tk.Frame.__init__(self, parent)
        self.body = body
        self.new_round_btn = tk.Button(self, text="Ny runde", font='Helvetica 16 bold', command=self.new_round)
        self.save_db_btn = tk.Button(self, text="Gem", font='Helvetica 16 bold', command=self.save)
        self.new_round_btn.pack()
        self.save_db_btn.pack()
        self.matchmaker = MatchMaker()
        self.results = None
        self.prettyView = None

    def save(self):
        self.body.refresh_df()
        save_db()

    def new_round(self):
        if (self.results is not None and self.results.winfo_exists() == 1) or (
                self.prettyView is not None and self.prettyView.winfo_exists() == 1):
            return

        self.body.refresh_df()
        matches = self.matchmaker.get_matches()
        round = self.matchmaker.get_round()
        self.results = tk.Toplevel()
        self.results.title(f"Resultater for runde {round}")
        resFrame = ResultsFrame(self.results, matches, self.body, round)
        resFrame.pack()

        self.prettyView = tk.Toplevel(self)
        self.prettyView.geometry("1280x720")
        self.prettyView.title(f"Runde {round}")
        bg = ImageTk.PhotoImage(file=resource_path("bg.png"))
        canvas = tk.Canvas(self.prettyView, width=700, height=3500)
        canvas.pack(fill=BOTH, expand=True)
        canvas.create_image(0, 0, image=bg, anchor='nw')

        global width_before
        width_before = 0
        global height_before
        height_before = 0

        def resize_image(e):
            global image, resized, image2, height_before, width_before

            if e.height != height_before or e.width != width_before:
                # open image to resize it
                image = Image.open(resource_path("bg.png"))
                # resize the image with width and height of root
                resized = image.resize((e.width, e.height), Image.LANCZOS)

                image2 = ImageTk.PhotoImage(resized)
                canvas.create_image(0, 0, image=image2, anchor='nw')
                canvas.create_text(math.floor(e.width * 2 / 6), math.floor(e.height * 1 / 15), anchor="center",
                                   text="Hvid", font=("Josefin Sans", 36), fill='#FFFFFF')
                canvas.create_text(math.floor(e.width * 4 / 6), math.floor(e.height * 1 / 15), anchor="center",
                                   text="Sort", font=("Josefin Sans", 36), fill='#FFFFFF')
                for i, match in enumerate(matches):
                    canvas.create_text(math.floor(e.width * 1 / 6), math.floor(e.height * 2 / 15) + i * 45,
                                       anchor="center",
                                       text=f"Bræt {i + 1}", font=("Josefin Sans", 26), fill='#FFFFFF')


                    p1_previous_matches = MATCHES.loc[
                        ((MATCHES['p1Id'] == match[0].id) | (MATCHES['p2Id'] == match[0].id))]
                    p1Wins = p1_previous_matches.loc[p1_previous_matches['winnerId'] == match[0].id]
                    p1Draws = p1_previous_matches.loc[p1_previous_matches['winnerId'] == ""]
                    p1Losses = p1_previous_matches.loc[p1_previous_matches['winnerId'] != match[0].id]
                    p1_score_str = f"{len(p1Wins.index)}-{len(p1Draws.index)}-{len(p1Losses.index)}"
                    canvas.create_text(math.floor(e.width * 2 / 6), math.floor(e.height * 2 / 15) + i * 45,
                                       anchor="center",
                                       text=f"{match[0].name} ({match[0].rating} {p1_score_str})", font=("Josefin Sans", 26),
                                       fill='#FFFFFF')

                    canvas.create_text(math.floor(e.width * 3 / 6), math.floor(e.height * 2 / 15) + i * 45,
                                       anchor="center",
                                       text=f"vs", font=("Josefin Sans", 26), fill='#FFFFFF')

                    p2_previous_matches = MATCHES.loc[
                        ((MATCHES['p1Id'] == match[1].id) | (MATCHES['p2Id'] == match[1].id))]
                    p2Wins = p2_previous_matches.loc[p2_previous_matches['winnerId'] == match[1].id]
                    p2Draws = p2_previous_matches.loc[p2_previous_matches['winnerId'] == ""]
                    p2Losses = p2_previous_matches.loc[p2_previous_matches['winnerId'] != match[1].id]
                    p2_score_str = f"{len(p2Wins.index)}-{len(p2Draws.index)}-{len(p2Losses.index)}"
                    canvas.create_text(math.floor(e.width * 4 / 6), math.floor(e.height * 2 / 15) + i * 45,
                                       anchor="center",
                                       text=f"{match[1].name} ({match[1].rating} {p2_score_str})", font=("Josefin Sans", 26),
                                       fill='#FFFFFF')
                width_before = e.width
                height_before = e.height

        self.prettyView.bind("<Configure>", resize_image)


load_db()
root = tk.Tk()
root.geometry("1000x500")
root.title("Bønderne MatchMaker by In-House Geek CB")
PlayersUI(root)
root.mainloop()
