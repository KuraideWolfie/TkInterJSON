import tkinter
from tkinter import messagebox
from tkinter import ttk
import json
import types

GEOMETRY_MODES = [ 'place', 'pack', 'grid', 'none' ]
VARIABLES = { "StringVar" : tkinter.StringVar, "IntVar" : tkinter.IntVar, "DoubleVar" : tkinter.DoubleVar, "BooleanVar" : tkinter.BooleanVar, "Variable" : tkinter.Variable }
TK = None

class Menu():
  """
      Menu is a simple abstraction of menu properties as used in `Window.addMenu()`, including
      the type of the menu entry, the label, and options/children. The `children` property should
      be a collection of either dictionaries that represent menu entries, or instances of Menu.

      Valid types for a Menu's mType are: `separator`, `command`, `checkbutton`, `radiobutton`, and
      `cascade`, as defined by tkinter.
  """

  def __init__(self, name, mType, label=None, options={}, children={}):
    self.name = name
    self.mType = mType
    self.label = label
    self.options = options
    self.children = children
  
  def asDict(self):
    return { 'type' : self.mType, 'label' : self.label, 'options' : self.options, 'children' : self.children }

class WidgetCollection():
  """
      WidgetCollection represents a set of widgets that are all of the same class. It bundles
      up the creation of widgets, placement of them, and reconfiguration. For example, a
      WidgetCollection may handle all instances of tkinter.Button.

      Actions:
      + Check for widgets using `hasWidget()`
      + Get widgets and metadata using `getWidget()` and `getMeta()`
      + Add a new widget of the collection's type using `addWidget()`
      + Reconfigure widget properties using `configure()`
  """

  def __init__(self, _parent, _class):
    self.widgets = { }
    self.meta = { }
    self._parent = _parent
    self._class = _class

  def hasWidget(self, name): return name in self.widgets

  def hasMeta(self, name): return name in self.meta

  def getWidget(self, name): return None if not self.hasWidget(name) else self.widgets[name]

  def getMeta(self, name):
    """
        Gets metadata for a widget in the collection.

        Keyword arguments:
        + `name` The name of the widget to fetch metadata for

        Returns: None if metadata doesn't exist or the widget isn't found, or stored metadata if found
    """

    if self.hasWidget(name):
      if name in self.meta:
        return self.meta[name]
      else:
        return None
    else:
      return None
  
  def setMeta(self, name, meta):
    if self.hasWidget(name):
      self.meta[name] = meta
    else:
      raise Exception(f"No widget with the name '{name}' exists in this window.")

  def addWidget(self, name, root=None, geoMode='none', geoOptions={}, options={}, state=None):
    """
        Adds a widget to the widget collection, registering the appropriate parent and toggling
        geometry options for the widget.

        Keyword arguments:
        + `name` The name of the widget
        + `root` The parent of the widget -- None for the window, or another widget
        + `geoMode` The geometry mode to use on the widget -- one of 'place', 'grid', 'pack', or 'none'
        + `geoOptions` The geometry options to supply the geometry functions
        + `options` The options to use in construction of the widget. These are based on widget type
        + `state` The state to set the widget to -- a list of options

        The default geometry mode is 'none', which means that no geometry functions are called. The 'none'
        option is useful for widgets like Menus, etc.

        Returns: The widget after its construction and geometry creation
    """

    # Raise an exception if an invalid geometry mode is selected
    # Raise an exception if the widget name already exists
    if not geoMode.lower() in GEOMETRY_MODES:
      raise Exception(f"Geometry mode {geoMode} is not valid mode. Valid: {GEOMETRY_MODES}")

    if not name in self.widgets:
      if self._class == tkinter.Toplevel:
        self.widgets[name] = self._class(**options)
      else:
        self.widgets[name] = self._class(root if root else self._parent, **options)
    else:
      raise Exception(f"Widget {str(self._class).split(' ')[1][:-1]}, Name '{name}' already exists")

    # Execute the proper geometry function based on the mode selected and given geometry options
    mode = geoMode.lower()
    if mode == 'place':
        self.widgets[name].place(**geoOptions)
    elif mode == 'pack':
        self.widgets[name].pack(**geoOptions)
    elif mode == 'grid':
        self.widgets[name].grid(**geoOptions)
    
    # Modify the state
    if state and state.__class__.__name__ in ['list', 'tuple']:
      self.widgets[name].state(state)

    return self.widgets[name]

  def deleteWidget(self, name):
    """
        Accepts a widget name, and deletes it.

        Keyword arguments:
        + `name` The name of the widget to be deleted

        Returns: Self for chaining
    """

    if hasWidget(name):
      wid = self.getWidget(name)

      del self.widgets[name]
      if name in self.meta: del self.meta[name]
      wid.delete()
    
    return self
  
  def configure(self, name, **options):
    """
        Reconfigures a widget using the given options

        Keyword arguments:
        + `name` The name of the widget to configure
        + `options` named set of arguments to pass to the widget's configure function

        Returns: Self for chaining
    """

    if self.hasWidget(name): self.getWidget(name).configure(**options)
    return self

class WindowManager():
  """
      WindowManager is a simple class that collects together a series of windows. It
      updates a window to refer to itself when added such that windows can intercommunicate
      through their commands or other actions (such as a button on window 'A' changing the
      text of a label on window 'B').
  """

  def __init__(self):
    self.windows = { }
  
  def hasWindow(self, name): return name in self.windows

  def getWindow(self, name): return None if not self.hasWindow(name) else self.windows[name]

  def addWindow(self, name, win):
    """
        Adds a window to this manager under the given name.

        Keyword arguments:
        + `name` The name that will be used in reference to the window added
        + `win` The Window instance to be associated with the name

        Returns: Self for chaining
    """

    if not self.hasWindow(name):
      self.windows[name] = win
      win.setManager(self)
    else:
      raise Exception(f"A window named '{name}' already exists for this manager")
    
    return self
  
  def createWindow(self, name, win):
    """
        Adds a window to this manager from raw JSON-formatted text.

        Keyword arguments:
        + `name` The name to associate with the newly-built window
        + `win` The raw JSON-formatted text representing the window to be added

        Returns: Self for chaining
    """

    self.addWindow(name, Window.buildFromDict(win))
    return self
  
  def removeWindow(self, name):
    """
        Removes a window from this manager.

        Keyword arguments:
        + `name` The name of the window to remove

        Returns: The Window instance associated with `name`, or None if not found
    """

    if self.hasWindow(name):
      win = self.getWindow(name)
      win.setManager()
      del self.windows[name]
      return win
    else:
      return None
  
  @staticmethod
  def build(dic):
    """
        Builds a WindowManager from a dictionary of name-window entries, where each window is a
        dictionary of information that `Window.build()` can parse.

        Keyword arguments:
        + `dic` The dictionary of name-windowdict pairs

        Returns: The WindowManager generated from the dictionary
    """

    man = WindowManager()

    for win in sorted(dic):
      man.createWindow(win, dic[win])

    return man

  @staticmethod
  def buildRaw(raw=''):
    """
        Builds a WindowManager from raw, JSON-formatted text. The format should be a dictionary of
        name-Window pairs, where 'Window' is JSON-formatted text that `Window.build()` can parse.

        Keyword arguments:
        + `raw` JSON-formatted text that can build a WindowManager

        Returns: The manager built from the JSON
    """

    if not raw: return None
    else:
      dic = json.loads(raw)
      man = WindowManager()

      for win in sorted(dic):
        man.createWindow(win, dic[win])

      return man

class Window():
  """
      Window is a one-stop shop for generating tkinter graphical user interfaces, including the
      parsing of raw JSON to generate an interface, and holding variables and the widgets of the
      interface in a uniform, organized manner. Windows may be built using the `build(json)`
      function, but the most specific way to generate a window is to instantiate the Window class
      and use its functions...

      Short, and sweet:
      ```
      Window(width, height, title, icon) # Creates the window
      .addMenu(menu)                     # Sets up a menu
      .addCommands(cmdList)              # Associates python functions with names as 'commands'
      .addWidgets(widgets)               # Builds the interface using JSON-formatted properties
      .run()                             # Opens the interface using the mainloop() function
      ```

      Extra functionality in the way of adding raw Python code (as strings) for commands is
      available as `addCommandsRaw(...)`, but is not recommended versus the above method due to
      potential security issues and memory management.

      Extra functionality in the way of managing variables used in widgets is available; however,
      once a variable is added, it may NOT be removed using the API.
  """

  def __init__(self, width=480, height=320, title="PUI", icon=""):
    # Instantiate TK root if not already created; otherwise, generate a Toplevel
    global TK

    if not TK:
      TK = tkinter.Tk()
      self.gui = TK
    else:
      self.gui = tkinter.Toplevel(TK)
      self.hide()

    # Instantiation of window
    self.guiIcon = None
    self.variables = { }
    self.manager = None

    self.messageboxes = messagebox
    self.buttons = WidgetCollection(self.gui, tkinter.Button)
    self.canvases = WidgetCollection(self.gui, tkinter.Canvas)
    self.checkbuttons = WidgetCollection(self.gui, tkinter.Checkbutton)
    self.textboxes = WidgetCollection(self.gui, tkinter.Entry)
    self.frames = WidgetCollection(self.gui, tkinter.Frame)
    self.labels = WidgetCollection(self.gui, tkinter.Label)
    self.listboxes = WidgetCollection(self.gui, tkinter.Listbox)
    self.menubuttons = WidgetCollection(self.gui, tkinter.Menubutton)
    self.menus = WidgetCollection(self.gui, tkinter.Menu)
    self.messages = WidgetCollection(self.gui, tkinter.Message)
    self.radiobuttons = WidgetCollection(self.gui, tkinter.Radiobutton)
    self.scales = WidgetCollection(self.gui, tkinter.Scale)
    self.scrollbars = WidgetCollection(self.gui, tkinter.Scrollbar)
    self.textareas = WidgetCollection(self.gui, tkinter.Text)
    self.windows = WidgetCollection(self.gui, tkinter.Toplevel)
    self.spinboxes = WidgetCollection(self.gui, tkinter.Spinbox)
    self.panes = WidgetCollection(self.gui, tkinter.PanedWindow)
    self.labelframes = WidgetCollection(self.gui, tkinter.LabelFrame)
    self.progressbars = WidgetCollection(self.gui, ttk.Progressbar)
    self.comboboxes = WidgetCollection(self.gui, ttk.Combobox)
    self.labelscales = WidgetCollection(self.gui, ttk.LabeledScale)
    self.spinboxes = WidgetCollection(self.gui, ttk.Spinbox)
    self.treeviews = WidgetCollection(self.gui, ttk.Treeview)
    self.sizegrips = WidgetCollection(self.gui, ttk.Sizegrip)
    self.tabbedpane = WidgetCollection(self.gui, ttk.Notebook)

    self.gui.geometry(f"{width}x{height}")
    self.gui.title(title)
    self.setIcon(icon)

  @property
  def categories(self):
    """ Returns a dictionary of (category, WidgetCollection) pairs for the window. """
    
    return dict([(e, self.__dict__[e]) for e in self.__dict__ if self.__dict__[e].__class__.__name__ == 'WidgetCollection' ])

  def run(self): self.gui.mainloop()

  def setManager(self, man=None):
    if man.__class__.__name__ == 'WindowManager':
      self.manager = man
    else:
      raise Exception("The provided parameter is not an instance of WindowManager.")

  def setIcon(self, icon=""):
    """
        Sets the icon for the window. Does nothing if the provided argument is an empty string

        Keyword arguments:
        + `icon` A string representing the path to the icon to be used
        
        Returns: Self for chaining
    """

    if icon:
      print(f"'{icon}'")
      self.guiIcon = tkinter.PhotoImage(file=icon)
      self.gui.iconphoto(False, self.guiIcon)
    
    return self

  def addMenuRaw(self, name, options={ 'tearoff': 0 }, children=[]):
    """
        Generates a menu for the GUI window based off of a name, set of options, and series of
        defined children elements. There are two methods for specifying a menu...
        1. Define a Menu instance, providing the name, type as `''`, label as `''`, options, and
           a list of children Menu instances with defined types/labels
        2. Define a raw JSON-formatted string of the given form, as used in `buildRaw()`:
          + ```{ "type" : "", "label" : "", "options": { }, "children" : { }```
          + Where:
            + `type` is a valid Menu type -- `cascade`, `command`, `separator`, `checkbutton`, `radiobutton`
            + `label` is the string to show for the entry on the menu
            + `options` is the named values passed to the `add_*` functions for a menu
              + Bear in mind that `"tearoff" : 0` is optimal to include with `cascade` types
              + Defining commands for menu entries doesn't necessarily have to be function pointers.
                Instead, string names representing commands added to the Window may also be used
            + `children` is a dictionary of name-data pairs of the same, above-defined form, or a
              list of children that are also Menu instances

        Keyword arguments:
        + `name` The name of the menu to be generated for the window
        + `options` The options for the menu
        + `children` Collection of `Menu()` instances or dictionaries defining children widgets

        Returns: Self for chaining
    """

    main : tkinter.Menu = self.menus.addWidget(name, options=options)

    # Reconfigure children collection to accomodate dictionaries and lists
    if 'dict' in str(type(children)):
      children = [(cName, children[cName]) for cName in children]
    elif 'list' in str(type(children)):
      children = [(child.name, child) for child in children]
    else:
      raise Exception("Unexpected collection type for children during menu creation")

    for cName, child in children:
      # Convert Menu instances to dictionaries for processing
      if child.__class__.__name__ != 'dict': child = child.asDict()

      # Associate commands in the window with commands in the menu unless a command is already assigned
      # This is discerned by checking the type of the command value is a function
      if child['type'] != 'separator':
        if 'command' in child['options'] and child['options']['command']:
          if not 'function' in str(type(child['options']['command'])):
            if self.hasCommand(child['options']['command']):
              child['options']['command'] = self.getCommand(child['options']['command'])
            else:
              raise Exception(f"There is no command named {child['options']['command']} in this window.")

      # Act based on child type
      if child['type'] == 'separator':
        main.add_separator()
      elif child['type'] == 'command':
        main.add_command(label=child['label'], **child['options'])
      elif child['type'] == 'checkbutton':
        # Associate the variable for the checkbox
        if self.hasVariable(child['options']['variable']):
          child['options']['variable'] = self.getVariable(child['options']['variable'])
        else:
          child['options']['variable'] = self.addVariable(child['options']['variable'], tkinter.BooleanVar, default=child['options']['isOn'])

        del child['options']['isOn']

        main.add_checkbutton(label=child['label'], **child['options'])
      elif child['type'] == 'radiobutton':
        # Associate the variable for the radiobutton
        if self.hasVariable(child['options']['variable']):
          child['options']['variable'] = self.getVariable(child['options']['variable'])
        else:
          var = str(type(child['options']['value'])).split("'")[1]
          if var == 'bool':
            var = tkinter.BooleanVar
          elif var == 'str':
            var = tkinter.StringVar
          elif var == 'int':
            var = tkinter.IntVar
          elif var == 'float':
            var = tkinter.DoubleVar
          else:
            raise Exception(f"The variable type for the variable '{child['options']['variable']}' is unknown.")

          child['options']['variable'] = self.addVariable(child['options']['variable'], var)

        main.add_radiobutton(label=child['label'], **child['options'])
      elif child['type'] == "cascade":
        self.addMenuRaw(cName, options=child['options'], children=child['children'])
        main.add_cascade(label=child['label'], menu=self.menus.getWidget(cName))
    
    self.gui.config(menu=main)
    return self

  def addMenu(self, menu: Menu = None):
    """
        Wrapper for `addMenuRaw()` which allows the root menu widget containing all children
        widget definitions to be used in a succinct, single call

        Keyword arguments:
        + `menu` The Menu to add to the window

        Returns: Self for chaining
    """

    # Premature return -- no menu provided
    if menu == None: return self

    dic = menu.asDict()
    self.addMenuRaw(menu.name, options=dic['options'], children=dic['children'])
    return self
  
  def deleteWidgets(self, widgets=[]):
    """
        Accepts a list of widget names and sequentially deletes them from the window. If a widget is
        not found, then an exception is raised indicating the window does not contain the widget

        Keyword arguments:
        + `widgets` A list of widget names as defined when adding widgets to the window

        Returns: Self for chaining
    """

    for widget in widgets:
      found = False

      for category in self.categories:
        if self.categories[category].hasWidget(widget):
          found = True
          self.categories[category].deleteWidget(widget)
      
      if not found:
        raise Exception(f"No widget with the name '{widget}' was found in the window.")
    
    return self

  def addWidgets(self, widgets):
    """
        Accepts a dictionary of (widget category, widget list) pairs that will be sequentially
        added to this Window. Widgets are specified using the given sample below:

        `{ "name" : "", "root" : "", "geoMode": "", "geoOptions": {}, "options": {}, "state" : [] }`

        Where:
        + `geoMode` is one of the three geometry function names, or 'none' for no placement
          + Function names: `place`, `pack`, and `grid`
        + `options` is name-based parameters passed to the widget's constructor
        + `state` is values to manipulate the widget's state to (such as 'readonly' for comboboxes)
        + `paneOptions` [optional] is named-based parameters given to PanedWindow's add function
        + `values` [optional] is a list of string entries defining a Combobox's selectable values
        + `strokes` [optional] is a list of dictionaries specifying stroke information for a Canvas
          + Form: `{ "type" : "", "unnamed" : [ ], "named" : { "tags" : [ ] } }`
          + Where:
            + `type` is any acceptable type of Canvas graphic, denoted by `create_*` functions
            + `unnamed` is a list of unnamed parameters passed at the front of the `create_*` functions
            + `named` is name-based parameters passed to `create_*`

        Widget categories are any type of widget defined by tkinter, including Button and Frame. The
        specification of these categories is simple -- in example: `'buttons': [ ... ]`. Any instance
        of 'variable' specified in the widget's options will be generated according to the name, type,
        and default value provided, as so: `{ "type" : "", "name" : "", "value" : <some value> }`

        Keyword arguments:
        + `widgets` The collection of widgets to add to this window

        Returns: Self for chaining
    """

    for category in widgets:
      if not category in self.categories:
        raise Exception(f"The category '{category}' is not valid for widgets.")

      for widget in widgets[category]:
        # Attempt to locate the parent widget for this widget
        # If there is no parent specified, defaults to the window
        # If there is a specified parent but it's not a string, assume its a widget
        if 'root' in widget and widget['root']:
          if 'str' in str(type(widget['root'])):
            for cat in self.categories:
              if self.categories[cat].hasWidget(widget['root']): widget['root'] = self.categories[cat].getWidget(widget['root'])
            
            if 'str' in str(type(widget['root'])):
              raise Exception(f"No widget with the name '{widget['root']}' was found to assign as parent.")
        else:
          widget['root'] = self.gui
        
        # Attempt to locate the command, if any
        # If there is a specified command but its not a string, assume its a function
        if 'command' in widget['options'] and widget['options']['command']:
          if 'str' in str(type(widget['options']['command'])):
            if self.hasCommand(widget['options']['command']):
              widget['options']['command'] = self.getCommand(widget['options']['command'])
            else:
              raise Exception(f"No command with the name '{widget['options']['command']}' exists for this window.")

        # Comb over the options and make variable replacements. If a variable already exists, it gets
        # used over creating a new variable
        for option in widget['options']:
          if 'variable' in option:
            global VARIABLES

            if widget['options'][option]['type'] in VARIABLES:
              if not self.hasVariable(widget['options'][option]['name']):
                self.addVariable(widget['options'][option]['name'], VARIABLES[widget['options'][option]['type']],
                  default = widget['options'][option]['value'] if 'value' in widget['options'][option] else None)

              widget['options'][option] = self.getVariable(widget['options'][option]['name'])
            else:
              raise Exception(f"The provided variable type {widget['options'][option]['type']} is invalid.")

        # Add the widget
        wid = self.__dict__[category].addWidget(
          widget['name'],
          widget['root'],
          widget['geoMode'],
          widget['geoOptions'],
          widget['options'],
          widget['state'] if 'state' in widget else None
        )

        # Add listbox options
        if 'listbox' == wid.__class__.__name__.lower():
          if 'values' in widget and widget['values'].__class__.__name__ in ['tuple', 'list']:
            wid.insert('end', *widget['values'])

        # Add the widget to the panedwindow if the parent is a PanedWindow
        if 'PanedWindow' == widget['root'].__class__.__name__: widget['root'].add(wid, **(widget['paneOptions'] if 'paneOptions' in widget else {}))

        # Take care of canvas painting
        if category == 'canvases':
          canvas: tkinter.Canvas = self.canvases.getWidget(widget['name'])
          types = {
            'line' : canvas.create_line,
            'rectangle' : canvas.create_rectangle,
            'oval' : canvas.create_oval,
            'polygon' : canvas.create_polygon,
            'arc' : canvas.create_arc,
            'image' : canvas.create_image,
            'text' : canvas.create_text
          }

          for stroke in widget['strokes']:
            # Perform the stroke using unnamed and named properties
            if stroke['type'] in types:
              obj = types[stroke['type']](*stroke['unnamed'], **(stroke['named'] if 'named' in stroke else {}))
            elif stroke['type'] == 'widget':
              # TODO Generate a new widget and associate with the canvas using create_image
              pass
            else:
              raise Exception(f"Invalid stroke type provided: '{stroke['type']}'")
    
    return self

  def hasVariable(self, name): return name in self.variables

  def getVariable(self, name):
    if self.hasVariable(name): return self.variables[name]
    else:
      return None

  def addVariable(self, name, _class, default=None):
    if not self.hasVariable(name):
      self.variables[name] = _class()

      if default: self.variables[name].set(default)

      return self.getVariable(name)
    else:
      raise Exception(f"Variable {name} already exists for this window")
  
  def hasCommand(self, name): return 'com_'+name in dir(self)

  def getCommand(self, name):
    if self.hasCommand(name): return getattr(self, 'com_'+name)
    else:
      return None
    
  def addCommand(self, name, com):
    """
        Accepts a name and function already-defined using Python, and binds the function to
        this window for execution in widgets that use it. A function should be defined with
        a header that includes `self` as the lone parameter, and should not return values.
        `self` in the context of said function will be this window.

        Keyword arguments:
        + `name` The name to represent the function `com` as
        + `com` The function, prior-defined, to bind to this Window for usage

        Returns: Self for chaining
    """

    if not self.hasCommand(name):
      setattr(self, 'com_'+name, types.MethodType(com, self))
    else:
      raise Exception(f"A command with the name '{name}' already exists for this window.")

    return self
  
  def addCommands(self, comList):
    """
        Wrapper for executing multiple calls of `addCommand()`

        Keyword arguments:
        + `comList` A list of (name, command) pairs for usage in `addCommand()`

        Returns: Self for chaining
    """

    for name, com in comList: self.addCommand(name, com)
    return self
  
  def addCommandRaw(self, name, com):
    """
        Accepts a raw, single-line string (using `\\n` as line separators) alongside a name,
        and generates a command bound to this Window. The spacing of each line should follow
        the same constraints as any other Python code, exempting the `def func(self)` line.

        Keyword arguments:
        + `name` The name of the command which the code in `com` should be represented by
        + `com` The raw Python code to execute when the command is called by a widget

        Returns: Self for chaining
    """

    if not self.hasCommand(name):
      parsed = '\n'.join([' '+ln for ln in com.split('\n')])
      _local = {}

      exec(f"def com_{name}(self):\n{parsed}", None, _local)

      for name, value in _local.items():
        setattr(self, name, types.MethodType(value, self))
    else:
      raise Exception(f"A command with the name '{name}' already exists for this window.")
  
    return self
  
  def addCommandsRaw(self, comList):
    """
        Wrapper for executing multiple calls of `addCommandRaw()`

        Keyword arguments:
        + `comList` A list of (name, code string) pairs for usage in `addCommandRaw()`

        Returns: Self for chaining
    """

    for name, com in comList: self.addCommandRaw(name, com)
    return self
  
  def addCommandsMixed(self, comList):
    """
        Wrapper for executing multiple calls to both `addCommandRaw()` and `addCommand()`.

        Keyword arguments:
        + `comList` A list of (name, code string or function) pairs

        Returns: Self for chaining
    """

    for name, com in comList:
      if 'str' == com.__class__.__name__:
        self.addCommandRaw(name, com)
      else:
        self.addCommand(name, com)
    return self
  
  def show(self):
    """
        Shows the window

        Returns: Self for chaining
    """

    if self.gui.state() in ['iconic', 'icon', 'withdrawn']:
      self.gui.deiconify()

    return self
  
  def minimize(self):
    """
        Hides the window from the screen by minimizing it

        Returns: Self for chaining
    """

    if not self.gui.state() in ['iconic', 'icon', 'withdrawn']:
      self.gui.iconify()
    
    return self
  
  def hide(self):
    """
        Removes the window from the screen without destroying it, instead of minimizing to
        an icon.

        Returns: Self for chaining
    """

    self.gui.withdraw()
    return self

  @staticmethod
  def build(width=480, height=320, title='PUI', icon=None, menu=None, com=[], widgets={}):
    """
        Builds a Window by shortening all critical function calls to this single call.

        Keyword arguments:
        + `width` The width of the window
        + `height` The height of the window
        + `title` The title text for the window
        + `icon` The filepath of the icon to be used for the window
        + `menu` A Menu instance for adding a menu to the window, or None for no menu
        + `com` The list of (name, function|code) pairs to associate with the window
        + `widgets` The dictionary of (category, widgetlist) pairs for adding widgets

        Returns: The Window built using the given parameters
    """

    return Window(width, height, title).setIcon(icon).addCommandsMixed(com).addMenu(menu).addWidgets(widgets)

  @staticmethod
  def buildFromDict(dic=None):
    if not dic: return None
    else:
      return Window.build(
        dic['win']['width'],
        dic['win']['height'],
        dic['win']['title'],
        dic['win']['icon']
          if 'icon' in dic['win'] else None,
        Menu(dic['menu']['name'], '', '', dic['menu']['options'], dic['menu']['children'])
          if 'menu' in dic else None,
        [(k, dic['commands'][k]) for k in dic['commands']]
          if 'commands' in dic else [],
        dic['widgets']
      )

  @staticmethod
  def buildRaw(raw=''):
    """ 
        Builds a Window from JSON-formatted text. In the simplest form, this format should be:

        ```
        { "win" : { "width" : 480, "height" : 320, "title" : "", "icon" : "" },
          "commands" : { "sample" : "print(\"Hello\")" },
          "menu" : { "name" : "", "options" : { "tearoff" : 0 }, "children" : { } },
          "widgets" : { } }
        ```

        Where:
        + `win` specifies the width, height, title, and icon filepath for the Window
        + `commands` is a set of name-code pairs, where code is Python code separated by line with \\n
        + `menu` is the entire structure of the 'File' menu at the top of the window,
        + `widgets` is a dictionary of category-widgetlist pairs for adding widgets to the Window

        Keyword arguments:
        + `raw` Raw JSON-formatted string that contains window, menu, command, and widget properties

        Returns: Window instance generated using the raw JSON string
    """

    return None if not raw else Window.buildFromDict(json.loads(raw))

      # TODO Event bindings for canvas children
      # TODO Modify canvas children using configure -- https://tkdocs.com/tutorial/canvas.html > Modifying Items
      # TODO Event bindings in BUILD and ADDEVENTS func, for window + widgets
