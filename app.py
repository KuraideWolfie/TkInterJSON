from src.gui.main import WindowManager
from tkinter import TOP, BOTTOM, LEFT, RIGHT, Canvas, messagebox

if __name__ == "__main__":
    with open('./src/gui/test.json', 'r') as fr:
        man = WindowManager.build(''.join(fr.readlines()))
        man.getWindow('winA').run()