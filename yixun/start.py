#--coding:utf-8--


'''
	yixun_crawler - 易迅网站商品信息收集器
	author: scott
	date:

	目前仅考虑单点设备登录

	lxml 的xpath还存在部分问题（还是自己没完全领会呢？）
'''

import imp
imp.load_source('init','../init_script.py')
import gevent
from gevent import monkey
from gevent.pool import  Pool

monkey.patch_socket()

import psycogreen.gevent
# psycogreen.gevent.patch_psycopg()

import os,os.path,sys,struct,time,traceback,signal,threading,copy,base64,datetime

# from django.db import connection
# from django.db.models import Sum
from django.db import transaction

import yixun.models as  yixun

from bson.objectid import ObjectId
import lxml.etree as etree

import urllib2,urlparse

dbfile = 'goods.txt'

runPool = Pool(50)

fdbfile = open(dbfile,'wb')

class ResourceItem:
	def __init__(self,text,href=None,tag=None,parent=None):
		self.text = text
		self.tag=tag
		self.href=href
		self.children=[]
		self.parent = parent


def scrape_page(url,pageIndex,cat1,cat2,cat3):
	print 'scrape_page:',url

	req = urllib2.urlopen(url)
	data = req.read()
	# savefile(data)
	html = etree.HTML(data.decode('utf-8'))
	del data
	del req
	#page size

	curPage = 0
	r = html.xpath('//*[@id="list"]/div[5]/div[2]/span/b/text()')
	if not r: return False
	curPage = r[0]
	r = html.xpath('//*[@id="list"]/div[5]/div[2]/span/text()')
	if not r : return False
	pageNum = int(r[0][1:])
	print pageNum,curPage,pageIndex

	#有一种情况，传入大于总page数量的值，server会返回第一个page

	if pageIndex > pageNum:
		return False


	#检索品牌
	goods = html.xpath(u"//div[@class='mod_goods']")
	if not goods:
		print 'skipped..'
		return False
	# return True

	for g in goods:
		image = None
		name = ''
		price =None
		link = ''
		for e in g.getchildren():
			if e.get('class') == 'mod_goods_img':
				for e2 in e.getchildren():
					if e2.get('class') == 'link_pic':
						image_url = e2.getchildren()[0].get('init_src')
						# print image_url
						# print e2.getchildren()[0].keys()
						req = urllib2.urlopen(image_url)
						image = req.read()
						print 'goods image size:',len(image)

			if e.get('class') ==  'mod_goods_info':	#一下search动作用xpath无法实现，所以只好挨个查找

				for  p in e.getchildren():
					if p.get('class')=='mod_goods_tit':
						a= p.getchildren()[0]
						name =  a.text.encode('utf-8')
						link = a.get('href')

					if p.get('class')=='mod_goods_price':
						price = p.getchildren()[0].getchildren()[-1].text.encode('utf-8')
			pass
		if name and price and link :
			# print name , price ,link
			text = "%s || %s || %s || %s || %s || %s\n"%(cat1,cat2,cat3,name,price,link.strip())

			print text
			gitem = yixun.GoodsItem()

			gitem.cat1 = cat1
			gitem.cat2 = cat2
			gitem.cat3 = cat3
			gitem.name = name
			gitem.url =  link

			gitem.image = image
			try:
				gitem.price = float(price)

			except:
				traceback.print_exc()
			gitem.save()

					# fdbfile.write(text)
					# fdbfile.flush()

			del gitem
			image = None
	del goods
	del html
	return True

	# ss= p.xpath('..//dd/a')

'''
http://searchex.yixun.com/705740t705741-1-/?YTAG=2.1738456040037
http://searchex.yixun.com/html?path=705740t705741&area=1&sort=0&show=0&page=2&size=40&pf=0&as=0&charset=utf-8&YTAG=2.1738456040037#list
http://searchex.yixun.com/html?path=705740t705741&area=1&sort=0&show=0&page=1&size=40&pf=0&as=0&charset=utf-8&YTAG=2.1738456040037#list
'''
def scrape_cat(cat,yPageId,yPageLevel,tag,cat1,cat2,cat3):
	try:
		print cat.href
		#parse url
		url = cat.href
		fs =  urlparse.urlparse(url)
		path,qs=fs[2],fs[4]
		cat_idx =  path[1:].split('-')[0]
		# tag = qs.split('=')[1]
		tag = "%s.%s%s"%(yPageLevel,yPageId,tag)
		#make path url
		for page in range(1,500):
			print 'page:',page
			url = "http://searchex.yixun.com/html?path=%s&area=1&sort=0&show=0&page=%s&size=40&pf=0&as=0&charset=utf-8&YTAG=%s#list"%(cat_idx,page,tag)
			if not scrape_page(url,page,cat1,cat2,cat3):
				break

		return


	except:
		traceback.print_exc()
		# print 'page is null,skipped..'

def savefile(d,filename='sample.html'):
	f = open(filename,'w')
	f.write(d)
	f.close()

def test():
	try:
		url = 'http://searchex.yixun.com/705740t705741-1-/?YTAG=2.1738456040037'
		fs =  urlparse.urlparse(url)
		path,qs=fs[2],fs[4]
		cat_idx =  path[1:].split('-')[0]
		tag = qs.split('=')[1]
		print cat_idx,tag

		return

		all_url = 'http://searchex.yixun.com/html?YTAG=3.705766287001&path=705882t705893'
		req = urllib2.urlsplit(all_url)
		html = req.read()
		savefile(html)

		dom = etree.HTML(html.decode('utf-8'))
		p = dom.xpath(u"//div[@title='品牌']")[0]
		ss= p.xpath('..//dd/a')
		print ss[0].text.encode('utf-8')

	except:
		traceback.print_exc()

def craw_start():
	import re
	try:
		all_url = 'http://searchex.yixun.com/?YTAG=2.1738456090000'
		req = urllib2.urlopen(all_url)
		html = req.read()

		# group = re.search("window\.yPageId ='(.*?)'",html)
		yPageId = re.search("window\.yPageId\s*=\s*'(\d+?)'",html).group(1)
		yPageLevel = re.search("window\.yPageLevel\s*=\s*'(\d+?)'",html).group(1)
		print yPageId,yPageLevel

		dom = etree.HTML(html.decode('gb2312'))
		all_cats=[]
		cat1_list = dom.xpath("//div[@class='m_classbox']")
		for cat in cat1_list:
			cat1_text = cat.xpath('h3/text()')[0]
			cat1_e = ResourceItem(cat1_text)
			all_cats.append(cat1_e)
			print cat1_e.text.encode('utf-8')
			div = cat.xpath("div")[0]
			for dl in  div.xpath('dl'):
				cat2 = dl.xpath('dt/a')[0]
				cat2_e = ResourceItem(cat2.text,href=cat2.attrib['href'],tag=cat2.attrib['ytag'],parent=cat1_e)
				cat1_e.children.append(cat2_e)
				print ' '*4,cat1_e.text.encode('utf-8'),cat2_e.href,cat2_e.tag
				for cat3 in dl.xpath('dd/a'):
					cat3_e = ResourceItem(cat3.text,href=cat3.attrib['href'],tag=cat3.attrib['ytag'],parent=cat2_e)
					cat2_e.children.append(cat3_e)
					print ' '*8,cat3_e.text.encode('utf-8'),cat3_e.href,cat3_e.tag
		tasks =[]
		for e1 in all_cats:
			print '-'*1,e1.text.encode('utf-8')
			for e2 in e1.children:
				print '  '*2	,e2.text.encode('utf-8')
				for e3 in e2.children:
					print '  '*4,e3.text.encode('utf-8')
					# task = gevent.spawn(scrape_cat,e3,yPageId,yPageLevel,e2.tag,e1.text.encode('utf-8'),e2.text.encode('utf-8'),e3.text.encode('utf-8'))
					runPool.spawn(scrape_cat,e3,yPageId,yPageLevel,e2.tag,e1.text.encode('utf-8'),e2.text.encode('utf-8'),e3.text.encode('utf-8'))
					# tasks.append(task)
					# scrape_cat(e3,yPageId,yPageLevel,e2.tag,e1.text.encode('utf-8'),e2.text.encode('utf-8'),e3.text.encode('utf-8'))
					# return
		print 'total tasklet size:',len(tasks)
		# gevent.joinall(tasks)
		runPool.join()
	except:
		traceback.print_exc()


if __name__ == '__main__':
	craw_start()
	# test()
	pass
