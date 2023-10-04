# External Libraries
import tkinter as tk

# Local Modules
from menu_window import MenuWindow

if __name__ == '__main__':
    root = tk.Tk()
    app = MenuWindow(master=root)
    app.mainloop()