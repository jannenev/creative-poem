
# coding: utf-8

# In[1]:

import re
from nltk import word_tokenize
import nltk
import random 
import urllib2
import time
from numpy.random import choice
import numpy as np
import sys
#Uses 5-grams provided by Google
#http://storage.googleapis.com/books/ngrams/books/datasetsv2.html


# In[2]:

f = open('as.txt','r')
lines = f.readlines()
f.close()


# In[3]:

def atNoun4Adj(word): #find mostly nouns for adjective. "as 'mysterious' as * Y"
    d={}
    #cut to 10% to make faster
    #i = iter(lines)
    lines_cut = random.sample(lines, len(lines)/10)
    for line in lines_cut: 
      if word in line:   #speeds up by 90% when not needing re.search for each line
        if re.search('as ' +word+ ' as .* .*', line):
            tokens = word_tokenize(line)
            x = tokens[3]
            y = tokens[4]
            count = int(tokens[7])           
            if y not in d:
                 d[y]=0
      #     if y not in d[x]:
       #          d[x][y]=0
            d[y]+=count                
    return d


# In[4]:

def atAdj4Noun(word): # find adjectives for a noun, "as Y as * 'student'"
    d={}
    #cut to 10% to make faster
    #i = iter(lines)
    lines_cut = random.sample(lines, len(lines)/10)
    for line in lines_cut:
      if word in line:  
        if re.search('as .* as .* '+word, line):
            tokens = word_tokenize(line)
            x = tokens[1]
            #y = tokens[4]
            count = int(tokens[7])          
            if x not in d:
                 d[x]=0
            d[x]+=count                
    return d


# In[5]:

# copied from net, http://stackoverflow.com/questions/25714531/find-rhyme-using-nltk-in-python
entries = nltk.corpus.cmudict.entries()
def rhyme(inp, level):
     syllables = [(word, syl) for word, syl in entries if word == inp]
     rhymes = []
     for (word, syllable) in syllables:
             rhymes += [word for word, pron in entries if pron[-level:] == syllable[-level:]]
     return set(rhymes)
# this one is too slow as brute force through cmudict (130k words), better version would be finding
# rhyming words as intersection of 2 sorted sets. Or by building hash version.


# In[6]:

# copied from net, same: http://stackoverflow.com/questions/25714531/find-rhyme-using-nltk-in-python
def doTheyRhyme( word1, word2 ):
  # first, we don't want to report 'glue' and 'unglue' as rhyming words
  # those kind of rhymes are LAME
  if word1.find ( word2 ) == len(word1) - len ( word2 ):
      return False
  if word2.find ( word1 ) == len ( word2 ) - len ( word1 ): 
      return False
  return word1 in rhyme ( word2, 1 )


# In[7]:

# return a word and a dict of words rhyming with it
def getRhyme(d, d2):
    word1 = generate(d) #random item from dict d
    keys_d2 = set(d2.keys())
    all_rhyming = rhyme(word1, 1)
    intersection = keys_d2 & all_rhyming
    keys = intersection
    #remove the word self from rhyming words
    try:
      keys.remove(word1)
    except KeyError:
      pass
    #def extract(d, keys):
    #    return dict((k, d[k]) for k in keys if k in d)
    newdict2 =dict((k, d2[k]) for k in keys)
    # if there would be no rhyming words, add one common rhyming
    if len(newdict2.keys())==0:
        word =str(random.sample(all_rhyming,1))
        word=word[3:-2]
        newdict2[word]=1 
    return word1, newdict2


# In[28]:

def generate(state):  #state is dict with keys and their sums, ie transitions and weights
    #from operator import itemgetter
    #sort(state, key=itemgetter(1))
    elements = state.keys()
    weights = state.values()
    
    together = zip(weights, elements)    
    sorted_together = sorted(together, reverse=True)
    weights= [x[0] for x in sorted_together]
    elements = [x[1] for x in sorted_together]    
    
    #cut to max 200
    if len(elements)>100:
        elements=elements[0:100]
        weights=weights[0:100]
    
    #print(len(elements)) 
        
    total=float(0)
    # from  counts, make probabilities to sum to 1
    for index, item in enumerate(weights):
        total+= item
    for index, item in enumerate(weights):
        weights[index] = item/total
        
    cmptotal=0
    for index, item in enumerate(weights):
        cmptotal+= item
        if random.uniform(0, 1) < cmptotal:
            return elements[index]

    #suffix= np.random.choice(elements, p=weights)     
    return suffix


# In[9]:

# with rhyme
def makeLine(word1, t1,t2, fillwords):    
    text = word1 +' '+ generate(fillwords) +' '+ t1 +' and '+word1 +' ' + generate(fillwords) +' '+ t2+'.'
    return text


# In[10]:

# with rhyme, for noun4(add4(noun))
def makeLine2(word1, adj1 ,adj2, fillwords):    
    if np.random.uniform(0,1) < 0.5:
      text = 'As '+adj1 +' and as '+adj2 +' as '+ word1 +' '+ generate(fillwords)+'.'
    else:
      text = 'So '+adj1 +' and so '+adj2 +' as '+ word1 +' '+ generate(fillwords)+'.'    
    return text


# In[11]:

def getWords(d, d2):    
    ta1 = generate(d)
    tb1 = generate(d2)    
    ta2, dict2 = getRhyme(d, d2)
    tb2= generate(dict2)   
    # if 2 same, do 1st ones again
    i=0
    if ta1==ta2 and i<200:
        d[ta1]=d[ta1]/2
        ta1=generate(d)
        i+=1    
    i=0
    if tb1==tb2 and i<200:
        d2[tb1]=d2[tb1]/2        
        tb1=generate(d2)
        i+=1    
    return ta1, ta2, tb1, tb2    


# In[12]:

fillwords = {}
fillwords["is"] = 50
fillwords["was"] = 40
fillwords["will be"] = 40
fillwords["is so"] = 30
fillwords["is now"] = 15
fillwords["was always"] = 10
#usage generate(fillwords), returns 1 word


# In[13]:

def processWords(word1, word2):
    d = atAdj4Noun(word1)
    d2 = atAdj4Noun(word2)
    d['well']=1 #fix 'well' to smaller as its not correct context "x as well as..." x is not well.
    d['long']=1
    d['soon']=1
    d['far']=1
    d['much']=1
    d['large']=1
    d2['well']=1 
    d2['long']=1 
    d2['soon']=1 
    d2['far']=1
    d2['much']=1
    d2['large']=1
    return d, d2


# In[14]:

def processWords2(word1, word2):
    dA = atAdj4Noun(word1) #dictAdj
    dB = atAdj4Noun(word2)
    dA['well']=1
    dA['soon']=1
    dA['far']=1
    dA['fast']=1
    dA['long']=1
    dA['much']=1    
    dB['well']=1
    dB['soon']=1
    dB['far']=1
    dB['fast']=1
    dB['long']=1
    dB['much']=1    
    adj3 =  generate(dA)
    adj4 =  generate(dA)
    adj5 =  generate(dB)
    adj6 =  generate(dB)
    return adj3,adj4,adj5,adj6


# In[15]:

# reduce weight of common non relating words
def fixWords(dB): #dict
    dB['well']=1
    dB['soon']=1
    dB['far']=1
    dB['fast']=1
    dB['long']=1
    dB['much']=1
    return dB


# In[16]:

# from net http://stackoverflow.com/questions/26320697/capitalization-of-each-sentence-in-a-string-in-python-3
def sentenceCapitalizer(string1):
    sentences = string1.split(". ")
    sentences2 = [sentence[0].capitalize() + sentence[1:] for sentence in sentences]
    string2 = '. '.join(sentences2)
    return string2


# In[17]:

def createPoem(word1='empty', word2='empty'):
    if word1=='empty':
        word1 = random.choice(tokens)
    if word2=='empty':
        word2 = random.choice(tokens)    
    
    t1,t2,t3,t4 = getWords(d, d2)
    poem = makeLine(word1, t1,t2, fillwords) +' '
    poem += makeLine(word2, t3,t4, fillwords)+' \n'    
    return sentenceCapitalizer(poem)


# In[18]:

def createPoem2(word1, word2):    
    adj3, adj4, adj5,adj6 = processWords2(word1, word2)
    dnoun3 = atNoun4Adj(adj3)
    dnoun3 =fixWords(dnoun3)
    noun3 = generate(dnoun3)
    dnoun4 = atNoun4Adj(adj5)
    dnoun4 =fixWords(dnoun4)
    noun4 = generate(dnoun4)
    poem = makeLine2(noun3, adj3, adj4, fillwords)+' '
    poem+= makeLine2(noun4, adj5, adj6, fillwords)+' \n'
    return sentenceCapitalizer(poem)


# In[19]:

print "Give 2 nouns for subjects of a poem."


# In[24]:

print "Give a noun1 (substantive) "
word1 = raw_input()
print "Give a noun2 "
word2 = raw_input()
d,d2 = processWords(word1, word2)


# In[27]:

poem = createPoem(word1,word2) 
print(poem)
sys.stdout.flush()
poem2 = createPoem2(word1, word2)
print(poem2)

