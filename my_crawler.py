#coding=UTF-8
import urllib
import urllib2
import re

# 剔除多余的标签的类
class RemoveTagTool:
    # 去除img标签,7位长空格
    removeImg = re.compile('<img.*?>| {7}|')
    # 删除超链接标签
    removeAddr = re.compile('<a.*?>|</a>')
    # 把换行的标签换为\n
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    # 将表格制表<td>替换为\t
    replaceTD= re.compile('<td>')
    # 把段落开头换为\n加空两格
    replacePara = re.compile('<p.*?>')
    # 将换行符或双换行符替换为\n
    replaceBR = re.compile('<br><br>|<br>')
    # 将其余标签剔除
    removeExtraTag = re.compile('<.*?>')
    def replace(self,x):
        x = re.sub(self.removeImg,"",x)
        x = re.sub(self.removeAddr,"",x)
        x = re.sub(self.replaceLine,"\n",x)
        x = re.sub(self.replaceTD,"\t",x)
        x = re.sub(self.replacePara,"\n    ",x)
        x = re.sub(self.replaceBR,"\n",x)
        x = re.sub(self.removeExtraTag,"",x)
        # strip()将前后多余内容删除
        return x.strip()

# 爬虫类
class TIEBA_CRAWLER:
	# 初始化
	def __init__(self,tiebaURL,seeLZ):
		# 保存此次要爬的网址
		self.url = tiebaURL
		# 是否要只看楼主，最后加在上面的url后面形成最终的url
		self.seeLZ = '?seeLZ=' + str(seeLZ)
		# 保存帖子的题目，如果失败则使用默认的title
		self.title = "tieba_crawler"
		# 如果上面的title爬取成功，则最后保存的txt也为这个名称
		self.file = None
		# 剔除多余标签
		self.removeTagTool = RemoveTagTool()

	# 根据page num来获得每一个page
	def getPage(self, page_num):
		# 形成最终的访问url
		url = self.url + self.seeLZ + '?pn=' + str(page_num)
		# 建立请求
		request = urllib2.Request(url)
		# 建立响应
		response = urllib2.urlopen(request)
		return response.read()

	# 先获得第一页，从第一个page中获得page num
	def getPageNum(self, page):	
		# 该表达式可以在网页的数据中找到，其他pattern同理
		pattern = re.compile('<li class="l_reply_num".*</span>.*<span.*>(.*)</span>')
		result = re.search(pattern, page)
		return result.group(1).strip()

 	# 获得page的title，同获得page num
	def getPageTitle(self, page):
		pattern = re.compile('class="core_title_txt.*>(.*)</h.>')
		result = re.search(pattern, page)
		return result.group(1).strip()

	# 由page获得每个page的真正内容，即每一楼的数据
	def getOnePageContent(self, page):
		pattern = re.compile('<div id="post_content_.*?>(.*?)</div>')
		# 本来此处的items已经可以作为return的对象了，但是因为贴吧会有表情或者超链接等，而这些在txt中无法表示，所以需要剔除。有兴趣的可以直接返回items，看看txt里面是什么东西
		items = re.findall(pattern, page)
		contents = []
		for item in items:
			# 剔除无法显示的image
			content = "\n" + self.removeTagTool.replace(item) + "\n"
			contents.append(content)
		return contents

	# 将数据写入txt
	def writeData(self, contents):
		self.file.write("One Page:----------------------------------------------------------\n")
		for content in contents:
			self.file.write(content)
		self.file.write("\n\n\n")
	
	# 爬虫的入口函数
	def crawl(self):
		# 获得页面page 1
		page = self.getPage(1)
		# 根据页面1获得页数pageNum
		pageNum = self.getPageNum(page)
		# 获得页面的pageTitle
		pageTitle = self.getPageTitle(page)
		# 设置页面的title和txt文件的名称
		if pageTitle:
			self.title = pageTitle
			self.file = open(self.title + ".txt", "w+")

		#根据每页的内容page，筛选出需要的内容content
		print "总共" + str(pageNum) + "页"
		for i in range(1, int(pageNum)+1):
			print "正在写入第" + str(i) + "页"
			page = self.getPage(i)
			onePageContents = self.getOnePageContent(page)
			#把内容写入文件txt
			self.writeData(onePageContents)

print "请输入贴吧帖子网址"
tiebaURL = 'http://tieba.baidu.com/p/' + str(raw_input('http://tieba.baidu.com/p/'))
seeLZ = raw_input("是否只获取楼主发言，0：不是，1：是\n")
crawler = TIEBA_CRAWLER(tiebaURL,seeLZ)
crawler.crawl()
