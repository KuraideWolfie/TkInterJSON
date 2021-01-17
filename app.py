from src.gui.main import WindowManager

if __name__ == "__main__":
    with open('./src/gui/test.json', 'r') as fr:
        man = WindowManager.build(''.join(fr.readlines()))
        man.getWindow('winA').run()