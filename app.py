from src.gui.main import Window, Menu
from tkinter import TOP, BOTTOM, LEFT, RIGHT, Canvas, messagebox

def test():
    messagebox.showinfo("Hello world!", "Giggity")

def test2(self):
    messagebox.showwarning("Oh no!", "Get outta here")

if __name__ == "__main__":
    with open('./src/gui/test.json', 'r') as fr:
        win = Window.buildRaw(''.join(fr.readlines()))
        win.run()
    
    menu = Menu('mnuMain', '', '', {'tearoff': 0}, [
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
    commands = [ ('test2', test2) ]
    widgets = {
        "frames" : [
            {
                "name" : "frmOne",
                "geoMode" : "pack",
                "geoOptions" : {},
                "options" : {}
            }
        ],
        "panes" : [
            {
                "name" : "pane1",
                "geoMode" : "pack",
                "geoOptions" : { "fill" : 'both', "expand" : 1 },
                "options" : {}
            }
        ],
        "buttons" : [
            {
                "name" : "pane1Btn",
                "root" : "pane1",
                "geoMode" : "pack",
                "geoOptions" : { "side" : "right" },
                "options" : { "text" : "GIG" }
            },
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
        ],
        "canvases" : [
            {
                "name" : "canTest",
                "geoMode" : "place",
                "geoOptions" : {
                    "x" : 200,
                    "y" : 200
                },
                "options" : {
                    "width" : 128,
                    "height" : 64
                },
                "strokes" : [
                    { "type" : "line", "unnamed" : [ 4, 4, 124, 4, 124, 60, 4, 60, 4, 4 ], "named" : { "arrow" : "last", "tags" : [ 'example' ] } },
                    { "type" : "oval", "unnamed" : [ 10, 10, 40, 40 ] },
                    { "type" : "rectangle", "unnamed" : [ 12, 12, 20, 20 ], "named" : { "fill" : "red", "tags" : [ 'example' ] } }
                ]
            }
        ]
    }

    win : Window = Window.build(menu=menu, com=commands, widgets=widgets)
    win.run()
