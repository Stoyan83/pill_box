import tkinter as tk
import view
import controller
import models

def main():
    root = tk.Tk()
    view_instance = view.View(root)
    model_instance = models.Client()
    controller.Controller(view=view_instance, model=model_instance)
    root.mainloop()

if __name__ == "__main__":
    main()
