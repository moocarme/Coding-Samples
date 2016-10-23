# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 16:49:11 2016

@author: matt-666
"""
from urllib import urlopen
from bs4 import BeautifulSoup, SoupStrainer
from string import maketrans, punctuation
from re import match
from pickle import dump

# = Helper Functions =========================================================
def visible(element):
    '''
    Filters all extraneous parts of he webpage out, and returns true only for 
    the visible text in the webpage
    '''
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

def strClean(strList):
    '''
    Cleans string by removing extraneous text on ends such as adverisements and
    text on every webpage and returns just the lyrics for the song
    '''
    newRes=strList[276:-57] # specific to this website
    newRes2 = []
    for i in range(len(newRes)-1):
        if newRes[i+1]!='\n' and newRes[i]!='\n': 
            t1 = ' '.join(str(newRes[i]).split()) # removes the \n, which may be needed
            t1 = t1.translate(maketrans("",""), punctuation)
            newRes2.extend(str.split(t1.lower()))
    return newRes2
    
def get_links(url, lookfor):
    '''
    Looks for just the links of a webpage that have a certain sub-string in them
    '''
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
        self.baseurl = urlopen(url).read()
        
    def get_all_links(self):
        '''
        Gets all the song links on the website
        '''
        # = Get all links by artist first letter
        artistAlphaLinks = get_links(self.baseurl, '.com/artist')    
         
        # = Get all links of artists 
        artistLinks = []
        for alphaLink in artistAlphaLinks:    
            newurl = urlopen(alphaLink).read()
            artistLinks.extend(get_links(newurl, '.com/show/artist'))
        
        # = Get all links of songs  
        self.songLinks = []
        for artistLink in artistLinks:    
            newArtisturl = urlopen(artistLink).read()
            self.songLinks.extend(get_links(newArtisturl, '.com/lyrics/'))
        
    def get_corpus(self):
        '''
        Get the lyrics from all songslinks on the website
        '''
        self.songLyrics = []
        for songLink in self.songLinks:
            songSoup = BeautifulSoup(urlopen(songLink).read())    
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
    dump(corpus, open("songLyrics.p","wb"))
