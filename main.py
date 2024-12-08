import tkinter as tk
from filebin.filebin import FilebinGUI

def main():
    root = tk.Tk()
    app = FilebinGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()