# Project Details
## Project name
TkInterJSON

## Project Author(s)
Matthew Morgan

## Project Description
`Tkinter` is a powerful Python 3 library that allows a user to generate graphical user interfaces by, initially, instantiating a `Tk` instance, and assigning other windows (aka `Toplevel`s) or widgets (such as `Button`s) to that instance as a parent, otherwise defined a 'root'. For instance, the following is a simple TKinter program with a single button _"Click Me"_ that will show a simple, popup message when clicked.

```PYTHON
from tkinter import Tk, Button, messagebox

def com(): messagebox.showinfo('Title', 'I was clicked!')

root = Tk()
root.geometry('480x320')
root.title("Window!")

btn = Button(root, text="Click Me", fg="blue", command=com)
btn.pack(fill='both', expand=1)

root.mainloop()
```

While for simple interfaces tkinter offers an elegant definition of GUIs, undoubtedly a beginner using TK will become fast lost in having numerous variables defined that store all the widgets and sub-elements of those widgets (for instance, a `Canvas` and its associated elements defined using `create_*()` functions).

The goal of this project is to, in a sense, -simplify- the definition and generation of GUI windows and provide a basic window management system that abstracts the functionality of tkinter with its own API. As such, I present **TkInterJSON**. Defining the same, above project is as simple as this:

```PYTHON
from tkinter import messagebox
from src.gui.main import WindowManager

def com(): messagebox.showinfo('Title', 'I was clicked!')

man = WindowManager.build(
    {
        "root" : {
            "win" : { "width" : 480, "height" : 320, "title" : "Window!" },
            "widgets" : {
                "buttons" : [
                    {
                        "name" : "btn",
                        "geoMode" : "pack",
                        "geoOptions" : { "fill" : "both", "expand" : 1 },
                        "options": { "text" : "Click Me", "fg" : "blue", "command" : com }
                    }
                ]
            }
        }
    }
)

man.getWindow('root').run()
```

To refer to the widgets / components of the interface, it's as easy as a line such as `man.getWindow('root').buttons.getWidget('btn')`, where the hierarchy established is manager -> window -> widget type -> widget. The indentation of JSON versus all widgets being lined up in-source also assists in readability.