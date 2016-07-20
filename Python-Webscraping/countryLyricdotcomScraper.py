# -*- coding: utf-8 -*-
"""
webscraper for country-lyrics.com
Created on Wed Jul 20 09:43:35 2016

@author: mmoocarme
"""

from bs4 import BeautifulSoup
import string
import re
import pickle
import requests

# = Helper Functions =========================================================
def visible(element):
    '''
    function to get main body of web page
    '''
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

def strClean(strList):
    '''
    string cleaning function, gets only the lyrics of the text, and removes 
    text enclosed with parenthsis and square brackets
    '''
    headerLength, footerLength = 220, 313
    subList=strList[headerLength:-footerLength] # country-lyrics.com
    cleanList = []    
    for lines in subList:
        noParen = re.sub(r'\([^)]*\)', '', lines)
        noSquare = re.sub(r'\[[^)]*\]', '', noParen)
        cleanList.append(noSquare)
    cleanSong = ' '.join([lines for lines in cleanList])
    return cleanSong

# ================================================================

# = Web scraper ==================================================

baseurl = requests.get('http://www.country-lyrics.com/')
soup = BeautifulSoup(baseurl.content)

# = Get all links by artist first letter
# i.e. 'http://www.country-lyrics.com/artists/a'
artistAlphaLinks = []
for link in soup.find_all('a', href=True):
    if link.has_attr('href') and '.com/artists' in link['href']:
        #print link#['href']
        artistAlphaLinks.append(link['href'])
artistAlphaLinks = list(set(artistAlphaLinks)) # remove duplicates

# = Get all links of artists 
artistLinks = []
for alphaLink in artistAlphaLinks:    
    newurl = BeautifulSoup(requests.get(alphaLink).content)
    for link in newurl.find_all('a', href=True):
        if link.has_attr('href') and '.com/lyrics' in link['href']:
            #print link['href']
            artistLinks.append(link['href'])
artistLinks = list(set(artistLinks)) # remove duplicates
print(len(artistLinks))


# = Get all links of songs 
songLinks = []
for artistLink in artistLinks:    
    newArtisturl = BeautifulSoup(requests.get(artistLink).content)
    for link in newArtisturl.find_all('a', href=True):
        if link.has_attr('href') and '.com/lyrics/' in link['href']:
            #print link['href']
            songLinks.append(link['href'])
songLinks = list(set(songLinks)) # remove duplicates
print(len(songLinks))
# 5369 songs

songLyrics = []
for songLink in songLinks:
    songSoup = BeautifulSoup(requests.get(songLink).content)    
    songData = songSoup.findAll(text=True)
    songResult = filter(visible, songData)
    cleanLyrics = strClean(songResult)
    songLyrics.append(cleanLyrics)
#    print(cleanLyrics)## Extend -> one long list, append -> list length of songs

# dump in pickle file
pickle.dump(songLyrics, open("songLyrics_country-lytics-dot-com.p","wb"))

# output to txt file
f=open('songLyrics_country-lytics-dot-com.txt','w')
for ele in songLyrics:
    f.write((ele).encode('utf8')+'\n')
f.close()