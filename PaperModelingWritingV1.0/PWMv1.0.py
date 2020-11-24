#!/usr/bin/python
#-- coding:utf8 --

from tkinter import *
import tkinter.filedialog
import tkinter.messagebox as tmb
import os

# 新建根窗口
root = Tk()
# 新建Menu实例
menu_bar = Menu(root)
file_menu = Menu(menu_bar, tearoff=0)
edit_menu = Menu(menu_bar, tearoff=0)
view_menu = Menu(menu_bar, tearoff=0)
about_menu = Menu(menu_bar, tearoff=0)
themes_menu = Menu(menu_bar, tearoff=0)

file_name = None


# 获取文本行数
def get_line_numbers():
    output = ''
    if show_line_number.get():
        row, col = content_text.index("end").split('.')
        for i in range(1, int(row)):
            output += str(i) + '\n'
    return output


# 更新文本行数
def update_line_numbers(event=None):
    line_numbers = get_line_numbers()
    line_number_bar.config(state='normal')
    line_number_bar.delete('1.0', 'end')
    line_number_bar.insert('1.0', line_numbers)
    line_number_bar.config(state='disabled')


# 高亮当前行
def highlight_line(interval=100):
    content_text.tag_remove("active_line", 1.0, "end")
    content_text.tag_add("active_line", "insert linestart", "insert lineend+1c")
    content_text.after(interval, toggle_highlight)


# 非高亮当前行
def undo_highlight():
    content_text.tag_remove("active_line", 1.0, "end")


# 高亮状态切换
def toggle_highlight(event=None):
    if to_highlight_line.get():
        highlight_line()
    else:
        undo_highlight()


# 显示光标信息
def show_cursor_info_bar():
    show_cursor_info_checked = show_cursor_info.get()
    if show_cursor_info_checked:
        cursor_info_bar.pack(expand='no', fill=None, side='right', anchor='se')
    else:
        cursor_info_bar.pack_forget()


# 更新光标信息
def update_cursor_info_bar(event=None):
    row, col = content_text.index(INSERT).split('.')
    line_num, col_num = str(int(row)), str(int(col) + 1)
    infotext = "Line: {0} | Column: {1}".format(line_num, col_num)
    cursor_info_bar.config(text=infotext)


# 当文本内容改变时触发
def on_content_changed(event=None):
    update_line_numbers()
    update_cursor_info_bar()


# 打开文件
def open_file(event=None):
    input_file_name = tkinter.filedialog.askopenfilename(defaultextension=".txt",
                                                         filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")])
    if input_file_name:
        global file_name
        file_name = input_file_name
        root.title('{} - {}'.format(os.path.basename(file_name), PROGRAM_NAME))
        content_text.delete(1.0, END)
        with open(file_name) as _file:
            content_text.insert(1.0, _file.read())
        on_content_changed()


# 保存文件
def save(event=None):
    global file_name
    if not file_name:
        save_as()
    else:
        write_to_file(file_name)
    return "break"


# 保存文件为
def save_as(event=None):
    input_file_name = tkinter.filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("All Files", "*.*"), (
    "Text Documents", "*.txt")])
    if input_file_name:
        global file_name
        file_name = input_file_name
        write_to_file(file_name)
        root.title('{} - {}'.format(os.path.basename(file_name), PROGRAM_NAME))
    return "break"


# 写入磁盘
def write_to_file(file_name):
    try:
        content = content_text.get(1.0, 'end')
        with open(file_name, 'w') as the_file:
            the_file.write(content)
    except IOError:
        pass


# 新建文件
def new_file(event=None):
    root.title("Untitled")
    global file_name
    file_name = None
    content_text.delete(1.0, END)
    on_content_changed()


# 退出编辑器
def exit_editor(event=None):
    if tkinter.messagebox.askokcancel("Quit?", "Really quit?"):
        root.destroy()


# 剪切
def cut():
    content_text.event_generate("<<Cut>>")
    on_content_changed()


# 复制
def copy():
    content_text.event_generate("<<Copy>>")


# 粘贴
def paste():
    content_text.event_generate("<<Paste>>")
    on_content_changed()


# 恢复
def redo(event=None):
    content_text.event_generate("<<Redo>>")
    on_content_changed()
    return 'break'


# 撤销
def undo(event=None):
    content_text.event_generate("<<Undo>>")
    on_content_changed()
    return 'break'


# 全选
def select_all(event=None):
    content_text.tag_add('sel', '1.0', 'end')
    return "break"


# 查找
def find_text(event=None):
    search_toplevel = Toplevel(root)
    search_toplevel.title('Find Text')
    search_toplevel.transient(root)
    search_toplevel.resizable(False, False)
    Label(search_toplevel, text="Find All:").grid(row=0, column=0, sticky='e')
    search_entry_widget = Entry(search_toplevel, width=50)
    search_entry_widget.grid(row=0, column=1, padx=2, pady=2, sticky='we')
    search_entry_widget.focus_set()
    ignore_case_value = IntVar()
    Checkbutton(search_toplevel, text='Ignore  Case', variable=ignore_case_value).grid(row=1, column=1, sticky='e',
                                                                                       padx=2, pady=2)
    Button(search_toplevel, text="Find All", underline=0,
           command=lambda: search_output(search_entry_widget.get(), ignore_case_value.get(), content_text,
                                         search_toplevel, search_entry_widget)).grid(row=0, column=2, sticky='e' + 'w',
                                                                                     padx=2, pady=2)


# 关闭查找窗口
def close_search_window():
    content_text.tag_remove('match', '1.0', END)
    search_toplevel.destroy()
    search_toplevel.protocol('WM_DELETE_WINDOW', close_search_window)
    return "break"


# 查找结果输出
def search_output(needle, if_ignore_case, content_text, search_toplevel, search_box):
    content_text.tag_remove('match', '1.0', END)
    matches_found = 0
    if needle:
        start_pos = '1.0'
        while True:
            start_pos = content_text.search(needle, start_pos, nocase=if_ignore_case, stopindex=END)
            if not start_pos:
                break
            end_pos = '{}+{}c'.format(start_pos, len(needle))
            content_text.tag_add('match', start_pos, end_pos)
            matches_found += 1
            start_pos = end_pos
        content_text.tag_config('match', foreground='red', background='yellow')
    search_box.focus_set()
    search_toplevel.title('{} matches found'.format(matches_found))


# 显示about
def display_about_messagebox(event=None):
    tkinter.messagebox.showinfo("About",
                                "{}{}".format(PROGRAM_NAME, "\nTkinter GUI Application\n Development Blueprints"))


# 显示help
def display_help_messagebox(event=None):
    tkinter.messagebox.showinfo("Help", "Help Book: \nTkinter GUI Application\n Development Blueprints",
                                icon='question')


# 变量初始化
show_cursor_info = BooleanVar()
to_highlight_line = BooleanVar()
theme_choice = StringVar()
show_line_number = IntVar()
show_line_number.set(1)
# 主题
color_schemes = {'Default': '#000000.#FFFFFF',
                 'Greygarious': '#83406A.#D1D4D1',
                 'Aquamarine': '#5B8340.#D1E7E0',
                 'Bold Beige': '#4B4620.#FFF0E1',
                 'Cobalt Blue': '#ffffBB.#3333aa',
                 'Olive Green': '#D1E7E0.#5B8340',
                 'Night Mode': '#FFFFFF.#000000'}


# 更换主题
def change_theme(event=None):
    selected_theme = theme_choice.get()
    fg_bg_colors = color_schemes.get(selected_theme)
    foreground_color, background_color = fg_bg_colors.split('.')
    content_text.config(background=background_color, fg=foreground_color)


# File
file_menu.add_command(label="New", accelerator='Ctrl+N', compound='left', underline=0, command=new_file)
file_menu.add_command(label="Open", accelerator='Ctrl+O', compound='left', underline=0, command=open_file)
file_menu.add_command(label="Save", accelerator='Ctrl+S', compound='left', underline=0, command=save)
file_menu.add_command(label="Save as", accelerator='Shift+Ctrl+S', compound='left', underline=0, command=save_as)
file_menu.add_separator()
file_menu.add_command(label="Exit", accelerator='Alt+F4', compound='left', underline=0, command=exit_editor)
# Edit
edit_menu.add_command(label="Undo", accelerator='Ctrl + Z', compound='left', command=undo)
edit_menu.add_command(label="Redo", accelerator='Ctrl + Y', compound='left', command=redo)
edit_menu.add_separator()
edit_menu.add_command(label="Cut", accelerator='Ctrl + X', compound='left', command=cut)
edit_menu.add_command(label="Copy", accelerator='Ctrl + C', compound='left', command=copy)
edit_menu.add_command(label="Paste", accelerator='Ctrl + V', compound='left', command=paste)
edit_menu.add_separator()
edit_menu.add_command(label="Find", underline=0, accelerator='Ctrl + F', compound='left', command=find_text)
edit_menu.add_separator()
edit_menu.add_command(label="Select All", underline=7, accelerator='Ctrl + A', compound='left', command=select_all)
# View
view_menu.add_checkbutton(label="Show Line Number", variable=show_line_number)
view_menu.add_checkbutton(label="Show Cursor Location at Bottom", variable=show_cursor_info,
                          command=show_cursor_info_bar)
view_menu.add_checkbutton(label='Highlight Current Line', onvalue=1, offvalue=0, variable=to_highlight_line,
                          command=toggle_highlight)
# Themes
themes_menu.add_radiobutton(label="Default", variable=theme_choice, command=change_theme)
themes_menu.add_radiobutton(label="Aquamarine", variable=theme_choice, command=change_theme)
themes_menu.add_radiobutton(label="Bold Beige", variable=theme_choice, command=change_theme)
themes_menu.add_radiobutton(label="Cobalt Blue", variable=theme_choice, command=change_theme)
themes_menu.add_radiobutton(label="Greygarious", variable=theme_choice, command=change_theme)
themes_menu.add_radiobutton(label="Night Mode", variable=theme_choice, command=change_theme)
themes_menu.add_radiobutton(label="Olive Green", variable=theme_choice, command=change_theme)
view_menu.add_cascade(label="Themes", menu=themes_menu)
# About
about_menu.add_command(label="About", compound='left', command=display_about_messagebox)
about_menu.add_command(label="Help", compound='left', command=display_help_messagebox)
# 主菜单栏
menu_bar.add_cascade(label='File', menu=file_menu)
menu_bar.add_cascade(label='Edit', menu=edit_menu)
menu_bar.add_cascade(label='View', menu=view_menu)
menu_bar.add_cascade(label='About', menu=about_menu)
# 窗口名称
PROGRAM_NAME = " Footprint Editor "
root.title(PROGRAM_NAME)
# 工具栏
shortcut_bar = Frame(root, height=25, background='light sea green')
shortcut_bar.pack(expand='no', fill='x')
# 图标名称
icons = ('new_file', 'open_file', 'save', 'cut', 'copy', 'paste', 'undo', 'redo', 'find_text')
for i, icon in enumerate(icons):
    tool_bar_icon = PhotoImage(file='icons/{}.gif'.format(icon))  # 图标文件路径
    cmd = eval(icon)
    tool_bar = Button(shortcut_bar, image=tool_bar_icon, command=cmd)
    tool_bar.image = tool_bar_icon
    tool_bar.pack(side='left')
# 左侧行数区
line_number_bar = Text(root, width=4, padx=3, takefocus=0, border=0, background='khaki', state='disabled', wrap='none')
line_number_bar.pack(side='left', fill='y')
# 文本内容区和右侧滚动条
content_text = Text(root, wrap='word', undo=1)
content_text.tag_configure('active_line', background='ivory2')
content_text.bind('<Any-KeyPress>', on_content_changed)
content_text.pack(expand='yes', fill='both')
scroll_bar = Scrollbar(content_text)
content_text.configure(yscrollcommand=scroll_bar.set)
scroll_bar.config(command=content_text.yview)
scroll_bar.pack(side='right', fill='y')
# 右键下拉菜单
popup_menu = Menu(content_text)
for i in ('cut', 'copy', 'paste', 'undo', 'redo'):
    cmd = eval(i)
    popup_menu.add_command(label=i, compound='left', command=cmd)
popup_menu.add_separator()
popup_menu.add_command(label='Select All', underline=7, command=select_all)


def show_popup_menu(event):
    popup_menu.tk_popup(event.x_root, event.y_root)


content_text.bind('<Button-3>', show_popup_menu)
# 右下侧光标信息显示
cursor_info_bar = Label(content_text, text='Line: 1 | Column: 1')
cursor_info_bar.pack(expand=NO, fill=None, side='right', anchor='se')

root.config(menu=menu_bar)
root.mainloop()
