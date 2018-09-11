# -*- coding: utf-8 -*-

import urllib.parse
import requests
import globalVar
import os,time
import urllib
import string
import shutil
import base64
from bs4 import BeautifulSoup
import random
import pdfkit


class csdnToPdf:


	url='https://blog.csdn.net/AI_BigData_wh'
	bName = ''
	blogName='AI_BigData_wh\\'
	blogNameSingle='Single_Blogs\\'
	blogImage='images\\'
	blogDir='\\csdn_blog\\'
	headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0', 'Origin': 'https://blog.csdn.net/'}
	StringPrefix = ''
	StringSurfix = ''
	session = ''
	identifier = ''


	def print(self,content):
		globalVar.text3.configure(text=content)


	def __init__(self, blogName, blogUrl):
		self.blogName = blogName
		self.url = blogUrl
		self.blogDir = os.path.abspath(os.path.dirname(__file__)) + self.blogDir
		self.session = requests.Session()
		try:
			r = self.session.get('https://blog.csdn.net/', headers=self.headers)
		except:
			raise Exception("网络链接出现问题")


	def setReferer(self, url):
		self.headers['Referer'] = url


	#读取html
	def login(self, htmlUrl = '', referer = 'https://blog.csdn.net', data = {}, isImage = False, imageId = "img_1", method = 'GET'):
		time.sleep(0.5)# 防止封IP
		if htmlUrl == '':
			htmlUrl = self.url
		self.setReferer(referer)
		try:
			r = ''
			if method.upper()=='GET':
				r = self.session.get(htmlUrl, headers = self.headers, data = data)
			else:
				r = self.session.post(htmlUrl, headers = self.headers, data = data)
			if isImage:
				file = open(self.blogDir + self.bName + self.blogImage + imageId + '.jpg', 'wb')
				file.write(r.content)
				file.close()
				return r.content
		except:
			raise Exception("网络链接出现问题")
		return r.text


	def fixSynaxHighLighter(self, html):
		soup = BeautifulSoup(html, features='html5lib')
		userSoup = soup.find(name="div", attrs={"class":"blog-content-box"})
		classes=userSoup.findAll(name="pre")    # 处理代码背景色 1/2
		try:
			for cla in classes:
				cla['style'] = "background-color:#DDD"
		except KeyError:
			pass
		classes = userSoup.findAll(name="code")  # 处理代码背景色 2/2
		try:
			for cla in classes:
				cla['style'] = "background-color:#DDD"
		except KeyError:
			pass
		intro=userSoup.findAll(name="div", attrs={"class":"article-bar-top"})   # 处理个人介绍
		try:
			for intr in intro:
				intr.clear()
		except KeyError:
			pass
		loginsoup=userSoup.findAll(name="div", attrs={"class":"hide-article-box text-center"})[0]
		try:
			del(loginsoup)
		except:
			pass
		strr = userSoup.__str__()
		dest = self.StringPrefix + strr + self.StringSurfix
		return dest


	def getBlog(self):
		self.prepareHTMLEnv(mode=2)
		self.identifier = str(int(time.time()))
		destHtml = self.blogDir + self.blogNameSingle + self.identifier + '.html'
		destPdf = self.blogDir + self.blogNameSingle + self.identifier + '.pdf'
		# 获取单个博文标题
		html = self.login(self.url, referer=self.url)
		soup = BeautifulSoup(html, features='html5lib')
		artical = soup.findAll(name='h1', attrs={'class': 'title-article'})[0]
		s = artical.text
		realNamePdf = self.blogDir + self.blogNameSingle + s + '.pdf'
		realNameHtml = self.blogDir + self.blogNameSingle + s + '.html'
		self.saveBlog(destHtml, destPdf, realNamePdf, realNameHtml, self.url)


	def getAllBlogContent(self):
		state=True
		self.print("当前博客内容保存地址：" + self.blogDir)
		pageNum=0
		listNum=0
		html=self.login()
		self.prepareHTMLEnv(mode=1)
		while state:
			soup=BeautifulSoup(html, features='html5lib')
			articals=soup.findAll(name='div',attrs={'class' : 'article-item-box csdn-tracking-statistics'})
			for artical in articals:
				self.identifier = str(int(time.time()))
				listNum += 1
				title = artical.find('a')
				artical_url = title['href']
				self.print('文章链接： ' + artical_url)
				artNum = artical_url.split('/')
				artNum = artNum[-1]
				artNum = "page_" + artNum
				self.print('文章编号： ' + artNum)
				s = self.processArtTitle(title.text)
				s = 'P%02d_%02d_%s' % (pageNum, listNum, s)
				self.print('文章标题： ' + s)
				destHtml = self.blogDir + self.blogName + artNum + '.html'
				destPdf = self.blogDir + self.blogName + artNum + '.pdf'
				realNamePdf = self.blogDir + self.blogName + s + '.pdf'
				realNameHtml = self.blogDir + self.blogName + s + '.html'
				if os.path.isfile(realNamePdf):
					continue
				self.saveBlog(destHtml, destPdf, realNamePdf, realNameHtml, artical_url)
			##换页转换
			pagelist= soup.find(name='div',attrs={'id' : 'pageBox'})
			next=pagelist.findAll('li')
			state=False
			for i in next :
				if i.text.encode('utf-8')==str('下一页') and string.find(i.attrs['class'], 'ui-pager-disabled')==-1:
					pageNum+=1
					listNum=0
					if not self.url.endswith('/'):
						self.url = self.url + '/'
					url2 = self.url + pageNum
					html = self.login(url2)
					state=True
					break


	def saveBlog(self, destHtml, destPdf, realNamePdf, realNameHtml, artical_url):
		htmlContent = self.fixSynaxHighLighter(self.login(artical_url, referer=artical_url))
		soup = BeautifulSoup(htmlContent, features='html5lib')
		self.print("处理图片中......")
		# 处理图片为BASE64
		imgSoup = soup.findAll(name="img")
		id = 0
		for img in imgSoup:
			id = id + 1
			self.login(img['src'],isImage=True,imageId=str(self.identifier)+'_'+str(id))
			img['src'] = "data:image/jpeg;base64," + self.get_image_file_as_base64_data(self.blogDir + self.bName + self.blogImage + str(self.identifier) + '_' + str(id) + '.jpg').decode('UTF-8')
			try:
				del(img['width'])
				del(img['height'])
			except:
				pass
		# 处理公式为BASE64
		self.print("处理公式中......")
		ind = 0
		for (typename, typefsize) in {'math/tex':'16px', 'math/tex; mode=display':'26px'}.items():
			latexsoup = soup.findAll(name="script", attrs={"type": typename})
			for l in latexsoup:
				ind = ind + 1
				if ind % 10 == 0:
					time.sleep(10)
				formulatext = "$$" + str(l.text) + "$$"
				formulatext = formulatext.replace(' ', '')
				all_url = 'http://quicklatex.com/latex3.f'
				Para = {'formula': formulatext, 'fsize': typefsize, 'fcolor': '000000', 'mode': '0', 'out': '1', 'remhost': 'quicklatex.com', 'rnd': random.uniform(0,100)}
				start_html = requests.post(all_url, data=Para)
				img_url = start_html.text.replace("\r\n", " ")
				img_url = img_url.split(' ')
				img_url = img_url[1]
				time.sleep(1.0)
				img = requests.get(img_url)
				f = open(
					self.blogDir + self.bName + "images\\" + 'formula_' + str(self.identifier) + '_' + str(ind) + '.png',
					'wb')
				f.write(img.content)
				f.close()
				latex_img = "<span style=\"position: relative;\"><img style=\"MARGIN:0; PADDING:0\" src=\"data:image/png;base64," + self.get_image_file_as_base64_data(
					self.blogDir + self.bName + "images\\" + 'formula_' + str(self.identifier) + '_' + str(
						ind) + '.png').decode('UTF-8') + "\"/></span>"
				l.insert_after(BeautifulSoup(latex_img, features='html5lib'))
		hidinginfosoup = soup.findAll(name="div", attrs={"class": "hide-article-box text-center"})[0]
		hidinginfosoup['style'] = 'display: none;'
		htmlContent = soup.__str__()
		with open(destHtml, 'w', encoding='utf-8') as f:
			f.write(htmlContent)
		self.print("正在转换为PDF......")
		# 获取页面Cookie
		http_cookie = list()
		cj = self.session.cookies.get_dict()
		for (k,v) in cj.items():
			if '%' in v:
				v = urllib.parse.unquote(v)
			http_cookie.append((k,v))
		pdfkit.from_file(destHtml, destPdf, options = {'custom-header' : [('Origin', 'https://blog.csdn.net'),('Referer', 'https://blog.csdn.net'),('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0')],
		                                               'cookie': http_cookie,
		                                               'enable-local-file-access':'',
		                                               'images': ''})
		while True:
			isExist = os.path.exists(destPdf)
			if isExist:
				break
			time.sleep(1)
		isExist = os.path.exists(realNamePdf)
		if isExist:
			realNamePdf = realNamePdf[:-4] + str(int(time.time())) + '.pdf'
			realNameHtml = realNameHtml[:-5] + str(int(time.time())) + '.html'
		os.rename(destPdf, realNamePdf)
		os.rename(destHtml, realNameHtml)
		self.print("已保存网页： " + realNameHtml)
		time.sleep(2)
		self.print("已保存PDF： " + realNamePdf)


	def processArtTitle(self, title):
		s = title.replace('\r\n', ' ')  # 去掉回车符
		s = s.lstrip()  # 去掉首空格
		s = s.rstrip()  # 去掉尾空格
		s = s.strip()  # 过滤字符串中所有的转义符
		s = s.replace('/', 'or')
		s = s.replace(' ', '')
		s = s.replace('原\n', '')
		s = s.replace('转\n', '')
		s = s.replace('\n', '')
		return s


	def prepareHTMLEnv(self, mode=1):
		surfixFd= open('./Surfix.txt','r')
		prefixFd = open('./prefix.txt','r')
		self.StringPrefix = prefixFd.read()
		self.StringSurfix = surfixFd.read()
		surfixFd.close()
		prefixFd.close()
		self.bName = self.blogName
		if mode != 1:
			self.bName = self.blogNameSingle
		isExist = os.path.exists(self.blogDir+self.bName)
		if not isExist:
			os.makedirs(self.blogDir+self.bName)
		isExist = os.path.exists(self.blogDir + self.bName + self.blogImage)
		if not isExist:
			os.makedirs(self.blogDir + self.bName + self.blogImage)
		else:
			shutil.rmtree(self.blogDir + self.bName + self.blogImage)
			os.makedirs(self.blogDir + self.bName + self.blogImage)
		isExist = os.path.exists(self.blogDir+self.bName+"scripts")
		if not isExist:
			shutil.copytree(os.path.abspath(os.path.dirname(__file__))+"\\scripts", self.blogDir+self.bName+"scripts")


	def get_image_file_as_base64_data(self, path):
		isExist = os.path.exists(path)
		if not isExist:
			open(path, 'a').close()
		with open(path, 'rb') as image_file:
			return base64.b64encode(image_file.read())