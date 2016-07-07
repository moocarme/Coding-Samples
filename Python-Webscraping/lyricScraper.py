# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 16:49:11 2016

@author: matt-666
"""
import urllib
from bs4 import BeautifulSoup, SoupStrainer
import string
import re
import pickle

# = Helper Functions =========================================================
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

def strClean(strList):
    newRes=strList[276:-57]
    newRes2 = []
    for i in range(len(newRes)-1):
        if newRes[i+1]!='\n' and newRes[i]!='\n': 
            t1 = ' '.join(str(newRes[i]).split()) # removes the \n, which may be needed
            t1 = t1.translate(string.maketrans("",""), string.punctuation)
            newRes2.extend(str.split(t1.lower()))
    return newRes2

# ================================================================

# = Web scraper ==================================================

baseurl = urllib.urlopen('http://www.anycountrymusiclyrics.com/').read()

# = Get all links by artist first letter
artistAlphaLinks = []
for link in BeautifulSoup(baseurl, parseOnlyThese=SoupStrainer('a')):
    if link.has_attr('href') and '.com/artist' in link['href']:
        print link['href']
        artistAlphaLinks.append(link['href'])

# = Get all links of artists 
artistLinks = []
for alphaLink in artistAlphaLinks:    
    newurl = urllib.urlopen(alphaLink).read()
    for link in BeautifulSoup(newurl, parseOnlyThese=SoupStrainer('a')):
        if link.has_attr('href') and '.com/show/artist' in link['href']:
            print link['href']
            artistLinks.append(link['href'])
print(len(artistLinks))

# = Get all links of songs 
songLinks = []
for artistLink in artistLinks:    
    newArtisturl = urllib.urlopen(artistLink).read()
    for link in BeautifulSoup(newArtisturl, parseOnlyThese=SoupStrainer('a')):
        if link.has_attr('href') and '.com/lyrics/' in link['href']:
            print link['href']
            songLinks.append(link['href'])
print(len(songLinks))

# = Get the lyrics of all songs 
songLyrics = []
for songLink in songLinks:
    songSoup = BeautifulSoup(urllib.urlopen(songLink).read())    
    songData = songSoup.findAll(text=True)
    songResult = filter(visible, songData)
    songLyrics.append(strClean(songResult)) ## Extend -> one long list, append -> list length of songs

# = dump in pickle file
pickle.dump(songLyrics, open("songLyrics.p","wb"))
