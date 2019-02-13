#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
from collections import Counter

import os
import re

from Articles import Article 


class WikiDumpParser:
    def __init__(self,file_path):
        self.Error_articles_list = []

        self.articles = {}
        self.articles['NonStandart_articles_list'] = []
        self.articles['withInfoBox_articles_list'] = []
        self.articles['withOUTInfoBox_articles_list'] = []
        
        self.log = {}
        self.log['#Article_withOut_InfoBox'] =  0 
        self.log['#NonStandart_Article'] = 0 
        self.log['#Total_Article'] = 0 
        self.log['#Article_with_InfoBox'] = 0 
        self.info_box_types = []
        #generation of tree
        tree = ET.parse(file_path)
        self.root = tree.getroot()

    def get_title(self,page):
        return page.find('{http://www.mediawiki.org/xml/export-0.10/}title').text

    def get_id(self,page):
        return page.find('{http://www.mediawiki.org/xml/export-0.10/}id').text

    def get_all_text(self,page):
        Whole_ARC = page.find('{http://www.mediawiki.org/xml/export-0.10/}revision')
        Whole_ARC_without_many_unnecessary_tag = Whole_ARC.find('{http://www.mediawiki.org/xml/export-0.10/}text', {'xml:space': 'preserve'})
        return Whole_ARC_without_many_unnecessary_tag.text

    def get_all_XMLText(self,page):
        xml_fname = ET.tostring(page).replace('ns0:','')\
                                .replace('</page>','</Page>')\
                                .replace('<page','<Page')\
                                .replace(' xmlns:ns0="http://www.mediawiki.org/xml/export-0.10/"','')\
                                .replace('&#287;','ğ')\
                                .replace('&#286;','Ğ')\
                                .replace('&#252;','ü')\
                                .replace('&#220;','Ü')\
                                .replace('&#351;','Ş')\
                                .replace('&#350;','ş')\
                                .replace('&#246;','ö')\
                                .replace('&#214;','Ö')\
                                .replace('&#304;','İ')\
                                .replace('&#305;','ı')\
                                .replace('&#231;','c')\
                                .replace('&#199;','Ç')
                           
                                
        return xml_fname


    def extract_pages(self,StoreAllText , NumberofParagraph  ):        
        for page in self.root.findall('{http://www.mediawiki.org/xml/export-0.10/}page'):
            self.log['#Total_Article'] +=1
            all_xml_test_as_string = self.get_all_XMLText(page)
            tuple_data = None
            try:
                article = Article()
                # Getting title, id, whole text of the article
                article.set_title( title = self.get_title(page) )
                article.set_id( id = self.get_id(page) )
                allBulkText = self.get_all_text(page)
                article.set_allBulkText( allBulkText )
                # -----
                tuple_data = all_xml_test_as_string, article.get_Title(), article.get_Id()

                
                # if there is no article text
                if allBulkText == None:                
                    self.articles['NonStandart_articles_list'].append(tuple_data)
                    self.log['#NonStandart_Article'] +=1
                    continue
                # -----
                
                # Is the article contains a info box or not
                if 'bilgi kutusu' in allBulkText :
                    pass
                else:
                    self.articles['withOUTInfoBox_articles_list'].append(tuple_data)
                    self.log['#Article_withOut_InfoBox'] +=1
                    #saveWOUTInfoBox( all_xml_test_as_string )
                    continue
                # -----

                # cleaning the article text     
                try:
                    article.seperateBulkText(StoreAllText, NumberofParagraph)
                    BK_type = article.get_infoBoxType()
                    if '[' in BK_type or '{' in BK_type or \
                            ']' in BK_type or '}' in BK_type or \
                                len (BK_type) >=30 or '|' in BK_type or BK_type == '':
                        self.articles['NonStandart_articles_list'].append(tuple_data)
                        self.log['#NonStandart_Article'] +=1
                        continue
                except Exception as e:
                    #print e
                    self.articles['NonStandart_articles_list'].append(tuple_data)
                    self.log['#NonStandart_Article'] +=1
                    continue
                # -----
                #article.__string__()
                #break
                self.info_box_types.append( article.get_infoBoxType() )
                self.articles['withInfoBox_articles_list'].append(article)
                self.log['#Article_with_InfoBox'] +=1
                
                
            except Exception as e:
                if tuple_data != None:                    
                    self.articles['NonStandart_articles_list'].append(tuple_data)
                else:
                    self.articles['NonStandart_articles_list'].append(all_xml_test_as_string)
                self.log['#NonStandart_Article'] +=1
                #saveError( all_xml_test_as_string )
                continue
            #save articles
        #save all type

    def get_all_articles(self):
        return self.articles
    def getLog(self):
        return self.log
    def get_uniqInfoBoxTypes(self):
        c = Counter( self.info_box_types )
        return list(c.items())