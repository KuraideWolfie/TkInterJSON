from src.gui.main import Window, Menu
from tkinter import TOP, BOTTOM, LEFT, RIGHT, Canvas, messagebox

def test():
    messagebox.showinfo("Hello world!", "Giggity")

def test2(self):
    messagebox.showwarning("Oh no!", "Get outta here")

if __name__ == "__main__":
    with open('./src/gui/test.json', 'r') as fr:
        win = Window.build(''.join(fr.readlines()))
        win.run()

    win = Window(480, 320, "PUI Test")
    win.addMenu(
        Menu('mnuMain', '', '', {'tearoff': 0}, [
            Menu('mnuMain_File', 'cascade', 'File', {'tearoff': 0}, [
                Menu('mnuMain_File_New', 'command', 'New', {'command': test}),
                Menu('mnuMain_File_Sep1', 'separator'),
                Menu('mnuMain_File_Exit', 'command', 'Exit!', {'command': test})
            ]),
            Menu('mnuMain_Test', 'cascade', 'Test', {'tearoff': 0}, [
                Menu('mnuMain_Test_Check', 'checkbutton', 'Checky', {'isOn': False, 'onvalue': 1, 'offvalue': 0, 'variable': 'mtcVariable' }),
                Menu('mnuMain_Test_Radio', 'radiobutton', 'Rady', {'value': 30.2, 'variable': 'mtrVariable', 'command': test}),
                Menu('mnuMain_Test_Cascade', 'cascade', 'Cascade test', {'tearoff': 0}, [
                    Menu('mnuMain_Test_Cascade_Sep1', 'separator')
                ])
            ])
        ])
    ).addCommands(
        [ ('test2', test2) ]
    ).addWidgets({
        "frames" : [
            {
                "name" : "frmOne",
                "geoMode" : "pack",
                "geoOptions" : {},
                "options" : {}
            }
        ],
        "buttons" : [
            {
                "name" : "btnOne",
                "geoMode" : "place",
                "geoOptions" : {
                    "x" : 16,
                    "y" : 32
                },
                "options" : {
                    "text" : "test",
                    "width" : 10,
                    "height" : 10,
                    "command" : 'test2'
                }
            },
            {
                "name" : "frmOne_btnOne",
                "root" : "frmOne",
                "geoMode" : "pack",
                "geoOptions" : {
                    "side" : "left"
                },
                "options" : {
                    "text" : "test 2",
                    "fg" : "blue",
                    "command" : test
                }
            }
        ],
        "labels": [
            {
                "name" : "lblOne",
                "geoMode" : "place",
                "geoOptions" : {
                    "x" : 48,
                    "y" : 32
                },
                "options": {
                    "text" : "I'm a label",
                    "fg" : "red"
                }
            }
        ]
    }).run()
