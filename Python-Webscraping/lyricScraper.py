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
    newRes=strList[276:-57] # specific to this website
    newRes2 = []
    for i in range(len(newRes)-1):
        if newRes[i+1]!='\n' and newRes[i]!='\n': 
            t1 = ' '.join(str(newRes[i]).split()) # removes the \n, which may be needed
            t1 = t1.translate(string.maketrans("",""), string.punctuation)
            newRes2.extend(str.split(t1.lower()))
    return newRes2
    
def get_links(url, lookfor):
    list_of_links = []
    for link in BeautifulSoup(url, parse_only=SoupStrainer('a')):
        if link.has_attr('href') and lookfor in link['href']:
            #print link['href']
            list_of_links.append(link['href'])
    return list_of_links
# ================================================================

# = Web scraper ==================================================

class lyrics_scraper(object):
    
    def __init__(self, url):
        self.baseurl = urllib.urlopen(url).read()
        
    def get_all_links(self):
        # = Get all links by artist first letter
        artistAlphaLinks = get_links(self.baseurl, '.com/artist')    
         
        # = Get all links of artists 
        artistLinks = []
        for alphaLink in artistAlphaLinks:    
            newurl = urllib.urlopen(alphaLink).read()
            artistLinks.extend(get_links(newurl, '.com/show/artist'))
        
        # = Get all links of songs  
        self.songLinks = []
        for artistLink in artistLinks:    
            newArtisturl = urllib.urlopen(artistLink).read()
            self.songLinks.extend(get_links(newArtisturl, '.com/lyrics/'))
        
    def get_corpus(self):
        # = Get the lyrics of all songs 
        self.songLyrics = []
        for songLink in self.songLinks:
            songSoup = BeautifulSoup(urllib.urlopen(songLink).read())    
            songData = songSoup.findAll(text=True)
            songResult = filter(visible, songData)
            self.songLyrics.append(strClean(songResult)) ## Extend -> one long list, append -> list length of songs
        return self.songLyrics
# ============================================================================

if __name__ == "__main__":
    baseurl = 'http://www.anycountrymusiclyrics.com/'
    scraper = lyrics_scraper(baseurl)
    scraper.get_all_links()
    scraper.getLyrics()
    corpus = scraper.get_corpus
    # = dump in pickle file
    pickle.dump(corpus, open("songLyrics.p","wb"))
