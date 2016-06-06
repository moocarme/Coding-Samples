# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 12:12:07 2016
Updates on Sun Apr 17

@author: matt
"""
# = Import packages
import requests
from lxml import html
from lxml.etree import tostring
import matplotlib.pyplot as plt


# = Helper Functions =========================================================

# = Function to get tab from a webpage in str format
def getTab(url):
    webPage = requests.get(url)
    webTree= html.fromstring(webPage.content)
    tabXpath = '//*[@id="cont"]/pre[2]/text()'
    tab = webTree.xpath(tabXpath)
    return tab

# = Function to get chords from a webpage in str format    
def getChords(url):
    webPage = requests.get(url)
    webTree= html.fromstring(webPage.content)
    tabContentClass = webTree.find_class('js-tab-content')
    chordsList = list(tabContentClass[0].iter('span')) # starts at element 0
    return [tostring(chordsList[i], with_tail = False).strip('</span>') for i in range(len(chordsList))]

# = Function to get xml tree given the band name
def getBandTree(band, page):
    if type(page) == int:
        page = str(page)
    theURL = 'https://www.ultimate-guitar.com/search.php?band_name=' + band + \
        '&type%5B2%5D=300&type2%5B0%5D=40000&rating%5B4%5D=5&tuning%5Bstandard%5D=standard&page=' \
        + page +'&view_state=advanced&tab_type_group=text&app_name=ugt&order=myweight'
    pageBand = requests.get(theURL)
    return html.fromstring(pageBand.content)

# = Function to get xml tree given the genre
def getGenreTree(genre, page):
    if type(page) == int:
        page = str(page)
#    theURL = 'https://www.ultimate-guitar.com/search.php?band_name=' + band + \
#        '&type%5B2%5D=300&type2%5B0%5D=40000&rating%5B4%5D=5&tuning%5Bstandard%5D=standard&page=' \
#        + page +'&view_state=advanced&tab_type_group=text&app_name=ugt&order=myweight'
    theURL = 'https://www.ultimate-guitar.com/search.php?type[2]=300&type2[0]=40000&rating[4]=5' \
        + '\&tuning[standard]=standard&genres[0]=' + genresDict[genre]+ '&page=' + page \
        + '&view_state=advanced&tab_type_group=text&app_name=ugt&order=myweight'
        
    pageBand = requests.get(theURL)
    return html.fromstring(pageBand.content)
    
# = Function sort and count items in a list
def sortAndCount(myList):
    list2dictCount = dict((x, myList.count(x)) for x in myList)
    sortedDictCount = sorted(list2dictCount.items(), key = lambda x:(x[1], x[0]), reverse= True)
    sortedDictCountVal = [x[1] for x in sortedDictCount]
    sortedDictCountKey = [x[0] for x in sortedDictCount]
    return sortedDictCount, sortedDictCountVal, sortedDictCountKey

# = Function to circshift a string
def stringShift(string, shift):
    return string[shift:] + string[:shift]

# ============================================================================
    
band = 'radiohead'
page = '1' # start at page 1, in str format as will be added to html str

# = Dictionary of genres that relate to ultimate guitar website
genresDict = {'alternative': '20', 'country': '6', 'blues': '2', 'classical':'5', \
    'jazz':'11', 'pop':'14', 'reggae': '24', 'rock':'21', 'world':'19'}
genre = 'country'

# = Get xml tree for first page
tree1 = getGenreTree(genre, page)
pages = tree1.find_class('paging')
maxPage = len(list(pages[0].iter('a'))) # see what the max number of pages is
print('Max Page: '+ str(maxPage))

# = Grab song links on the first page
songs = tree1.find_class('song result-link')
songLinks = []
for i in songs:
    songLinks.append(i.get('href'))        

# = Iterate through the remaining pages and add song links
for i in range(maxPage -1):
    looppage = i + 2
    looptree = getGenreTree(genre, str(looppage))
    loopsongs = looptree.find_class('song result-link')
    for song in loopsongs:
        songLinks.append(song.get('href'))

print('No of tabs: ' + str(len(songLinks)))

# = Initialize chords list and add chords from the links
myChords = []
j = 0
for i in songLinks:
    myChords.append(getChords(i))
    j = j + 1

# = Join all lists
chordsTotal = []
for i in range(len(myChords)):
    chordsTotal = chordsTotal + myChords[i]
    
# = Sort and count individual chords from the lists
sortedChordsDict, sortedChordsDictVal, sortedChordsDictKey = sortAndCount(chordsTotal)
sumChords = float(sum(sortedChordsDictVal))
fracSortedChordsDictVal = [i/sumChords*100 for i in sortedChordsDictVal]

# Test chord progression for 1 set of chords
chordProgressionLen = 4
testChords = chordsTotal
chordProgression = [0]*(len(testChords)-chordProgressionLen)
mainChordProgression = [0]*(len(testChords)-chordProgressionLen)
for i in range(len(testChords) - chordProgressionLen):
    chordProgression[i] = ''.join(testChords[i:i+chordProgressionLen])
    mainChordProgression[i] = testChords[i][0] + testChords[i+1][0] + testChords[i+2][0] + testChords[i+3][0]

#sortedMainChordProgDict, sortedMainChordProgDictVal, sortedMainChordProgDictKey = sortAndCount(mainChordProgression)
sortedMainChordProgDict, sortedMainChordProgDictVal, sortedMainChordProgDictKey = sortAndCount(chordProgression)

# Remove permutations of the chords (i.e. GCDAm == CDAmG)
newChordProg = []
newChordProgVals = []
noEntries = 100
for j in range(len(sortedMainChordProgDictKey[:noEntries])):
    permutationsTmp = [stringShift(sortedMainChordProgDictKey[j],k) for k in range(len(sortedMainChordProgDictKey[j]))]
    if not any([[jj == x for x in newChordProg] for jj in permutationsTmp]):
        newChordProg.append(sortedMainChordProgDictKey[j])
        newChordProgVals.append(sortedMainChordProgDictVal[j])

# PLot in bar chart        
plt.figure(4); plt.clf()
res = 20
plt.bar(range(len(newChordProgVals[:res])), newChordProgVals[:res], align='center')
plt.xticks(range(len(newChordProgVals[:res])), newChordProg[:res], rotation = 60)
plt.draw()