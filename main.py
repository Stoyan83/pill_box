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
    session_model = models.SessionManager()
    medicine_model = models.Medicine(session=session)
    controller_instance = controller.Controller(view=view_instance, medicine_model=medicine_model, session_model=session_model)
    view_instance.controller = controller_instance
    WindowUtils.center_window(root, 1200, 800)
    root.mainloop()
    models.SessionManager.close_session()


if __name__ == "__main__":
    main()
