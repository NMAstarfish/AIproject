import mLogAnalog as ag
import mLogSqlite as sq
import os
import glob
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
from tkinter import ttk

class MyInput:
    cmd = ''
    address = ''
    datestart = ''
    dateend = ''
    timestart = ''
    timeend = ''
    process = ''
    thread = ''
    log_level = ''
    def __init__(self, cmd='', address='', datestart='', dateend='', timestart='', timeend='',process='',thread='',log_level='',nokey=''):
        self.cmd = cmd
        self.address = address
        self.process = process
        self.thread = thread
        self.log_level = log_level
        # 转换日期为元组格式
        self.datestart = tuple(map(int, (datestart or '1-1').split('-')))
        self.dateend = tuple(map(int, (dateend or '12-30').split('-')))
        # 定义时间范围 # 将 timestart 和 timeend 转换为 datetime 对象
        self.timestart = datetime.strptime(timestart or '00:00:00.000', "%H:%M:%S.%f")
        self.timeend = datetime.strptime(timeend or '23:59:59.999', "%H:%M:%S.%f")
        # 将 process 和 thread 字符串转换为整数列表
        self.process_list = list(map(int, self.process.split())) if self.process else []
        self.thread_list = list(map(int, self.thread.split())) if self.thread else []
        if log_level:  # 检查log_level是否非空
            self.log_level = log_level[0]  # 只有在log_level非空时才截取首个字符
        else:
            self.log_level = ''  # 如果log_level为空，设置self.log_level为空字符串或默认值
        self.nokey_list = nokey.split(',') if nokey else []
    def display(self):
        print(f"Command: {self.cmd}")
        print(f"Address: {self.address}")
        print(f"Start Date: {self.datestart}")
        print(f"End Date: {self.dateend}")
        print(f"Start Time: {self.timestart}")
        print(f"End Time: {self.timeend}")
        print(f"Process: {self.process}")
        print(f"Thread: {self.thread}")
        print(f"log_level: {self.log_level}")
        print(f"nokey_list':{self.nokey_list}")
        
# 定义一个接受 MyInput 实例的函数
def process_input(my_input_instance):
    print("Processing input:")
    my_input_instance.display()
# 逐行分析
def find_command_in_line(text_input, line):
    keywords = {}
    # 将输入的cmd字符串按逗号分割，得到一个包含多个键值对的列表
    cmd_list = text_input.cmd.split(',')
    for item in cmd_list:
        # 检查每个键值对是否符合基本格式要求
        if '\'' not in item or ':' not in item or item.count('\'') < 2:
            text.insert(tk.END, f'error : Input "{item}" format is incorrect.\n')
            continue
        
        # 初始化位置指针
        positionStart = item.find('\'')
        positionCut = item.find(':')
        positionEnd = item.rfind('\'')  # 使用rfind找到最后一个单引号的位置
        keystring = item[positionStart+1:positionCut]
        valuestring = item[positionCut+1:positionEnd]
        # 确保关键字存在，如果不存在则初始化一个空列表
        if keystring not in keywords:
            keywords[keystring] = []
        # 添加值到对应关键字的列表中
        keywords[keystring].append(valuestring)
    # 遍历keywords字典，对每个key执行操作
    for key, values in keywords.items():
        rc = ag.run_key(text_input, values, line)
        if rc == 1:
            break
    return rc


# 读取文件进行分析和输出
def run(text_input):
    try:
        with open(text_input.address, 'r', encoding='utf-8') as file:
            # 逐行读取文件
            for line in file:
                # 分析输出与否
                rc = find_command_in_line(text_input, line)
                # 分析完成后输出
                if(rc):
                    text.insert(tk.END, line)
            return
    except FileNotFoundError as e:
        text.insert(tk.END, "error file address")

# 空地址时使用默认地址检索
def find_defult_txt_file():
    # 获取当前工作目录
    current_dir = os.getcwd()
    # 使用glob模块查找当前目录下的所有.txt文件
    txt_files = glob.glob(os.path.join(current_dir, "*.txt"))
    # 如果找到了.txt文件
    if txt_files:
        # 返回第一个.txt文件的完整路径
        return txt_files[0]
    else:
        # 如果没有找到.txt文件，返回None或适当的提示信息
        return None

# 按钮控制
def on_button_click():
    # 清除之前的输出
    text.delete('1.0', tk.END)
    # 读取地址和cmd
    text_input = MyInput(
        cmd = entry.get(),
        address = loc.get(),
        datestart = StartDate.get(),
        dateend = EndDate.get(),
        timestart = StartTime.get(),
        timeend = EndTime.get(),
        process = process_in.get(),
        thread = thread_in.get(),
        log_level = log_level_combobox.get(),
        nokey = nokey_in.get()
    )
    process_input(text_input)
    # 判断使用默认地址
    if not text_input.address:
        text_input.address = find_defult_txt_file()
        if not text_input.address:
            text.insert(tk.END, "no file to analog")
            return
    # 有文件地址的情况下运行输出
    run(text_input)
    


# main window
root = tk.Tk()
root.title("My Tkinter App")
root.geometry("1200x800")  # 设置窗口初始大小
# root.minsize(200, 200)  # 设置窗口的最小尺寸
# root.maxsize(1000, 800)  # 设置窗口的最大尺寸
root.configure(bg="white")  # 设置窗口的背景色

# 创建标签输入框
loc_text = tk.Label(root, text = "输入文件地址(必填),例如:generated_logs.txt", width=80)
loc = tk.Entry(root, width=80)
entry_text = tk.Label(root, text = "输入需要查找的关键词(必填),例如：'key:System'", width=80)
entry = tk.Entry(root, width=80)
nokey_in_text = tk.Label(root, text = "输入不能出现的关键词,例如：'Error','update'", width=80)
nokey_in = tk.Entry(root, width=80)
# 创建日期的标签与输入框，并放在同一行
date_frame = tk.Frame(root)
StartDate_text = tk.Label(date_frame, text="起始日期", width=30)
StartDate = tk.Entry(date_frame, width=30)
EndDate_text = tk.Label(date_frame, text="截止日期", width=30)
EndDate = tk.Entry(date_frame, width=30)

StartDate_text.pack(side=tk.LEFT)
StartDate.pack(side=tk.LEFT)
EndDate_text.pack(side=tk.LEFT)
EndDate.pack(side=tk.LEFT)

# 创建时间的标签与输入框，并放在同一行
time_frame = tk.Frame(root)
StartTime_text = tk.Label(time_frame, text="起始时间", width=30)
StartTime = tk.Entry(time_frame, width=30)
EndTime_text = tk.Label(time_frame, text="截止时间", width=30)
EndTime = tk.Entry(time_frame, width=30)

StartTime_text.pack(side=tk.LEFT)
StartTime.pack(side=tk.LEFT)
EndTime_text.pack(side=tk.LEFT)
EndTime.pack(side=tk.LEFT)

#创建进程与线程的标签与输入框
process_thread_frame = tk.Frame(root)
process_in_text = tk.Label(process_thread_frame, text="进程", width=30)
process_in = tk.Entry(process_thread_frame, width=30)
thread_in_text = tk.Label(process_thread_frame, text="线程", width=30)
thread_in = tk.Entry(process_thread_frame, width=30)

process_in_text.pack(side=tk.LEFT)
process_in.pack(side=tk.LEFT)
thread_in_text.pack(side=tk.LEFT)
thread_in.pack(side=tk.LEFT)

# 布局
loc_text.pack()
loc.pack()
entry_text.pack()
entry.pack()
nokey_in_text.pack()
nokey_in.pack()
date_frame.pack()
time_frame.pack()
process_thread_frame.pack()

# 创建组合框的框架
log_level_frame = tk.Frame(root)
log_level_frame.pack()
# 创建组合框控件，设置其宽度并初始化一个默认值
log_level_combobox = ttk.Combobox(log_level_frame, width=20, values=['','V:Verbose,调试信息', 'D:Debug,调试信息', 'I:Info,一般信息', 'W:Warn', 'E:ERROR'])
log_level_combobox.set(' 请选择日志级别')  # 设置默认显示的值
log_level_combobox.pack(side=tk.LEFT)

# 创建按钮
button = tk.Button(root, text="Submit", command=on_button_click, width=40)
button.pack()

# 创建滚动的文本输出框(日志部分)
text = scrolledtext.ScrolledText(root, wrap=tk.NONE, width=120, height=30)
text.pack()
sql_text = scrolledtext.ScrolledText(root, wrap=tk.NONE, width=120, height=10)
sql_text.pack()
# 创建滚动的文本输出框(同类问题提示)

# 主循环
root.mainloop()