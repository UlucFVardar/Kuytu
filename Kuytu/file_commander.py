#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from Articles import Article 
import json
import XML_templates as tp

def checkFilePath(mypath):
    import os
    if not os.path.isdir('/'.join(mypath.split('/')[:-1])):
        os.makedirs( '/'.join(mypath.split('/')[:-1]) )            
    f = open(mypath,'w')
    f.close()    
def save_XML(XMLPath, indexPath, articleList ,type_of_save = None):
    def prettyPrintXml(xmlFilePathToPrettyPrint):
        from lxml import etree
        assert xmlFilePathToPrettyPrint is not None
        parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
        document = etree.parse(xmlFilePathToPrettyPrint, parser)
        document.write(xmlFilePathToPrettyPrint, pretty_print=True, encoding='utf-8')            
    def generate_XML_page(article_object,type_of_save = None):


        def give_paragrafXML(paragraph):

            return tp.paragrafTemplate%re_make_xml_changes(paragraph)
        def give_allArticleBulkText(article_object):
            try:
                return tp.all_text%re_make_xml_changes(article_object.get_allBulkText())
            except Exception as e:
                #print e
                return ''
        def give_allArticleText_clean(article_object):
            try:
                return tp.all_text%re_make_xml_changes(article_object.get_allCleanText())
            except Exception as e:
                #print e
                return ''            
        ##### ''' bura ''' #################

        map = {}
        
        map['Id'] = re_make_xml_changes(article_object.get_Id()).encode('utf-8')
        map['Title'] = re_make_xml_changes(article_object.get_Title()).encode('utf-8')
        map['infoBox_type'] = re_make_xml_changes(article_object.get_infoBox_type()).encode('utf-8')        
        #print 'burda11'
        if type_of_save == 'clean':
            paragraphList_clean = []
            for p in article_object.get_cleanParagraphs():
                paragraphList_clean.append(give_paragrafXML(p).strip())
            map['ParagraphList_XMLtext_clean'] = '\n '.join(paragraphList_clean)
            map['infoBoxTextclean'] = re_make_xml_changes(json.dumps(article_object.get_cleanInfoBox(),indent = 4,ensure_ascii=False, encoding='utf8').encode('utf-8'))
            map['AllText_XMLText_clean'] = give_allArticleText_clean(article_object)        
        #---------
        elif type_of_save == None:
            paragraphList = []
            for p in article_object.get_bulkParagraphs():
                paragraphList.append(give_paragrafXML(p).strip())
            #print 'burda112'
            map['ParagraphList_XMLtext'] = '\n '.join(paragraphList).encode('utf-8')
            #print 'burda113'
            map['infoBoxText'] = re_make_xml_changes(article_object.get_infoBoxText()).encode('utf-8')
            #print 'burda114'
            map['allBulkText'] = re_make_xml_changes(article_object.get_allBulkText()).encode('utf-8')
            #print 'burda115'
            map['AllText_XMLText'] = give_allArticleBulkText(article_object).encode('utf-8')
            #print 'burda116'


        #print json.dumps(map,indent = 4,ensure_ascii=False, encoding='utf8')
        #----
        #print tp.template_clean%map


        try:
            if type_of_save == None:
                return tp.template%map         
            elif type_of_save == 'clean':
                return tp.template_clean%map
        except Exception as e:
            print 'patladi'
            print '*'*10
            print json.dumps(map,indent = 4,ensure_ascii=False, encoding='utf8')
            print '-'*10
            print '\n'*3
            print e
            return None
    ######################################################## ''' 2''' ######################################################
    if len (articleList) == 0 :
        log = '!'+'-'*10+'  There is no Page to Save -- FileName(%31s)'%XMLPath.split('/')[-1]+'-'*10+'!'
        print log
        return log
    checkFilePath(XMLPath)



    f = open(XMLPath,"w")
    f.write('<Pages>\n\t')

    indexfile = open(indexPath,"w")    
    # -------
    err_counter = 0
    indexData = []
    for i,article_object in enumerate(articleList):
        indexFileString = "%s#%s#%d\n"
        if type(article_object)==type(Article()): # article object 
            if type_of_save == 'clean':
                articleXML_text =  generate_XML_page(article_object,type_of_save)
            else:
                #print 'burda1'
                articleXML_text =  generate_XML_page(article_object,type_of_save).decode('utf-8').encode('utf-8') 
                #print 'burda2'
            indexFileString = indexFileString%(make_xml_changes(article_object.get_Id()), make_xml_changes(article_object.get_Title()), i+1 )
        elif type(article_object) == type(tuple()): 
            all_xml_test_as_string, Title, Id = article_object
            indexFileString = indexFileString%( Id , Title, i+1 )
            articleXML_text = all_xml_test_as_string
        else:
            articleXML_text = article_object
            indexFileString = (indexFileString%( 'Indexlenememiş' , 'Indexlenememiş', i+1 )).decode('utf-8')
        if articleXML_text == None:
            err_counter +=1
            continue
        #print 'burda3'
        f.write( articleXML_text.replace('<br />',',').replace('<br>',','))
        #print 'burda4'
        indexfile.write( indexFileString.encode('utf-8') )
    f.write('</Pages>')        
    f.close()
    indexfile.close()
    # ---- 
    try:    
        prettyPrintXml(XMLPath)
        pass
    except Exception as e:
        print e
        print '!! [prettyPrintXml] Execution Had Some Errors!!'
    log =  '!'+'-'*2+' %6d Article Saved Successfully -- FileName(%31s)'%(len(articleList)-err_counter,XMLPath.split('/')[-1])+'-'*10+'!'
    print log
    return log

def save_Uniq_InfoBoxTypes(path,data):
    checkFilePath(path)
    f = open(path,'w')
    for BK_type,hit_count in data:
        line = '%s#%d\n'%(BK_type.encode('utf-8'),hit_count)
        f.write( line )

def save_Graph(output_path,data,min_repetition,title):
    ''' Function draws list of list form data
        [ ['BK Type' , hitCount],
          ['BK Type' , hitCount],
          ['BK Type' , hitCount]....]
    '''
    def draw(x,y,title,saving_path):
        import matplotlib.pyplot as plt
        plt.title(title)
        plt.plot(x, y)
        plt.xticks(x, x, rotation='vertical')
        fig =plt.gcf()
        fig.set_size_inches(20, 11)
        #plt.savefig(saving_path)
        plt.savefig(saving_path,format='eps', dpi=1000)
        plt.show()

    x_list = [x for x,y in data if y>=min_repetition ]
    y_list = [y for x,y in data if y>=min_repetition ]
    draw(   x = x_list, 
            y = y_list, 
            title = title, 
            saving_path = output_path+title)
    #print output_path+title

#-----
def re_make_xml_changes(text):
    return text.replace('>','&gt;').replace('<','&lt;').replace('&','&amp;').replace('\n\n','').replace('\t','')
def make_xml_changes(text):
    return text.replace('&amp;','&').replace('&gt;','>').replace('&lt;','<').replace('\n\n','').replace('\t','')


def read_XML(XML_path):
    ''' This funciton read XML data of Articles that has only InfoBox Data.'''
    import xml.etree.ElementTree as ET
    tree = ET.parse(XML_path)
    root = tree.getroot()

    Articles = []
    for page in root.findall('Page'):
        article_object = Article()
        # Getting title, id, whole text of the article
        article_object.set_id( id = make_xml_changes(page.find('Id').text) )
        article_object.set_title( title = make_xml_changes(page.find('Title').text) )
        article_object.set_infoBox_type( infoBox_type = make_xml_changes(page.find('InfoBoxType').text) )
        article_object.set_infoBoxBulkText ( infoBox = make_xml_changes(page.find('InfoBox_BulkText').text) )
        try:
            article_object.set_allBulkText(allBulkText = make_xml_changes(((page.find('Article_BulkTexts')).find('All_Text')).text) )
            if article_object.get_allBulkText() == '' :
                article_object.del_allBulkText()
        except Exception as e:
            print e

        try:
            article_object.set_bulkParagraphs( Paragraphs = [make_xml_changes(p.text) for p in ((page.find('Article_BulkTexts')).find('Paragraphs')).findall('Paragraph')] )
        except Exception as e:
            print e
        Articles.append(article_object)
        #article_object.__string__()
    return Articles
def save_txt_file(file_path,all_articles):
    all_a = map(lambda a : a.clean_save_json_format(),all_articles)
    checkFilePath(file_path)
    f = open(file_path,'w')
    text = json.dumps(all_a,indent = 4,ensure_ascii=False, encoding='utf8').encode('utf-8')
    f.write(text)
    f.close()

import xlsxwriter
def export_data_2_excel(file_name,articles_data,clomuns):
    checkFilePath(file_name)

    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(file_name)
    for type_ in articles_data.keys():
        worksheet = workbook.add_worksheet(type_)
        row = 0
        mapp_ = {}        
        for j,a in enumerate(articles_data[type_]):
            col = 0
            if j == 0:
                for i,key in enumerate(clomuns[type_]):
                    mapp_[key] = col+i
                    worksheet.write(row, col+i,  key.decode('utf-8')  )
                row += 1

                
            for i,(key,value) in enumerate(a.get_cleanInfoBox().items()):
                if value == None:
                    continue
                col = 0
                worksheet.write(row, mapp_[key], value.decode('utf-8'))
            
            row += 1
    workbook.close()



