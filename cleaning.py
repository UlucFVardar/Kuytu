#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from Kuytu.wikiLog import KuytuLog
from Kuytu.WikiDumpParser import WikiDumpParser
import Kuytu.file_commander as K_fc
import Kuytu.Analyzer as Analyzer


import json
from collections import Counter


# In[2]:


log = KuytuLog('BlackBoxCode','r')
output_path = log.get_output_path()
StandartPagesXMLPath = output_path + 'BulkData/withInfoBoxPages_bulkXML.xml'

Articles_with_BK = K_fc.read_XML(StandartPagesXMLPath)


# In[3]:

# --------------- Cleaning infoboxes -----------
from Kuytu.article_cleaner_kit import clean_InfoBoxBulk #* # clean_InfoBoxBulk, set_BK_fieldsMaps, get_BK_fieldsMaps

for i,a in enumerate(Articles_with_BK):
    Articles_with_BK[i].set_infoBox_clean( infoBox_clean = clean_InfoBoxBulk( a.get_infoBoxText()) )    



# In[4]:
# --------------- eleminating un-cleaned parts -----------
Articles_with_BK_clean =  filter(lambda a: a.get_cleanInfoBox() != None , Articles_with_BK)


# In[5]:

# --------------- Saving Clean DA's Articles -----------
uniq_types = map(lambda a : a.get_infoBox_type() , Articles_with_BK_clean)
c = Counter( uniq_types )
uniq_types_histogram = list(c.items())

output_path = log.get_output_path()
#print json.dumps( wdp.get_uniqInfoBoxTypes(),indent=4,ensure_ascii=False, encoding='utf8')
K_fc.save_Uniq_InfoBoxTypes( output_path + '/Uniq-BK-Types-Hit-Counts-Graph-Clean(>100).txt', uniq_types_histogram )
K_fc.save_Graph( output_path = output_path
                ,data = uniq_types_histogram
                ,min_repetition = 100
                ,title = 'Uniq-BK-Types-Hit-Counts-Graph-Clean(>100)' )
log.logging('Uniq-BK-Types-Hit-Counts-Graph-Clean(>100) Saved')
# ------------------------------------------------------------------------------



# In[6]:

prt_log = '#Articles parsed clean '+ str(len(Articles_with_BK_clean))

log.logging(prt_log)
print prt_log

# In[7]:

# --------------- Our interested Info Box Types --------------------
Interested_Info_Box_Types = [ u'Hakem' ,u'Manken' ,u'Makam Sahibi' ,u'Filozof' ,u'Bilim Insanı',u'Güreşçi' 
                             ,u'Bilim Adamı' ,u'Sporcu' ,u'Buz Patencisi',u'Asker' 
                             ,u'Voleybolcu' ,u'Sanatçı',u'Futbolcu' ,u'Oyuncu' 
                             ,u'Müzik Sanatçısı' ,u'Yazar' ,u'Kraliyet' ,u'Tenis Sporcu' ,u'Profesyonel Güreşçi'
                             ,u'Kişi' ,u'Basketbolcu']
Interested_articles_with_BK_clean =  filter(lambda a: a.get_infoBox_type() in Interested_Info_Box_Types , Articles_with_BK_clean)

log.save_log('Interested ınfoBoxes are', str(Interested_Info_Box_Types) )

# In[8]:

prt_log = '#Articles interested categories '+ str(len(Interested_articles_with_BK_clean))

log.logging(prt_log)
print prt_log








# In[9]:
import Kuytu.Analyzer as Analyzer

#------------ Analysis Start -----------------------------------
'''
format of 'seperated_interested_articles'

{
     "ınfo_box_type_1" : [.....list of articles....],
     "ınfo_box_type_2" : [.....list of articles....],
     "ınfo_box_type_3" : [.....list of articles....],
     "ınfo_box_type_4" : [.....list of articles....],
     "ınfo_box_type_5" : [.....list of articles....],
     "ınfo_box_type_6" : [.....list of articles....]
     }
'''
seperated_interested_articles = Analyzer.seperate_articles_according_to_type(Interested_articles_with_BK_clean)


# In[10]

# same domain type join
seperated_interested_articles[u"Bilim Insanı"] += seperated_interested_articles[u"Bilim Adamı"]
del seperated_interested_articles[u"Bilim Adamı"]


# In[11]:

# mappin data fields of ınfo boxes 
map_ = {
    u'Manken' :{
        "yer" : "doğumyeri"
    },
    u'Hakem' : {
        "etkinyıl" : "aktifyıl",
        "yıl" : "aktifyıl",
        "yer" : "doğumyeri"
    }
}         
seperated_interested_articles = Analyzer.datafield_map(map_, seperated_interested_articles)


# In[12]:

# data field countings
total_count_data, count_data = Analyzer.data_field_counter(seperated_interested_articles)      


# In[13]:
# sa

output_path = log.get_output_path()
total_article_count = float(len(Interested_articles_with_BK_clean))
subcats_article_counts =  { type_ :float(len(list_)) for type_,list_ in seperated_interested_articles.items()}

Analyzer.save_count_data( path = output_path + 'Counts'
                        , total_count_data =  total_count_data
                        , count_data = count_data
                        , total_first_n = 100
                        , subcat_first_n = 20
                        , total_article_count = total_article_count
                        , subcats_article_counts = subcats_article_counts )


# In[ ]:
import Kuytu.Analyzer as Analyzer

# ------ deleting un-needed datafields
interested_datafields =  {
    u"Hakem" :               ["ad","doğumtarihi" ,"turnuva"    ,"aktifyıl","doğumyeri"],
    u"Sporcu" :              ["ad","doğumtarihi" ,"spor"       ,"doğumyeri","ülke"],
    u"Kraliyet"  :           ["ad","doğumtarihi" ,"hanedan"    ,"hükümsüresi","ölümtarihi"],
    u"Voleybolcu" :          ["ad","doğumtarihi" ,"pozisyon"   ,"doğumyeri"],
    u"Manken" :              ["ad","doğumtarihi" ,"ulus"       ,"doğumyeri"],
    u"Oyuncu" :              ["ad","doğumtarihi" ,"meslek"     ,"yer","ölümtarihi"],
    u"Asker" :               ["ad","doğumtarihi" ,"rütbesi"    ,"doğumyeri","ölümtarihi"],
    u"Makam Sahibi" :        ["ad","doğumtarihi" ,"makam"      ,"doğumyeri"],
    u"Buz Patencisi" :       ["ad","doğumtarihi" ,"ülke"       ,"koç"],
    u"Profesyonel Güreşçi" : ["ad","doğumtarihi" ,"doğumyeri"],
    u"Kişi" :                ["ad","doğumtarihi" ,"meslek"     ,"doğumyeri","ölümtarihi"],
    u"Futbolcu" :            ["ad","doğumyeri"   ,"pozisyon"   ,"doğumtarihi"],
    u"Tenis Sporcu" :        ["ad","doğumyeri"   ,"oyunstili"  ,"doğumtarihi"],
    u"Bilim Insanı" :        ["ad","doğumyeri"   ,"dalı"       ,"doğumtarihi"],
    u"Filozof" :             ["ad","doğumyeri"   ,"doğumtarihi","çağ"],
    u"Basketbolcu" :         ["ad","doğumyeri"   ,"pozisyon"   ,"doğumtarihi"],
    u"Güreşçi" :             ["ad","doğumyeri"   ,"doğumtarihi","ölümtarihi"],
    u"Yazar" :               ["ad","doğumyeri"   ,"meslek"     ,"doğumtarihi","ölümtarihi"],
    u"Müzik Sanatçısı":      ["ad","artalan"     ,"tarz"       ,"etkinyıllar","meslek"],
    u"Sanatçı" :             ["ad","alanı"       ,"ölümtarihi" ,"ölümyeri"]
}
seperated_interested_articles2 = Analyzer.hold_interested_datafields(interested_datafields, seperated_interested_articles)


# In[ ]:
seperated_interested_articles3={}
for type_ in seperated_interested_articles2.keys():
    seperated_interested_articles3[type_] = filter(lambda a : len(a.get_cleanInfoBox().keys()) != 0 , seperated_interested_articles2[type_] )



# In[ ]:

print json.dumps(seperated_interested_articles3['Hakem'][3].get_cleanInfoBox(),indent = 4,ensure_ascii=False, encoding='utf8')#.encode('utf-8')

print '-'*10
#print json.dumps(seperated_interested_articles3['Futbolcu'][3].__string__(),indent = 4,ensure_ascii=False, encoding='utf8')#.encode('utf-8')


# In[ ]:
K_fc.export_data_2_excel('../dememe.xlsx',seperated_interested_articles3,interested_datafields)

# In[ ]:
import Kuytu.file_commander as K_fc

all_clean_articles = [ seperated_interested_articles3[type_] for type_ in seperated_interested_articles3.keys()]
all_clean_articles = sum(all_clean_articles, [])
# Pages With InfoBox 
StandartPagesXMLPath = output_path + 'CleanData/withInfoBoxPages_cleanXML.xml'
StandartPagesIndexPath = output_path + 'CleanData/withInfoBoxPages_cleanXML_index.txt'
l2 = K_fc.save_XML(StandartPagesXMLPath, StandartPagesIndexPath, all_clean_articles, 'clean')


# In[ ]:

import Kuytu.file_commander as K_fc
Txt_File_path = output_path + 'CleanData/withInfoBoxPages_cleanXML_index.txt'
K_fc.save_txt_file(Txt_File_path, all_clean_articles)


# In[ ]:





# In[ ]:





# In[15]:





# In[16]:





# In[17]:


a = 'asdasda asdda'


# In[18]:


a.title()
import re


# In[19]:


orj = '{{Ölüm yılı ve yaşı|1947|1889}}'
reg = "[^\|]*ve yaşı\|(\d*)\|\d*"
match = re.search(r"[^\|]*ve yaşı\|(\d*)\|\d*", orj)
print match.group(1)  


# In[ ]:





# In[ ]:





# In[47]:


a ='MüZisyen, ŞArkıcı, RapçI ve ProdüKtöR'


# In[49]:


print a.lower()


# In[57]:


new_value = 'Sağ el çift el backhand'


# In[68]:


print new_value[:inew_value.find(';')]


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




