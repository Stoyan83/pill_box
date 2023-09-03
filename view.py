import tkinter as tk
from tkinter import ttk


class View():
    def __init__(self, master,  controller=None):
        self.master = master
        self.master.title("PillBox")
        self.controller = controller

        self.load_widgets()

    def load_widgets(self):
        self.label = ttk.Label(self.master, text="Hello")
        self.label.pack()
        self.label = ttk.Label(self.master, text="World")
        self.label.pack()
