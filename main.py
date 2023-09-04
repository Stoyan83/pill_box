import tkinter as tk
import view
import controller
import models


def main():
    root = tk.Tk()
    root.withdraw()
    view_instance = view.View(root)
    model_instance = models.Medicine()
    controller_instance = controller.Controller(view=view_instance, model=model_instance)
    view_instance.controller = controller_instance
    root.mainloop()

if __name__ == "__main__":
    main()
