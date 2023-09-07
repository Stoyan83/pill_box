import tkinter as tk
from tkinter import ttk


class WindowUtils:
    """
        Note:
             Centers the window in the middle of the screen.
    """
    @staticmethod
    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"{width}x{height}+{x}+{y}")
