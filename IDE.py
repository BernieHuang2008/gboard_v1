import ctypes
import sys
from tkinter import Menu, messagebox, Tk, END, BOTH
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.scrolledtext import ScrolledText

from MathLang import token, Run


def start(*args, canrun=True):
    file_name = "Untitled"

    def change_filename(new_name):
        nonlocal file_name
        file_name = new_name
        win.title("IDE:G - {}".format(file_name))

    def change_font_size(event):
        font = text_box['font'].split('} ')
        if event.delta > 0:
            font[1] = str(int(font[1]) + 1)
            font = '} '.join(font)
        else:
            font[1] = str(int(font[1]) - 1)
            font = '} '.join(font)
        text_box['font'] = font

    win = Tk()
    win.title("IDE:G - {}".format(file_name))
    win.geometry('1000x600')
    win.iconbitmap(True, default="assets/icon/IDE-G.ico")
    win['bg'] = "#2b2b2b"
    win.bind("<Control-MouseWheel>", change_font_size)

    # 设置缩放因子
    if sys.platform == 'win32':
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        win.tk.call('tk', 'scaling', ScaleFactor / 75)

    last_save_hash = hash("\n")

    def new_file(*args):
        nonlocal last_save_hash
        if last_save_hash != hash(text_box.get(1.0, END)) and \
                not messagebox.askyesno("IDE:G", "Do you really want to open another file?\n\
    The current changes will be lost if you don't save it."):
            return False

        text_box.delete(1.0, END)
        last_save_hash = hash("\n")
        change_filename("Untitled")

    def open_file(*args):
        nonlocal last_save_hash
        if last_save_hash != hash(text_box.get(1.0, END)[:-1]) and \
                not messagebox.askyesno("IDE:G", "Do you really want to open another file?\n\
    The current changes will be lost if you don't save it."):
            return False

        filename = askopenfilename(defaultextension='.mathlang', filetypes=[("Math Lang", ".mathlang")])
        if filename != '':
            text_box.delete(1.0, END)  # delete all
            f = open(filename, 'r', encoding='utf-8', errors='ignore')
            text_box.insert(1.0, f.read())
            last_save_hash = hash(text_box.get(1.0, END))
            change_filename(filename)
            f.close()
        update()

    def save_file(*args):
        nonlocal last_save_hash
        if file_name != "*Untitled" and file_name != "Untitled":
            filename = file_name.lstrip("*")
        else:
            filename = asksaveasfilename(initialfile='script', defaultextension='.mathlang',
                                         filetypes=[("Math Lang", ".mathlang")])
        if filename != '':
            fh = open(filename, 'w', encoding='utf-8', errors='ignore')
            msg = text_box.get(1.0, END)
            fh.write(msg)
            last_save_hash = hash(msg)
            change_filename(filename)
            fh.close()

    def run_script(*args):
        Run(text_box.get(1.0, END))

    main_menu = Menu(win, bg="#2b2b2b", fg="#a9b7c6")
    menu_file = Menu(main_menu, tearoff=False)
    main_menu.add_cascade(label="File", menu=menu_file, underline=0)
    if canrun:
        main_menu.add_cascade(label="Run", underline=0, command=run_script)
    menu_file.add_command(label="New", command=new_file, underline=0, accelerator='Ctrl+N')
    win.bind("<Control-n>", new_file)
    menu_file.add_command(label="Open", command=open_file, underline=0, accelerator='Ctrl+O')
    win.bind("<Control-o>", open_file)
    menu_file.add_command(label="Save", command=save_file, underline=0, accelerator='Ctrl+S')
    win.bind("<Control-s>", save_file)
    win.config(menu=main_menu)

    text_box = ScrolledText(win, bg='#2b2b2b', fg="#a9b7c6", insertbackground="#bbb", height=10,
                            font=("JetBrains Mono Regular", 13))
    text_box.vbar.config(troughcolor='red', bg='blue')
    text_box.pack(fill=BOTH, expand=1)
    text_box.focus_set()

    def update(*args):
        nonlocal ctrl_on, alt_on
        if ctrl_on or alt_on:
            ctrl_on = alt_on = False
            return
        if args and args[0].keycode == 16:
            alt_on = True
        elif args and args[0].keycode == 17:
            ctrl_on = True
        if last_save_hash == hash(text_box.get(1.0, END)):
            change_filename(file_name.lstrip("*"))
        else:
            change_filename("*" + file_name.lstrip("*"))

        origin = text_box.get(1.0, END)
        replaced = origin[:-1]  # remove the last `\n`
        insert = text_box.index('insert').split('.')

        cnt = 0
        for _from, _to, _cnt in [('>=', '≥', -1), ('<=', '≤', -1), ('连接', 'connect', 5), ('（', '(', 0), ('）', ')', 1)]:
            if _from in replaced:
                cnt += _cnt
            replaced = replaced.replace(_from, _to)

        text_box.delete(1.0, END)
        text_box.insert(1.0, replaced)
        text_box.mark_set('insert', insert[0] + '.' + str(int(insert[1]) + cnt))
        text_box.see('.'.join(insert))
        replaced_token = replaced.split('\n')

        for i in range(len(replaced_token)):
            line = replaced_token[i]
            tokens = token(line, token_index=True)
            for t in tokens:
                for _type, _color in [('keyword', 'cc7832'), ('string', '539a50'), ('name', '8888c6'),
                                      ('number', '6897bb')]:
                    if t['type'] == _type:
                        row = i + 1
                        col = t['token_index'] - min(replaced[:t['token_index']].rfind(' '),
                                                     replaced[:t['token_index']].rfind('\n')) - 1
                        for j in range(len(t['value'])):
                            new_col = col + j
                            text_box.tag_add(_type, str(row) + '.' + str(new_col))
                            text_box.tag_config(_type, foreground='#' + _color)
                        break

    def keyrelease(x):
        nonlocal ctrl_on, alt_on
        if x.keycode == 16:
            alt_on = False
        if x.keycode == 17:
            ctrl_on = False

    win.bind("<KeyPress>", update)
    win.bind("<KeyRelease>", keyrelease)
    ctrl_on = False
    alt_on = False
    win.mainloop()


if __name__ == '__main__':
    start(canrun=False)
