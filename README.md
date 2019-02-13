
### Needed Lib for Next Instractions


```python
#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from Kuytu.wikiLog import KuytuLog
from Kuytu.WikiDumpParser import WikiDumpParser
import Kuytu.file_commander as K_fc

import json
```

##### Create custom Log from Kuytu


```python
log = KuytuLog('BlackBoxCode')
```

---

## SEPERATION Starts

##### Giving Wiki-Dump XML path wait for seperation


```python
# ----------- WIKI DUMP XML PARSE ------------------------------- Execution ----
# XML Getting Memory
print '-'*10 + 'WIKI DUMP XML GETTING MEMORY' + '-'*10 
#wdp = WikiDumpParser('./Data/wikidump.xml')
wdp = WikiDumpParser('./Data/part.xml') # A Part of The Orjinal WIKI-DUMP Data

# Starting to parse all page in XML file
print '-'*14 + 'WIKI DUMP PARSE START' + '-'*13
wdp.extract_pages(StoreAllText = False, NumberofParagraph = 2 )
# ------------------------------------------------------------------------------
```

    ----------WIKI DUMP XML GETTING MEMORY----------
    --------------WIKI DUMP PARSE START-------------


##### After Seperation saving Seperation Log to our 'Kuytu_log' file


```python
# ----------- WIKI DUMP XML PARSE -------------- Save Log Info (of execution)---
# non_article_count, no_infoBox_count, error_count, number_of_total_article, number_of_article_has_infoBox
log.save_log('WIKI DUMP PARSE - RESULT', json.dumps(wdp.getLog(),indent=4,ensure_ascii=False, encoding='utf8') )
# ------------------------------------------------------------------------------
```

##### Take the  [Uniq Info Box Type - Hit Count] data and Graph it


```python
# ----------- WIKI DUMP XML PARSE -------------- Save Uniq InfoBoxCounts (B.K.)-
output_path = log.get_output_path()
#print json.dumps( wdp.get_uniqInfoBoxTypes(),indent=4,ensure_ascii=False, encoding='utf8')
K_fc.save_Uniq_InfoBoxTypes( output_path + '/Uniq-BK-Types-Hit-Counts.txt', wdp.get_uniqInfoBoxTypes() )
K_fc.save_Graph( output_path = output_path
                ,data = wdp.get_uniqInfoBoxTypes()
                ,min_repetition = 100
                ,title = 'Uniq-BK-Types-Hit-Counts-Graph(>100)' )
log.logging('Uniq-BK-Types-Hit-Counts-Graph(>100) Saved')
# ------------------------------------------------------------------------------
```

##### Save The Seperated Pages in 3 Group
    -> Template of the returnin valu of wdp.get_all_articles()
    { 
        "withInfoBox_articles_list" 	: [....articleObject...],
        "withOUTInfoBox_articles_list"  : [..(article_XML_TEXT,Article_Title,Article_Id)..],
        "NonStandart_articles_list" 	: [..article_XML_TEXT..]
    }


```python
# ----------- WIKI DUMP XML PARSE ----------------------- Save Article Pages ---
allArticles = wdp.get_all_articles()


# Pages WithOut InfoBox 
withOUTInfoBoxPagesXMLPath = output_path + 'BulkData/withOUTInfoBoxPages_bulkXML.xml'
withOUTInfoBoxPagesIndexPath = output_path + 'BulkData/withOUTInfoBoxPages_bulkXML_index.txt'
l1 = K_fc.save_XML(withOUTInfoBoxPagesXMLPath, withOUTInfoBoxPagesIndexPath, allArticles['withOUTInfoBox_articles_list'] )

# Pages With InfoBox 
StandartPagesXMLPath = output_path + 'BulkData/withInfoBoxPages_bulkXML.xml'
StandartPagesIndexPath = output_path + 'BulkData/withInfoBoxPages_bulkXML_index.txt'
l2 = K_fc.save_XML(StandartPagesXMLPath, StandartPagesIndexPath, allArticles['withInfoBox_articles_list'] )

# Pages - NonStandart
nonStandartPagesXMLPath = output_path + 'BulkData/NonStandartPages_bulkXML.xml'
nonStandartPagesIndexPath = output_path + 'BulkData/NonStandartPages_bulkXML_index.txt'
l3 = K_fc.save_XML(nonStandartPagesXMLPath, nonStandartPagesIndexPath, allArticles['NonStandart_articles_list'] )

log.logging([l1,l2,l3])  ## Save '.save_XML' log.
# ------------------------------------------------------------------------------
```

    !--    330 Article Saved Successfully -- FileName(withOUTInfoBoxPages_bulkXML.xml)----------!
    !--     30 Article Saved Successfully -- FileName(   withInfoBoxPages_bulkXML.xml)----------!
    !----------  There is no Page to Save -- FileName(   NonStandartPages_bulkXML.xml)----------!

---

### First part of the Wiki Full Extraction is finished

##### The Outputs are ;
![alttext](https://raw.githubusercontent.com/UlucFVardar/Kuytu/master/Examples/Output_of_seperation.png)




