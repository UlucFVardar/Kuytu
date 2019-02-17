#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# @author =__Uluç Furkan Vardar__

'''Simple usage



'''

import re
import json


def configure_BK_fieldsMaps():
	''' User can easly add a new field in maps or banned fields here, 
		Also User can edit the map with in the program
	'''
	month = [   'Ocak',
	            'Şubat',
	            'Mart',
	            'Nisan',
	            'Mayıs',
	            'Haziran',
	            'Temmuz',
	            'Ağustos',
	            'Eylül',
	            'Ekim',
	            'Kasım',
	            'Aralık']

	key_banned = ['imza',
				   'internet',
	              'resim',
	              'resimboyutu',
	              'websitesi',
	              'renkler',
	              'altyazı',
	              'plakşirketi',
	              'internetsitesi',
	              'resmiinternetsitesi'
	              'image',
	              'resimadı',
	              'genişlet',
	              'screenshot',
	              'logo',
	              'resimyazısı']

	value_banned = ["<!--",
	                "yalın liste|",
	                ""]	              	              



	value_maps = { 	'ad' : 		   	[   'adı'		,
										'isim'		,
										'ismi'		,
										'adi'		,
										'name'		,
										'karakteradı'],

					'doğumtarihi' : [	'dogumtarihi'],
					'meslek'	  : [	'mesleği'	 ]


					}


	maps = {}

	maps['value_maps'] = value_maps
	maps['month'] = month
	maps['key_banned'] = key_banned
	maps['value_banned'] = value_banned
	return maps
	


def clean_InfoBoxBulk( Bulk_InfoBoxText ):
	def step1(infoBox):
		#some cleanings
		infoBox = re.sub(r"\[\[Dosya.*\]\]","",infoBox)
		infoBox = re.sub(r"<br/>","",infoBox)
		infoBox = re.sub(r"<br />","",infoBox)    
		infoBox = re.sub(r"<br>","",infoBox)
		#infoBox = infoBox.replace('[[','').replace(']]','').replace("\'\'\'",'').replace("''",'')
		#infoBox = infoBox.replace('{{','').replace('}}','')
		infoBox = re.sub(r"<ref(.|\n)*</ref>","",infoBox)
		infoBox = infoBox.replace(u'\xa0', u' ')
		return infoBox
	def step2(infoBox):
		#empty place will be deleted
		t = infoBox.split('\n')
		infoBox = []
		for i in range(0,len(t)):
			line = t[i]
			if ' ' == line or ' ' == line or '  ' == line or '' == line:
				continue
			elif line.count('=') == 1:
				if len(line[line.find('='):].replace(' ','')) <3:
					continue
				else:
					infoBox.append(t[i])
			else:
				infoBox.append(t[i])
		infoBox = '\n'.join(infoBox)
		return infoBox
	def step3(infoBox):
		text = infoBox
		try:
			lines = text.replace('<nl>','\n').split('\n')
			temp = {}
			for i in range(1,len(lines)):
				temp_key = ""
				temp_value = ""
				lines[i] = lines[i].strip()
				if lines[i].count('=') == 1:
					if '|' in lines[i]:
						m = re.search(".*\|(.*)=(.*)",lines[i])
						#print lines[i]
						temp_key = (m.group(1)).replace('|','').strip()
						temp_value = m.group(2).strip()
						temp[temp_key] = temp_value
					else:
						#print lines[i],"-----"
						#print 'HATA!! PİPE YOK..'
						continue
				else:
					if '}}' == lines[i]:
						continue
					#print lines[i],"-----"
					#print 'HATA! BİRDEN FAZLA EŞİTTİR/Yok......\n\n\n\n'
					continue  
			return temp
		except Exception as e:
			return None
	Bulk_InfoBoxText = step1(Bulk_InfoBoxText)
	Bulk_InfoBoxText = step2(Bulk_InfoBoxText)
	Bulk_InfoBoxText = step3(Bulk_InfoBoxText)
	Bulk_InfoBoxText = clean_jsonvalues(Bulk_InfoBoxText)
	#print json.dumps(Bulk_InfoBoxText,indent=4,ensure_ascii=False, encoding='utf8')
	return Bulk_InfoBoxText





#----------
# . ['adı','isim','ismi','adi','name','karakteradı'] --> 'ad'
def key_map(data,maps ):
	for maped_value in maps['value_maps'].keys():
		if data in maps['value_maps'][maped_value]:
			return maped_value
	return data


# for clean infoBox
def clean_jsonvalues(infobox):
	maps = configure_BK_fieldsMaps()
	try:
	    newjson = {}
	    for key in infobox.keys():
	    	infobox[key] = infobox[key].encode('utf8')
	        new_key = key.encode('utf8').replace(' ','').replace('_','').lower()

	        # banned key 
	        if new_key in  maps['key_banned']  or\
	        	 infobox[key] in maps['value_banned']:
	        	continue

	        ## Key cleaning
	        new_key = key_map(new_key,maps)

	        ## Value cleaning
	        new_value = infobox[key].replace("'",'').replace('\"','')
	        if new_key != 'ad':
	            new_value =  clean_pipes(new_value)
	        else:
	            new_value =  remove_brackets_with_text(new_value)
	        
	        
	        new_value =  clean_tags(new_value)
	        new_value =  remove_brackets(new_value)	        
	        if new_key == 'meslek' :
	        	parts = new_value.replace(' ,',',').replace(', ',',').replace(' , ',',').split(',')
	        	new_value = ', '.join(parts[:-1]) +' ve '+ parts[-1]
	        if 'tarihi' in new_key:
	        	new_value =  date_map(new_value,maps)

	        newjson[new_key] = new_value        

	    return newjson
	except Exception as e:
	    print e,'[Line: 168 ]'
	    return None





# . [[asdasda]], deneme ---> , deneme
def remove_brackets_with_text( data):
    pattern= r'({{([^}}]*)}}|\[\[([^\]\]]*)\]\])'
    try:
        data = re.sub(pattern,"",data)
        return data.strip()
    except Exception as e:
        return data


# . [[Cenova]]{{,}} [[İtalya]] --> Cenova, İtalya
def remove_brackets( data):
    pattern= r'{{|}}|\[\[|\]\]'
    try:
        return re.sub(pattern,"",data)#re.sub(r"^.*?<[/].*?>|<.*?(.|\s)*?</.*?>|<.*?(.|\s)*","",data)
    except:
        return data

# . [[Film yapımcısı|Yapımcı]] , {{Film yönetmeni|Yönetmen}} --->Yapımcı, Yönetmen
def clean_pipes( data):
    pattern  = '(\[\[[^\]\]]*\|([^\]\]]*)\]\])|({{[^}}]*\|([^}}]*)}})' 
    p = re.compile(pattern, re.MULTILINE)
    try:
        if p:
            clean = p.sub(r'\2', data)
            if '|' not in clean:
            	return clean
    except Exception as e:
        pass
    pattern  = '({{[^}}]*\|([^}}]*)}})|(\[\[[^\]\]]*\|([^\]\]]*)\]\])' 
    p = re.compile(pattern, re.MULTILINE)
    try:
        if p:
            clean = p.sub(r'\2', data)
            return clean
    except Exception as e:
        return data        

# . <br> --> ,
def clean_tags( data):
    try:
        data = re.sub(r"((<br />.*?<br />|<br />)|(<br>.*?<br>|<br>))",", ",data)
    except:
        pass
    try:
        return re.sub(r"<.*?\/>|<.*?</.*?>",", ",data)#re.sub(r"^.*?<[/].*?>|<.*?(.|\s)*?</.*?>|<.*?(.|\s)*","",data)
    except:
        return data
    
# . {{Doğum tarihi|1818|5|5}} ---> 5 Mayıs 1818
# . {{ölüm tarihi ve yaşı|1883|03|14|1818|05|05}} ---> 14 Mart 1883
# . 1162 ---> 1162   
# . 123 ---> 123       
# . 2188 2 2 --->  2 Şubat 2188
# . 2188.2.2 --->  2 Şubat 2188
def date_map( date_value,maps ):
    date_value = '{{'+date_value+'}}'
    orj = date_value
    converted_date = date_value
    try : 
        value = re.findall(r"(\|\d+|\d+)", date_value, re.MULTILINE) ## finding numbersafter pipes
        value = [int(w.replace('|', '')) for w in value]  # clean pipes |
        if len(value) == 3:
            converted_date = "%s %s %s"%(value[2],  maps['month'][value[1]-1],value[0])
            return converted_date
        elif len(value) == 6:
            year1 = int(value[0])
            year2 = int(value[0+3])
            if year1 >year2:
                converted_date = "%s %s %s"%(value[2],  maps['month'][value[1]-1],value[0])
                return converted_date
            else:
                converted_date = "%s %s %s"%(value[2+3],  maps['month'][value[1+3]-1],value[0+3])
                return converted_date
        elif len(value) == 1:
            if len(str(value[0])) == 4 or len(value[0]) ==3:
                converted_date = str(value[0])
                return converted_date
    except Exception as e:
        #print e
        pass
    try:
        '''
        value = orj                
        if value.count('-') >0:
            value = value[:value.find('-')]
            if 'M.' in value[:2] or 'MS' == value[:2] or 'MÖ' == value[:2]:
                converted_date = str(value.encode('utf-8'))
                return converted_date
        '''
        value = orj.replace(',',' ').replace('  ',' ').replace('.',' ')
        if len(value.split(' ')) == 3:
            if value.split(' ')[1].decode('utf-8') in  month:
                converted_date =  str(value)
            if value.split(' ')[1].isdigit():
                value = value.split(' ')
                converted_date = str(value[2])+' '+ str( month[value[1]-1]) + ' ' + str(value[0])
        return converted_date            
    except Exception as e:
        #print e
        pass
    return None
    #----------------------------------------------


#--------------------


def clean_Bulk_Text( Bulk_Text ):
	# delete '[[Dosya.*]]'
	Bulk_Text = clean_dosya(Bulk_Text)

	print Bulk_Text,'---'
	# . [[asdasda]], deneme ---> , deneme
	Bulk_Text = remove_brackets_with_text(Bulk_Text)
	print Bulk_Text,'---'
	# . [[Cenova]]{{,}} [[İtalya]] --> Cenova, İtalya
	Bulk_Text = remove_brackets(Bulk_Text)
	print Bulk_Text,'---'
	# . [[Film yapımcısı|Yapımcı]] , {{Film yönetmeni|Yönetmen}} --->Yapımcı, Yönetmen
	Bulk_Text = clean_pipes(Bulk_Text)


	print Bulk_Text,'---'
	# delete <.*?>.*?</.*?> TAGS
	Bulk_Text = clean_tags_regex(Bulk_Text)
	print Bulk_Text,'---'
	#  [[ ... | ... ]]
	#Bulk_Text = clean_pipes_in_double_square_brackets(Bulk_Text)     
	print Bulk_Text,'---'
	# delete {{...}} double curly brackets
	#Bulk_Text = clean_double_curly_brackets(Bulk_Text)
	print Bulk_Text,'---'
	# remove ' """ ' and  " ''' " in sentence
	Bulk_Text = clean_triple_quoates(Bulk_Text)
	print Bulk_Text,'---'
	Bulk_Text = clean_unknown(Bulk_Text)
	print Bulk_Text,'---'
	return Bulk_Text

# ----- Little functions
def clean_dosya( data):
    try:
        return re.sub(r"\[\[Dosya.*\]\]","",data)
    except:
        return data
# . [[asdasda]], deneme ---> , deneme
def remove_brackets_with_text(data):
    pattern= r'({{([^}}]*)}}|\[\[([^\]\]]*)\]\])'
    try:
        data = re.sub(pattern,"",data)
        return data.strip()
    except Exception as e:
        return data
# . [[Cenova]]{{,}} [[İtalya]] --> Cenova, İtalya
def remove_brackets(data):
    pattern= r'{{|}}|\[\[|\]\]'
    try:
        return re.sub(pattern,"",data)#re.sub(r"^.*?<[/].*?>|<.*?(.|\s)*?</.*?>|<.*?(.|\s)*","",data)
    except:
        return data

# . [[Film yapımcısı|Yapımcı]] , {{Film yönetmeni|Yönetmen}} --->Yapımcı, Yönetmen
def clean_pipes(data):
    pattern  = '(\[\[[^\]\]]*\|([^\]\]]*)\]\])|({{[^}}]*\|([^}}]*)}})' 
    p = re.compile(pattern, re.MULTILINE)
    try:
        if p:
            clean = p.sub(r'\2', data)
            return clean
    except Exception as e:
        return data

def clean_pipes_in_double_square_brackets( data):
    try:
        return re.sub(r"\[\[[^\[\{]*\|","",data).replace('[','').replace(']','') # \[\[.*?\|
    except:
        return data.replace(']','').replace('[','')        

def clean_tags_regex(data):
    try:
        data = re.sub(r"((<br />.*?<br />|<br />)|(<br>.*?<br>|<br>))",", ",data)
    except:
        pass
    try:
        return re.sub(r"<.*?\/>|<.*?</.*?>",", ",data)#re.sub(r"^.*?<[/].*?>|<.*?(.|\s)*?</.*?>|<.*?(.|\s)*","",data)
    except:
        return data      



def clean_double_square_brackets( data):
    # Cancelled for now
    try:
        data = re.sub(r"\(.*\)","",data).replace(']]','') # \(.*\) # \(.*?\[\[[\D].*?\]\].*?\)
    except:
        pass
    try:
        data = data.replace('[[','').replace(']]','')
    except :
        return data
def clean_double_curly_brackets(data):
    try:
        return re.sub(r"\(({{.*?(.|\s).*?}})\)|({{.*?(.|\s).*?}})","",data)
    except:
        return data        

def clean_unknown(data):
	try:
		return infoBox.replace(u'\xa0', u' ')
	except:
		return data
def clean_triple_quoates( data):
    try:
        return data.replace("'''",'').replace("''",'').replace('"','').replace("\'\'\'",'').replace("''",'')
    except:
        return data	


def clean_double_equation_mark( data): #==
    try:
        return re.sub(r"==.*?==","", data)
    except:
        return data

