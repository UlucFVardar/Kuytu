#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
'''

{
  "Article_CleanTexts": {},
  "Title": "Cengiz Han",
  "Article_BulkTexts": {
    "Paragraphs": [ 
      "...", "..."
    ]
  },
  "infoBoxText": ".."
  "infoBox_type": "Kraliyet",
  "Id": "10"
}
'''
import re
import json
class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items)-1]

    def size(self):
        return len(self.items)

class Article:
	def __init__(self):
		self.article_data = dict()
		self.article_data['Article_BulkTexts'] = {}
		self.article_data['Article_CleanTexts'] = {}
		self.article_data['Article_BulkTexts']['Paragraphs'] = []
		

	def get_infoBoxType(self):
		return self.article_data['infoBox_type']
	def set_id(self,id):
		self.article_data['Id'] = id.strip().replace('&','&amp;')

	def set_title(self,title):
		self.article_data['Title'] = title.strip().title().replace('&','&amp;')

	def set_infoBoxBulkText(self,infoBox):
		self.article_data['infoBoxText'] = infoBox.strip().replace('>','&gt;').replace('<','&lt;').replace('&','&amp;') #.replace('\n|','\n\t\t\t\t|')

	def set_infoBox_clean(self,infoBox_clean):
		self.article_data['cleanInfoBox'] = infoBox_clean

	def set_infoBox_type(self,infoBox_type):
		self.article_data['infoBox_type'] = infoBox_type.strip().title().replace('&','&amp;')

	def set_allBulkText(self,allBulkText):
		self.article_data['Article_BulkTexts']['allBulkText'] = allBulkText.strip().replace('>','&gt;').replace('<','&lt;').replace('&','&amp;')	

	def add_bulkParagraph(self,paragraph):
		paragraph = paragraph.strip().replace('>','&gt;').replace('<','&lt;').replace('&','&amp;')
		try:
			self.article_data['Article_BulkTexts']['Paragraphs'].append( paragraph )
		except Exception as e:
			self.article_data['Article_BulkTexts']['Paragraphs'] = []
			self.article_data['Article_BulkTexts']['Paragraphs'].append( paragraph )

	def get_Id(self):
		return self.article_data['Id']
	def get_Title(self):
		return self.article_data['Title']
	def get_infoBoxText(self):
		return self.article_data['infoBoxText']
	def get_infoBox_type(self):
		return self.article_data['infoBox_type']
	def get_allBulkText(self):
		try:
			return self.article_data['Article_BulkTexts']['allBulkText'] 
		except Exception as e:
			return Exception("user doesn't want alltext")
	def get_bulkParagraphs(self):
		return self.article_data['Article_BulkTexts']['Paragraphs']
	def add_cleanParagraph(self,paragraph):
		try:
			self.article_data['Article_CleanTexts']['Paragraphs'].append( paragraph )
		except Exception as e:
			self.article_data['Article_CleanTexts']['Paragraphs'] = []
			self.article_data['Article_CleanTexts']['Paragraphs'].append( paragraph )        	
	


	def add_sentences(self,sentence):
		try:
			self.article_data['Article_CleanTexts']['Sentences'].append( paragraph )
		except Exception as e:
			self.article_data['Article_CleanTexts']['Sentences'] = []
			self.article_data['Article_CleanTexts']['Sentences'].append( paragraph )		
	def __string__(self):
		print json.dumps(self.article_data,indent = 4,ensure_ascii=False, encoding='utf8')#.encode('utf-8')
	#----------------
	def seperateBulkText(self,StoreAllText, NumberofParagraph):
		def stack_check(text):
			stack = Stack()
			lines = text.split("\n")
			isFirst = True
			isFinish = False
			infoBox = []
			for line in lines:
			    openB = line.count("{{")
			    closeB = line.count("}}")
			    for i in range(0,openB):
			        stack.push('{{')
			    if isFirst == True and openB!=0:
			        isFirst=False
			        n = stack.pop()
			    for i in range(0,closeB):
			        if stack.size()>0:
			            if stack.peek() == '{{':
			                n = stack.pop()
			            else:
			                isFinish = True
			        else:
			            isFinish = True
			    infoBox.append(line)
			    if isFinish == True:
			        break
			infoBox = '\n'.join(infoBox)
			return infoBox
		def seperateParagraph(article,text,NumberofParagraph):
			counter = 0
			for p in text.split('\n\n'):
				if len(p)>10:
					article.add_bulkParagraph(p)
					counter +=1
				if counter == NumberofParagraph : 
					break			
		'''infoBox and Text seperate'''
		text = self.article_data['Article_BulkTexts']['allBulkText']
		article_txt = text[:text.find("==")]
		infoBoxType = (re.search('{{(.*) bilgi kutusu', article_txt)).group(1)
		self.set_infoBox_type(infoBoxType)

		# a little cleaning
		temp = article_txt.split('\n')
		for i in range(0,len(temp)):
			if 'bilgi kutusu' in temp[i]:
				break
			else:
				temp[i]=''
		article_txt = '\n'.join(temp)

		infoBox = stack_check( text = article_txt)
		self.set_infoBoxBulkText( infoBox = infoBox )		
		article_txt = article_txt[article_txt.find(infoBox)+len(infoBox):]
		seperateParagraph(self, article_txt ,NumberofParagraph)
		if StoreAllText == True:
			article_all_txt = text[text.find(infoBox)+len(infoBox):]
			self.set_allBulkText( article_all_txt )
		else : 
			del self.article_data['Article_BulkTexts']['allBulkText']



