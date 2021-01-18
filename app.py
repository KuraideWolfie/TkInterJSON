from src.gui.main import WindowManager

if __name__ == "__main__":
    with open('./test.json', 'r') as fr:
        man = WindowManager.buildRaw(''.join(fr.readlines()))
        man.getWindow('winA').run()