import sys

import command
from board import Point, Segment
import IDE
import board
import ctypes
from tkinter import Tk, Toplevel, Scrollbar, Listbox, Menu, END, Canvas, YES, BOTH, RIGHT, Y
import time

last_motion = (0, 0)
canmotion = 1
ondrag = 0
toolbar: Tk
selected = set()


def clear_selecte():
    for x in selected:
        x.show(0)
    selected.clear()


def mouseLeft(e):
    global selected
    cof = board.cooRef(e.x, e.y)
    if not cof:
        clear_selecte()
    x = None
    for x in cof:
        x = board.objects[x]
        if x.type == 'Point':
            break
    if x in selected:
        x.show(0)
        selected.remove(x)
    elif x:
        x.show(1)
        selected.add(x)
    print(selected)


def mouseRight(e):
    global selected, toolbar
    tools, wid, hei = get_tool()

    toolbar = Toplevel()

    toolbar.geometry(
        '{}x{}+{}+{}'.format(wid, hei, win.winfo_pointerx(), win.winfo_pointery()))
    toolbar.overrideredirect(True)
    toolbar.attributes("-topmost", True)
    toolbar.bind("<FocusOut>", toolbarFocusOut)
    toolbar.bind("<Button-1>", lambda _: fl[box.curselection()[0]]())
    toolbar.focus()

    scrollBar = Scrollbar(toolbar)
    scrollBar.pack(side=RIGHT, fill=Y)

    box = Listbox(toolbar, yscrollcommand=scrollBar.set, borderwidth="0")

    scrollBar.config(command=box.yview)

    fl = []

    for x, f in tools:
        box.insert(END, x)
        fl.append(f)
    box.pack()


def toolbarFocusOut(*args):
    global toolbar, selected
    if toolbar is not None:
        toolbar.destroy()
    clear_selecte()


def mouseUp(e):
    global ondrag
    if ondrag:
        ondrag = 0
        clear_selecte()


def motion(e):
    global canmotion, last_motion, mouseObj
    if canmotion:
        canmotion = 0
        lx, ly = last_motion = (e.x, e.y)
        if board.cooRef(lx, ly):
            board.canvas.moveto(mouseObj, 99999, 99999)
            board.canvas.moveto(mousePointer, lx, ly)
        else:
            board.canvas.moveto(mousePointer, 99999, 99999)
            board.canvas.moveto(mouseObj, lx, ly)
        time.sleep(0.02)
        canmotion = 1
    # selected = get_select()


def drag(e):
    global ondrag, last_motion, mouseObj
    lx, ly = last_motion = (e.x, e.y)
    if board.cooRef(lx, ly):
        board.canvas.moveto(mouseObj, 99999, 99999)
        board.canvas.moveto(mousePointer, lx, ly)
    else:
        board.canvas.moveto(mousePointer, 99999, 99999)
        board.canvas.moveto(mouseObj, lx, ly)

    for x in selected:
        x.moveto(lx, ly, alert=True)
    ondrag = 1


def hideMouse(e):
    global last_motion, mouseObj
    # lx, ly = last_motion
    # board.canvas.create_polygon(lx, ly, lx, ly + 23, lx + 5, ly + 17, lx + 9, ly + 30, lx + 14, ly + 30, lx + 9,
    #                             ly + 17, lx + 16, ly + 17, fill='white')
    # board.canvas.delete(mouseObj)
    board.canvas.moveto(mouseObj, 99999, 99999)


def showMouse(e):
    global last_motion, mouseObj
    lx, ly = last_motion
    board.canvas.moveto(mouseObj, lx, ly)
    # mouseObj = board.canvas.create_polygon(lx, ly, lx, ly + 23, lx + 5, ly + 17, lx + 9, ly + 30, lx + 14, ly + 30,
    #                                        lx + 9, ly + 17, lx + 16, ly + 17, fill='black')


win = Tk()
win.geometry('1000x600')
win.title('G-Board')
win.iconbitmap(True, default="assets/icon/icon.ico")

# 设置缩放因子
if sys.platform == 'win32':
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    win.tk.call('tk', 'scaling', ScaleFactor / 75)

# create canvas
board.canvas = Canvas(win, height=600, width=1000, bg='white', cursor='none')
board.canvas.pack(expand=YES, fill=BOTH)

board.canvas.bind("<Button-1>", mouseLeft)
board.canvas.bind("<Button-3>", mouseRight)
board.canvas.bind("<ButtonRelease>", mouseUp)
board.canvas.bind("<Motion>", motion)
board.canvas.bind("<B1-Motion>", drag)
board.canvas.bind("<Leave>", hideMouse)
board.canvas.bind("<Enter>", showMouse)

main_menu = Menu(win)
menu_file = Menu(main_menu, tearoff=False)
menu_script = Menu(main_menu, tearoff=False)
main_menu.add_cascade(label="File", menu=menu_file, underline=0)
menu_file.add_command(label="Save", command=command.save, underline=0)
win.bind("<Control-s>", command.save)
main_menu.add_cascade(label="Script", menu=menu_script, underline=0)
menu_script.add_command(label="Editor", command=IDE.start, underline=0)
win.bind("<Alt-g>", IDE.start)
win.config(menu=main_menu)

lx, ly = 0, 0
mouseObj = board.canvas.create_polygon(lx, ly, lx, ly + 23, lx + 5, ly + 17, lx + 9, ly + 30, lx + 14, ly + 30,
                                       lx + 9, ly + 17, lx + 16, ly + 17, fill='black')
mousePointer = board.canvas.create_polygon(lx, ly, lx + 20, ly + 10, lx + 20, ly + 3, lx + 40, ly + 3, lx + 40, ly - 3,
                                           lx + 20, ly - 3, lx + 20, ly - 10, fill='black')
hideMouse(0)

"""
===============================================================================
===============================================================================
===============================================================================
============================ Part 2 : Script ==================================
===============================================================================
===============================================================================
===============================================================================
"""


# board.ErrorWindow("Contradiction",
#             "Relationship between\nmid_point( {} , {} )\nhas contradiction.".format(0.192384928492810401,
#                                                                                     20.192384928492810401))


def get_tool():
    global selected
    s = [x.type for x in selected]

    # print(s)

    src = [x for x in selected] + [win.winfo_pointerx() - win.winfo_rootx(),
                                   win.winfo_pointery() - win.winfo_rooty()]
    res = {
        'Point Point': [("Segment", lambda: toolbarFocusOut(Segment(src[0], src[1])))],
        'Segment': [
            ("Mid-Point", lambda: toolbarFocusOut(
                src[0].newRelation([Point((src[0].a.x + src[0].b.x) / 2, (src[0].a.y + src[0].b.y) / 2).id],
                                   "mid_point"),
                board.objects[src[0].relation[-1][0][0]].newRelation([src[0].id], ".mid_point"))),
            ("Info", lambda: toolbarFocusOut(src[0].show_info())),

        ],
        'Segment Point': [
            ("Perpendicular Bisector", lambda: toolbarFocusOut(src[0]))
        ],
        'Point': [("Info", lambda: toolbarFocusOut(src[0].show_info())),
                  ("T:MoveTo", lambda: toolbarFocusOut(src[0].moveto(1400, 400, alert=True)))],
        '': [("Point", lambda: toolbarFocusOut(Point(src[-2], src[-1])))],
    }.get(' '.join(s), [("Close", toolbarFocusOut)])

    return res, 200, Listbox(win).winfo_reqheight()


# p1 = Point(200, 100)
# p2 = Point(300, 400)
# l1 = Segment(p1, p2)

# MathLang.Run("""
# A (574, 67)
# B (429, 42)
# C (298, 153)
# D (298, 435)
# E (451, 532)
# F (585, 449)
# G (585, 327)
# H (437, 327)
#
# connect A B
# connect B C
# connect C D
# midpoint CD as M
# connect D E
# connect E F
# connect F G
# connect G H
# connect H D
# connect A M
# """)

# p2.moveto(1400, 400)
# print(board.cooref)
win.mainloop()
