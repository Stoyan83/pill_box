import tkinter as tk
from utils import WindowUtils
import view
import controller
import models


def main():
    root = tk.Tk()
    root.withdraw()
    view_instance = view.View(root)

    session = models.SessionManager.get_session()
    model_instance = models.Medicine(session=session)
    controller_instance = controller.Controller(view=view_instance, model=model_instance)
    view_instance.controller = controller_instance
    WindowUtils.center_window(root, 1000, 800)
    root.mainloop()
    models.SessionManager.close_session()


if __name__ == "__main__":
    main()
