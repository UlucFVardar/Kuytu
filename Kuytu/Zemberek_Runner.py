import os


def get_sentences():
    
    def set_environment():
        os.system("mkdir ./outputs")
        os.system("export CLASSPATH=zemberek-full.jar:$CLASSPATH")
        os.system("javac -cp zemberek-full.jar SentenceSplitter.java")
    
    def clear_environment():
        os.system("rm -r zemberek/outputs")
    
    def fixZemberekOutput(zemberek_output_path):
        """
            @szemberek_output_path: output path of SentenceSplitter.java
        """
        fs = []
        ss = []
        with open(zemberek_output_path, "r") as f:
            for line in f:
                if 'None#None' == line.strip():
                    fs.append('None')
                    ss.append('None')  
                    continue

                line_parts = line.strip().split('#')
                
                first_sentence = line_parts[0]
                second_sentence = 'None'
                sentences = {}
                d_flag = False
                o_flag = False
                lngth = len(line_parts)
                for j, part in enumerate(line_parts):
                    try:
                        if part.endswith('o.') and o_flag == False:
                            first_sentence += line_parts[j+1]
                            o_flag = True

                        if d_flag == True:
                            if o_flag == True:
                                try:
                                    second_sentence = line_parts[3]
                                except:
                                    second_sentence = 'None'
                            else:
                                try:
                                    second_sentence = line_parts[2]
                                except:
                                    second_sentence = 'None'

                        if part.endswith('(d.') and d_flag == False:
                            first_sentence = line_parts[j] + " " + line_parts[j+1]
                            d_flag = True
                    except:
                        if '(d.' not in part:
                            first_sentence = line_parts[1]
                        else:
                            first_sentence = 'None-Faulty'
                    
                fs.append(first_sentence)
                ss.append(second_sentence)                    
                #print '\n1. ', first_sentence, '\n2. ',second_sentence, '\n'       
        f.close()
        return fs,ss
    

    # Start
    set_environment()
    
    # Run Java Program   
    # output.txt-->[input]--(SentenceSplitter.java)--[output]--> zemberek_output.txt
    print "\n\n-----Java Kodu Run Edildi------\n\n"
    cmd = "java SentenceSplitter ./outputs/zemberek_output.txt ./outputs/sentenceSplitterInput.txt"
    os.system(cmd)
    
    # Fix output anomalies
    # zemberek_output.txt-->[input]--(dataCleaner.py)--[output]--> (first_sentence, second_sentence), Ack. Message
    print "\n\n-----Find Zemberek Run Edildi------\n\n"
    first_sentences, second_sentences = fixZemberekOutput("./outputs/zemberek_output.txt")
    
    # remove text files
    #os.system("rm ./outputs/output.txt ./outputs/zemberek_output.txt ./outputs/sentenceSplitterInput.txt")
    
    return first_sentences, second_sentences 

# mus be run on terminal 
'''
export CLASSPATH=zemberek-full.jar:$CLASSPATH
javac -cp zemberek-full.jar SentenceSplitter.java
'''
def set_dir():
    print '\n\n\n\n-----------'
    p = os.path.dirname( os.path.realpath( __file__ ))
    if 'Kuytu/zemberek' in p:
        pass
    else:
        p = p + '/zemberek' 
        print 'burda',p
        print '\n\n\n\n-----------'
        os.chdir( p ) 

def create_sentences():

    set_dir()

    ## splitting the sentences
    first_sentences, second_sentences  = get_sentences()

    lines_of_sentence = map(lambda f,s: f+'#'+s ,first_sentences, second_sentences)
    f = open("./outputs/results.txt","w")
    for line in lines_of_sentence:
        f.write(line)
        f.write("\n")
    f.close()


def create_sentence_splittler_input_text(Articles_with_BK):
    set_dir()
    os.system("mkdir ./outputs")
    
    with open("./outputs/sentenceSplitterInput.txt","w+") as f: 
        for i, article in enumerate(Articles_with_BK):
            paragraphs = article.get_cleanParagraphs()
            listSize = len(paragraphs)
            if listSize > 1:
                for j, p in enumerate(paragraphs):
                    p = p.replace('\n',' ').replace('\t',' ').replace('\r',' ').strip()
                    if j == listSize-1:
                        f.write(p)
                    else:
                        f.write(p + " ")
            elif listSize == 1:
                f.write(paragraphs[0].replace('\n',' ').replace('\t',' ').replace('\r',' ').strip())
            else:
                f.write('None#None')
            f.write("\n")
            
        f.close()
        
def re_read_Sentences(Articles_with_BK):


    set_dir()


    f = open('./outputs/results.txt','r')
    lines = f.readlines()
    sentences = map(lambda a: a.split('#'), lines) 
    for i,ss in enumerate(sentences):
        #print ss
        Articles_with_BK[i].set_sentences(ss)
    os.system('rm -r ./outputs')
    