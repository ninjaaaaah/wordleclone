"""
My first application
"""
from random import random
from math import floor
import toga
from toga import Box, Label, Button, TextInput, MainWindow
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class WordleClone(toga.App):
    def startup(self):
        self._impl.create_menus = lambda *x, **y: None

        # application states
        self.gameover = 0
        self.words = (
            self.paths.app.joinpath(self.paths.app.parent, "words.txt")
            .read_text()
            .split("\n")
        )
        self.allowed = (
            self.paths.app.joinpath(self.paths.app.parent, "allowed_guesses.txt")
            .read_text()
            .split("\n")
        )
        self.word = self.words[floor(random() * len(self.words))]
        self.active_row = 0

        # creates the header containing the text field
        self.guess = TextInput(style=Pack(flex=1))
        header = Box(
            children=[
                Label("Guess: ", style=Pack(padding=5)),
                self.guess,
                Button("Guess!", on_press=self.validate, style=Pack(padding=(0, 5))),
            ],
            style=Pack(direction=ROW),
        )
        print(self.word)

        # creates the rows containing the tiles
        self.gamebox = Box(
            children=[
                Box(
                    children=[
                        Label(
                            "",
                            style=Pack(
                                padding=5,
                                height=50,
                                width=50,
                                font_weight="bold",
                                font_size=20,
                                background_color="white",
                                color="white",
                                text_align="center",
                                font_family="Segoe UI",
                            ),
                        )
                        for _ in range(5)
                    ],
                )
                for _ in range(6)
            ],
            style=Pack(direction=COLUMN, padding=(10, 0)),
        )

        # creates the keys of the keyboard interface
        self.first = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"]
        self.second = ["a", "s", "d", "f", "g", "h", "j", "k", "l"]
        self.third = ["ENTER", "z", "x", "c", "v", "b", "n", "m", "⌫"]
        button = Pack(height=50, width=40, padding=2, background_color="white")
        long_button = Pack(height=50, width=60, padding=2, background_color="white")
        self.keyboard = Box(
            children=[
                Box(
                    children=[
                        Button(c.upper(), style=button, on_press=self.press)
                        for c in self.first
                    ]
                ),
                Box(
                    children=[
                        Button(c.upper(), style=button, on_press=self.press)
                        for c in self.second
                    ]
                ),
                Box(
                    children=[
                        Button(
                            c.upper(),
                            style=(
                                button
                                if i != 0 and i != len(self.third) - 1
                                else long_button
                            ),
                            on_press=self.press,
                        )
                        for i, c in enumerate(self.third)
                    ]
                ),
            ],
            style=Pack(direction=COLUMN, alignment="center", padding=(10, 0)),
        )

        # reset button
        self.resetbutton = Button("Reset!", on_press=self.reset, enabled=False)

        # creates container of all components
        self.container = Box(
            children=[
                header,
                self.gamebox,
                self.resetbutton,
                self.keyboard,
            ],
            style=Pack(direction=COLUMN, alignment="center", padding=10),
        )

        self.main_window: MainWindow = MainWindow(title=self.formal_name)
        self.main_window.size = (500, 600)
        self.main_window.content = self.container
        self.main_window.show()

    def reset(self, button):
        self.gameover = 0
        self.active_row = 0
        self.word = self.words[floor(random() * len(self.words))]
        print(self.word)
        for row in self.gamebox.children:
            for tile in row.children:
                tile.style.background_color = "white"
                tile.text = " "
        for row in self.keyboard.children:
            for key in row.children:
                key.style.background_color = "white"
                key.style.color = "black"
        button.enabled = False

    def press(self, button):
        if button.label == "ENTER":
            self.validate("")
        elif button.label == "⌫":
            self.guess.value = self.guess.value[:-1]
        else:
            self.guess.value = self.guess.value + button.label

    def errorcheck(self):
        message = ""
        if len(self.guess.value) != 5:
            message = "Input does not consist of 5 characters!"
        elif not (self.guess.value.isalpha()):
            message = "Input consists of non-alphabet characters!"
        elif not (self.guess.value.lower() in self.allowed):
            message = "Word is not in the allowed guesses!"

        if message:
            self.guess.value = ""
            self.main_window.info_dialog("", message)
            return 1

    def colortile(self):
        for i, tile in enumerate(self.gamebox.children[self.active_row].children):
            tile.style.background_color = (
                "#6aaa64"
                if self.guess.value[i].lower() == self.word[i]
                else (
                    "#c9b458" if self.guess.value[i].lower() in self.word else "#787c7e"
                )
            )
            tile.text = self.guess.value[i].upper()

    def colorkey(self):
        for i, c in enumerate(self.guess.value):
            setBG = (
                "#6aaa64"
                if c.lower() == self.word[i]
                else (
                    "#c9b458" if self.guess.value[i].lower() in self.word else "#787c7e"
                )
            )

            if c.lower() in self.first:
                index = self.first.index(c.lower())
                self.keyboard.children[0].children[index].style.background_color = setBG
                self.keyboard.children[0].children[index].style.color = "white"
                continue

            if c.lower() in self.second:
                index = self.second.index(c.lower())
                self.keyboard.children[1].children[index].style.background_color = setBG
                self.keyboard.children[1].children[index].style.color = "white"
                continue

            if c.lower() in self.third:
                index = self.third.index(c.lower())
                self.keyboard.children[2].children[index].style.background_color = setBG
                self.keyboard.children[2].children[index].style.color = "white"
                continue

    def checkstate(self):
        self.active_row += 1
        message = ""
        if self.guess.value.lower() == self.word:
            message = "That's the word!"
        elif self.active_row == 6:
            message = f"The correct answer is {self.word}!"

        if not (message):
            return

        self.main_window.info_dialog("", message)
        self.gameover = 1
        self.resetbutton.enabled = True
        self.guess.value = ""

    def validate(self, _):
        if self.gameover:
            return
        if self.errorcheck():
            return

        self.colortile()
        self.colorkey()
        self.checkstate()


def main():
    return WordleClone()
