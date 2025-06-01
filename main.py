from gui import SmartHomeGUI
import tkinter as tk

def main():
    root = tk.Tk()
    app = SmartHomeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()