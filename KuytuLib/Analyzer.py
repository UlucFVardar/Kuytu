#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# @author =__Uluç Furkan Vardar__

# -*- coding: utf-8 -*-

'''
    

'''


from collections import Counter
import os

def seperate_articles_according_to_type(articles):
    seperated_articles = {}
    for a in articles:
        try:
            seperated_articles[a.get_infoBox_type()].append(  a)
        except Exception as e:
            seperated_articles[a.get_infoBox_type()] = []
            seperated_articles[a.get_infoBox_type()].append(  a)
    return seperated_articles

def data_field_counter(seperated_articles):
    count_data ={}
    total_count_data = Counter()
    
    for type_ in seperated_articles.keys():
        #print type_,'stars'
        in_cat_Counter = Counter()
        for a in seperated_articles[type_]:
            in_cat_Counter += Counter(a.get_cleanInfoBox().keys())
            total_count_data += Counter(a.get_cleanInfoBox().keys())
        count_data[type_] = in_cat_Counter
    return total_count_data, count_data 

def datafield_map(map_,seperated_articles):
    for type_ in seperated_articles.keys():
        #print type_,'stars'
        if map_.get(type_,'') == '':
            continue
        for i,a in enumerate(seperated_articles[type_]):
            new_infoBox = dict([(map_[type_].get(k,k), v) for k, v in a.get_cleanInfoBox().items()])
            seperated_articles[type_][i].set_infoBox_clean( new_infoBox )
    return seperated_articles

def save_count_data( path, total_count_data, count_data, total_first_n, subcat_first_n, total_article_count, subcats_article_counts):
    mypath = path
    if not os.path.isdir(mypath):
        os.makedirs(mypath)
    #------------ TOTAL 
    total_file = open(path+'/total_counts.txt','w')
    head = '%-30s\t,%6s\t,%s------>Over All Sum : %d\n'%('Field Name','Hit Count', 'Hit Ratio Over All(%)',total_article_count)+'_'*70+'\n'
    total_file.write(head)
    for datafield,n in total_count_data.most_common(total_first_n):
        string = '%-30s\t,%6d\t,%s%.2f\n'%(datafield,n,'%', (n/total_article_count*100) )
        total_file.write(string)
    total_file.close()

    #------------ SUB
    for type_ in count_data.keys():
        sub_cat_file = open(path+'/'+str(type_)+'_counts.txt','w')
        head = '%-30s\t,%6s\t,%s------>Over All Sum : %d\n'%('Field Name','Hit Count', 'Hit Ratio Over All(%)',subcats_article_counts[type_])+'_'*70+'\n'
        sub_cat_file.write(head)
        for datafield,n in count_data[type_].most_common(total_first_n):
            string = '%-30s\t,%6d\t,%s%.2f\n'%(datafield,n,'%', (n/subcats_article_counts[type_]*100) )
            sub_cat_file.write(string)
        sub_cat_file.close()





'''
import yaml
import matplotlib.pyplot as plt
import pandas as pd
import json
import os 
from file_commander import Article

class Article_Analyzer():
    def __init__(self,articles):
        self.articles = articles
        self.calculate_all_uniq_infoBoxTypes()

    def ignore_other_types(self,interested_infobox_type):
        new_list = []
        for one_article in self.articles:
            if one_article.article['infoBox_type']  in interested_infobox_type:
                new_list.append(one_article)
        self.articles = new_list
        self.calculate_all_uniq_infoBoxTypes()

        
    def calculate_all_uniq_infoBoxTypes(self):
        c = Counter()
        for a in self.articles:
            try:
                infoBox_type = a.article['infoBox_type'].decode('utf-8')
            except Exception as e:
                continue
            try:
                c[infoBox_type] +=1
            except Exception as e:
                c[infoBox_type] = 1
        self.all_infoBoxType_counter = c
    
    def get_all_uniq_infoBoxTypes_as_list(self,limit):
        temp = []
        for type_ in self.all_infoBoxType_counter.items():
            if int(type_[1]) > limit:
                s = ('%s#%d' % (type_[0],type_[1]))
                temp.append(s)
        return temp
    
    def get_all_uniq_infoBoxTypes_for_save(self,limit):
        temp = []
        for type_ in self.all_infoBoxType_counter.items():
            if int(type_[1]) > limit:
                s = ('%-35s -> %d' % (type_[0],type_[1]))
                temp.append(s)
        return '\n'.join(temp)

    def get_one_example_for_every_infoBox_type(self):
        examples = []
        for oneType in self.get_all_uniq_infoBoxTypes_as_list(1):
            oneType = oneType.split('#')[0]
            for a in self.articles:
                if a.article['infoBox_type'].decode('utf-8') == oneType:
                    value = oneType, a.article
                    examples.append(value)
                    break
        return examples
    

    # --- Data Field Analysis ----------
    def count_data_fields(self):
        counter_of_fields = {}

        for a in self.articles:
            try:
                type_ = a.article['infoBox_type'].decode('utf-8')
            except Exception as e:
                continue            
            try:
                counter_of_fields[type_]['count'] += Counter(a.article['clean_infoBox'].keys())
                counter_of_fields[type_]['number'] += 1 
            except Exception as e:
                counter_of_fields[type_] = {}
                counter_of_fields[type_]['count'] = Counter(a.article['clean_infoBox'].keys())
                counter_of_fields[type_]['number'] = 1     
        self.counter_of_fields = counter_of_fields

    def save_allCounts_2_file(self,output_path):
        allCounters = Counter()
        number = 0
        for i in self.counter_of_fields.keys():
            allCounters += self.counter_of_fields[i]['count']
            number += self.counter_of_fields[i]['number']

        f = open(output_path+'all_count.txt',"w")
        aa = '#Info Box Types : {}, #Total article with infoBox: {}\n\n'.format(len(self.counter_of_fields.keys()),number)
        a = json.dumps( allCounters.most_common() , ensure_ascii=False, encoding='utf8',indent = 4).encode('utf-8')
        self.allCounters = allCounters
        f.write(aa)
        f.write(a)
        f.close()

    def save_Counts_for_types(self,output_path):
        # her bir cat için bastırma counter
        if not os.path.isdir(output_path+'Counters/'):
            os.makedirs(output_path+'Counters/')
        for i in self.counter_of_fields.keys():
            name = str(i.encode('utf-8'))
            f = open(output_path+'Counters/'+name+'.txt',"w")
            aa = 'Info Box Type : {}, #Total article with this infoBox: {}\n\n'.format(name,self.counter_of_fields[i]['number'])
            a = json.dumps(self.counter_of_fields[i]['count'].most_common(), ensure_ascii=False, encoding='utf8',indent = 4).encode('utf-8')
            f.write(aa)
            f.write(a)
            f.close()

    def save_uniq_fields(self,output_path):
        path = output_path+'Uniq/'
        if not os.path.isdir(path):
            os.makedirs(path)    
        for who in range (0,len(self.counter_of_fields.keys())):
            st = 'Uniq Data Fields for {} -------\n'.format(self.counter_of_fields.keys()[who].encode('utf-8'))
            one_type = self.counter_of_fields[self.counter_of_fields.keys()[who]]['count']
            other_types = {}
            other_types =  [ self.counter_of_fields[k]['count']  for k in self.counter_of_fields.keys() if k != self.counter_of_fields.keys()[who]]
            result = []
            for element in one_type.keys():
                Flag = False
                for cs in other_types:
                    if cs[element] != 0:
                        Flag=True
                if Flag == False:
                    result.append(element)
            #strr = ' \n'.join(result)
            f= open(path+self.counter_of_fields.keys()[who]+'_Uniq_Fields.txt',"w")
            f.write(st)
            f.write(json.dumps(result, ensure_ascii=False, encoding='utf8',indent = 4).encode('utf-8'))

    def save_dataField_Analysis(self,output_path):
        f= open(output_path+'Counts2.txt',"w")
        for i in self.counter_of_fields.keys():
            a = []
            for j in self.counter_of_fields[i]['count'].most_common(10):
                y = self.counter_of_fields[i]['number']
                b = json.dumps(j, ensure_ascii=False, encoding='utf8').\
                            replace(']','').replace('[','')\
                            .replace('"','').replace(',',':').strip()
                bb = int(b.split(':')[1].strip())
                a.append( ('%26s|')%( b ))
            u = str(i.encode('utf-8'))
            ab = '%26s -> %6s' % (i,str(self.counter_of_fields[i]['number']))
            for bb in a:
                ab += bb
            f.write(ab.encode('utf-8'))
            f.write('\n') 

        # çıktı göresterme
        f.write('\n')
        for i in self.counter_of_fields.keys():
            a = []
            for j in self.counter_of_fields[i]['count'].most_common(10):
                y = self.counter_of_fields[i]['number']
                b = json.dumps(j, ensure_ascii=False, encoding='utf8').\
                            replace(']','').replace('[','')\
                            .replace('"','').replace(',',':').strip()
                bb = int(b.split(':')[1].strip())
                a.append( ('%20s: %.2f|')%( b.split(':')[0].strip(),bb/float(y) ))
            u = str(i.encode('utf-8'))
            ab = '%26s -> %6s' % (i,str(self.counter_of_fields[i]['number']))
            for bb in a:
                ab += bb
            f.write(ab.encode('utf-8'))
            f.write('\n')

        # çıktı göresterme
        f.write('\n')
        for i in self.counter_of_fields.keys():
            a = []
            for j in self.counter_of_fields[i]['count'].most_common(10):
                y = self.counter_of_fields[i]['number']
                b = json.dumps(j, ensure_ascii=False, encoding='utf8').\
                            replace(']','').replace('[','')\
                            .replace('"','').replace(',',':').strip()
                bb = int(b.split(':')[1].strip())
                if bb/float(y)>=0.60:
                    a.append( ('%20s: %.2f|')%( b.split(':')[0].strip(),bb/float(y) ))
                else:
                    a.append( ('%26s|')%( '' ))
            u = str(i.encode('utf-8'))
            ab = '%26s -> %6s' % (i,str(self.counter_of_fields[i]['number']))
            for bb in a:
                ab += bb
            f.write(ab.encode('utf-8'))
            f.write('\n') 
        f.write('\n\nGenel durum\n')    
        total = ('%25s|')%(json.dumps(self.allCounters.most_common(20), ensure_ascii=False, encoding='utf8').\
                            replace(']','').replace('[','')\
                            .replace('"','').replace(',',':').strip() )
        f.write(total.encode('utf-8'))
        f.close()

    # --------------------------------


    # ---- Drawing -------- --------- 
    def draw(self,x,y,title,saving_path):
        plt.title(title)
        plt.plot(x, y)
        plt.xticks(x, x, rotation='vertical')
        fig =plt.gcf()
        fig.set_size_inches(20, 11)
        #plt.savefig(saving_path)
        plt.savefig(saving_path,format='eps', dpi=1000)
        plt.show()
        
    def print_info(self,x,y):
        pd.set_option('display.height', 1000)
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)
        df_more_than_1 = pd.DataFrame({'Info Box Type':x , 'Repetitions':y})
        print df_more_than_1.count()
        print df_more_than_1

    def draw_Repetition_of_all_InfoBoxTypes(self,output_path,title,min_repetition):
        x = []
        y = []
        for type_ in self.all_infoBoxType_counter.items():
            if type_[1] < min_repetition:
                continue
            x.append(type_[0])
            y.append(type_[1])
        self.draw(x = x, 
                  y = y, 
                  title = title, 
                  saving_path = output_path+title)

        #self.print_info(x = x,y = y)
        return len(x)
    
            
            
    # --------------------------------
'''