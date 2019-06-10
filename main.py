# -*- coding:utf-8 -*-
import csdnToPdf
import tkinter as tk
import globalVar
import tkinter.font as tkFont
from tkinter import *
from csdnToPdf import *
from threading import Thread


debug = False


def opt(opt_url):
	opt_url = opt_url.replace('\r', '').replace('\n', '').replace(' ', '')
	if not opt_url.startswith('http') or opt_url == '':
		globalVar.text3.configure(text='网址输入错误，请您重新输入！')
		return
	if not debug:
		if not opt_url.endswith('/'):
			opt_url = opt_url + '/'
		opt_blogname = opt_url.split('/')[-2]
		opt_blogname = opt_blogname + '\\'
		proc = csdnToPdf(opt_blogname, opt_url)
		if opt_url.find('details/') == -1:
			globalVar.text3.configure(text='已识别为全博客抓取模式......')
			time.sleep(2)
			globalVar.text3.configure(text='正在抓取，请耐心等待......')
			proc.getAllBlogContent()
		else:
			globalVar.text3.configure(text='已识别为特定博文抓取模式......')
			time.sleep(2)
			globalVar.text3.configure(text='正在抓取，请耐心等待......')
			proc.getBlog()
	else:
		opt_url = "https://blog.csdn.net/AI_BigData_wh/article/details/78326386"
		opt_blogname = "Single_Blogs\\"
		proc = csdnToPdf(opt_blogname, opt_url)
		proc.getBlog()


def operation(opt_url):
	t = Thread(target=opt, args=[opt_url])
	t.setDaemon(True)
	t.start()


# 程序入口
def main():
	global text3
	root = tk.Tk()
	windowWidth = root.winfo_reqwidth()
	windowHeight = root.winfo_reqheight()
	positionRight = int(root.winfo_screenwidth() / 2 - windowWidth / 2)
	positionDown = int(root.winfo_screenheight() / 2 - windowHeight / 2)
	root.geometry("+{}+{}".format(positionRight, positionDown))
	root.title('CSDN博客导出 Build.20190610')
	root.resizable(width=False, height=False)
	ft_title = tkFont.Font(family='Fixdsys', size=18, weight=tkFont.NORMAL)
	ft_hint = tkFont.Font(family='Fixdsys', size=14, weight=tkFont.NORMAL)
	text1 = tk.Label(root, text="输入网址：", font=ft_title, justify='left', anchor='w')
	text1.grid(row=0,column=0,pady=(5,5),padx=(10,0),sticky=EW)
	edit1 = tk.Text(root, height=1, font=ft_hint)
	edit1.grid(row=0,column=1,pady=(5,5),padx=(0,10),sticky=EW)
	text2 = Label(root, text="若为获取整个博客，格式为：https://blog.csdn.net/jacksparrow\n若为获取特定博文，格式为：https://blog.csdn.net/jacksparrow/article/details/12345678\n请勿在网址末尾添加 / \\ 等奇怪符号", font=ft_hint, justify='left', anchor='w')
	text2.grid(row=1,column=1,pady=(0,5),padx=(0,10),sticky=EW)
	button = tk.Button(root, text="开始抓取",font=ft_title,command=lambda:operation(edit1.get("1.0",END)))
	button.grid(row=2, column=0, pady=(5,5), padx=(10, 10), sticky=EW, columnspan=2)
	globalVar.text3 = tk.Label(root, text='等待抓取中......', font=ft_hint, justify='left', anchor='w')
	globalVar.text3.grid(row=3, column=0, pady=(5,5), padx=(10, 10), sticky=EW, columnspan=2)
	root.mainloop()


if __name__=="__main__":
	main()