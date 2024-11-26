from tkinter import *
from tkinter.dnd import Tester as DragWindow, Icon as Dragable

# Make a root window and hide it, since we don't need it.
root = Tk()
root.withdraw()
# Make the actual main window, which can have dragable objects on.
main = DragWindow(root)

dragable_item = None

def make_btn():
    global dragable_item
    if dragable_item is None:
        dragable_item = Dragable('B')
        dragable_item.attach(main.canvas)

def dragoff():
    if dragable_item:
        dragable_item.label.unbind("<ButtonPress>")

# Make a button and bind it to our button creating function.
B1 = Button(main.top, text='A', command=make_btn)
B1.pack()
B2 = Button(main.top, text='Drag Off', command=dragoff)
B2.pack()

root.mainloop()