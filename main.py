# using keyboard instead of pynput (seems to work better/fewer issues)
import pyperclip, sys, keyboard, mouse, time, os
from tkinter import *
from tkinter import ttk

# TODO: 1 - Gui History window and main window history has scroll bar
# 2 - When finished, migrate everything to ttkThemed, because it makes stuff look cooler

# Greys from darkest to Brightest
Colors = {
    'G1': '#404258',
    'G2': '#474E68',
    'G3': '#50577A',
    'G4': '#6B728E'
}

# Main Window
root = Tk()

'''
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path,relative_path)
'''


CPText = 'Copied Text Here'
TextLabel = Label(root, text=CPText).pack
ListOpen = False

# List to hold clipboard Text,
clipboard = [pyperclip.paste(), ]
UpdateString = StringVar(root, 'Updates Here')



def onCtrlC():
    time.sleep(0.1)  # If this runs too fast, it doesn't detect the copied text fast enough
    global CPText
    if pyperclip.paste() in clipboard:  # Check it's not already in the list (had a function for this, but python makes this ez)
        return
    clipboard.append(pyperclip.paste())
    UpdateLB(windowEntities['ITEMLIST'])
    UpdateString.set('item Copied')


# Just for testing
def clearList():
    if ListOpen:
        return
    clipboard.clear()
    ResetLB(windowEntities['ITEMLIST'])
    print(f'List Deleted: {clipboard}')
    UpdateString.set('List Cleared')


def ResetLB(listbox):
    listbox.delete(0, END)


def delSelection(key=None):
    if not key == 'BackSpace' or ListOpen:
        print('heyo')
        return
    print(clipboard[windowEntities['ITEMLIST'].curselection()[0]])
    thing = windowEntities['ITEMLIST'].curselection()[0]
    UpdateString.set(f"#{thing} Deleted")
    clipboard.remove(clipboard[windowEntities['ITEMLIST'].curselection()[0]])
    windowEntities['ITEMLIST'].delete(windowEntities['ITEMLIST'].curselection())


def UpdateLB(listbox):
    lastItemIndex = clipboard[len(clipboard) - 1]  # get the last input in the list (just added)
    string = f'{len(clipboard) - 1}: {lastItemIndex}'  # The string to display
    listbox.insert(len(clipboard) - 1, string)  # insert the string into the list
    try:
        print(str(listbox.curselection()))
    except IndexError:
        print('none selected')


def CopySelection(LB, window):
    global ListOpen
    #print(clipboard[LB.curselection()[0]])
    #print(f'User Copied {clipboard[LB.curselection()[0]]}')
    ListOpen = False
    window.withdraw()
    keyboard.remove_hotkey('enter')


# so that the child window doesn't close
def CloseChildWin():
    pass


def CreateFile():
    f = open("ClipBoardList.txt", "w")
    for item in enumerate(clipboard):
        print(f'writing {item}')
        f.write(str(item) + '\n')
    f.close()
    UpdateString.set('File Written at program directory')


def quitApp():
    sys.exit()


# Added to make the history window function smaller
def MakeChildWindow(position):
    LBWindow = Toplevel(takefocus=True)
    #LBWindow.iconbitmap((resource_path("Logo.ico")))
    #LBWindow.iconbitmap(r"C:\Users\JOE\Desktop\ClipboardApp\PygameVer\Logo.ico")
    windowLen = len(max(clipboard, key=len))
    # size of the largest string + a lil more
    if windowLen > 500:
        windowLen = 500
    elif windowLen < 150:
        windowLen = 150

    LBWindow.geometry(f"{windowLen + 50}x100+{position[0]}+{position[1]}")
    LBWindow.title("Clipboard List")
    LBWindow.resizable(False, False)  # stops window from being resizable
    return LBWindow


# Makes Clipboard Listbox at mouse Location
def MakeHistoryWindow():
    global ListOpen
    if ListOpen or clipboard.__len__() == 0:  # if the window is open, or list is empty do nothing
        return
    ListOpen = True  # set windowOpen to true
    window = MakeChildWindow(mouse.get_position())
    ClipboardLB = Listbox(window, width=50, exportselection=False)
    for item in enumerate(clipboard):  # add clipboard item to the listbox
        s = f'{item[0]}: {item[1]}'
        ClipboardLB.insert(item[0], s)

    ClipboardLB.select_set(0)  # initially selects 0

    keyboard.add_hotkey('enter', CopySelection, (ClipboardLB, window))  # Adds the enter hotkey

    ClipboardLB.pack()
    ClipboardLB.focus_force()
    window.attributes('-topmost', 1)    #This forces the window to the forground (front)

    CheckFocus(window)

    window.protocol("WM_DELETE_WINDOW", CloseChildWin)


def CheckFocus(win):
    def focus():
        funny = False
        if not win.focus_displayof() and not funny:
            funny = True
        if funny:  # this is really bad but idk how else to do this in my CAREER
            # Like this is really really bad. Removes all listeners because idk what counts as a listener in this module
            # The documentation is really barebones (maybe shouldve used pynput?)
            mouse.unhook_all()
            keyboard.unhook_all()  # To remove the listener on enter (otherwise it has multiple callbacks)
            keyboard.add_hotkey('ctrl+c', onCtrlC)
            keyboard.add_hotkey('ctrl+`', MakeHistoryWindow)
            addMouseChecks()
            # Hides window and resets variables
            win.withdraw()
            global ListOpen
            ListOpen = False

    # temporarily Adds these to check in the shite function above (gets removed in that function)
    mouse.on_click(focus)
    mouse.on_right_click(focus)


def addMouseChecks():
    mouse.on_right_click(CheckMouse)
    mouse.on_click(CheckMouse)


def MakeList():
    itemsLB = Listbox(root, width=50, height=30, exportselection=False)
    for item in enumerate(clipboard):  # add clipboard item to the listbox
        s = f'{item[0]}: {item[1]}'
        itemsLB.insert(item[0], s)
    return itemsLB


# Copies selected item with left click
def CopyItem(event):
    LB = windowEntities['ITEMLIST']
    print(f'{clipboard[LB.curselection()[0]]} Copied')
    pyperclip.copy(clipboard[LB.curselection()[0]])
    UpdateString.set(f'#{LB.curselection()[0]} Copied')


windowEntities = {
    'TITLE': ttk.Label(root, text='Extended Clipboard', font=('Helvetica 15 underline')),
    'MAKELIST': ttk.Button(root, text='Write List', command=CreateFile),
    'DELLIST': ttk.Button(root, text='Delete List', command=clearList),
    'REMOVEITEM': ttk.Button(root, text='Remove Item', command=delSelection),
    'DESCRIBE': ttk.Label(root, textvariable=UpdateString),
    'HEADING': ttk.Label(root, text='Copied Items'),
    'ITEMLIST': MakeList()
}


# Just checks every mouse click if something has been copied to clipboard
def CheckMouse():
    if len(clipboard) > 0:
        if clipboard[-1] is not pyperclip.paste():  # if final item isn't the same as clipboard
            onCtrlC()
            return


def tksetup():
    root.resizable(False, False)
    root.title('Clipper')
    root.geometry("300x500")
    #root.iconbitmap((resource_path("Logo.png")))
    #root.iconbitmap(r"C:\Users\JOE\Desktop\ClipboardApp\PygameVer\Logo.ico")
    for item in windowEntities.values():
        item.pack()
    windowEntities['ITEMLIST'].bind('<Double-1>', CopyItem)
    windowEntities['ITEMLIST'].bind('<Key>', delSelection)
    root.mainloop()
    sys.exit()  # This stops the program when the x button is actually pressed (lets user keep going if not used)



def main():


    global CopyLabel
    # Hotkeys to look for: ctrl c, x.
    keyboard.add_hotkey('ctrl+c', onCtrlC)
    keyboard.add_hotkey('ctrl+`', MakeHistoryWindow)
    addMouseChecks()
    tksetup()

    # needs to be here for some reason. this whole bit is so wierd like I need some in depth knowledge about pynput


if __name__ == '__main__':
    main()
