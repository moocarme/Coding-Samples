# -*- coding: utf-8 -*-
"""
Created on Sun Mar 20 12:12:07 2016
Updates on Sun Apr 17
Added SQL database on July 10th

@author: matt
"""
# = Import packages
import requests
from lxml import html
from lxml.etree import tostring
import sqlite3
import collections
import re

# = Helper Functions =========================================================

def removeTags(string):
    '''
    Function to remove html tags
    '''
    return re.sub('<[^<]+?>', '', string)
    
def getArtist(webTree):
    '''
    Function to get the artist name from html
    '''
    ArtistLoc = webTree.find_class('t_autor')
    ArtistStrList = [tostring(track, with_tail=False) for track in list(ArtistLoc[0].iter('a'))]
    Artist = removeTags(ArtistStrList[0])
    return Artist
    
def getTrack(webTree):
    '''
    Function to get the track name from html
    '''
    title = webTree.find_class('t_title')
    Tracklist = [tostring(track, with_tail = False) for track in list(title[0].iter('h1'))]
    Track = removeTags(Tracklist[0])
    return Track

def getChordsList(webTree):
    '''
    Function to get a list of chords from html
    '''
    tabContentClass = webTree.find_class('js-tab-content')
    try:
        chordsList = list(tabContentClass[0].iter('span')) # starts at element 0
        chords = [tostring(chord, with_tail = False).strip('</span>') for chord in chordsList]
    except IndexError:
        chords = []
    return chords
    
def getChordsArtistTrack(url):
    '''
    Function to get chords from a webpage in str format
    '''
    webPage = requests.get(url)
    webTree = html.fromstring(webPage.content)
    Artist = getArtist(webTree)
    Track = getTrack(webTree)
    Chords = getChordsList(webTree)    
    return Artist, Track, Chords 

def getGenreTree(genrekey, page):
    '''
    Function to get xml tree given the genre
    '''    
    if type(page) == int:
        page = str(page)
    theURL = 'https://www.ultimate-guitar.com/search.php?type[2]=300&type2[0]=40000&rating[4]=5' \
        + '\&tuning[standard]=standard&genres[0]=' + str(genrekey)+ '&page=' + page \
        + '&view_state=advanced&tab_type_group=text&app_name=ugt&order=myweight'
        
    pageBand = requests.get(theURL)
    return html.fromstring(pageBand.content)
    

def getChordProg(chordList, progLen = 4):
    '''
    Function to get the most common chord progression in a list
    '''
    progs4 = [''.join(chordList[i:i+progLen]) for i in range(len(chordList)-progLen)]
    try:
        chordProg = collections.Counter(progs4).most_common(1)[0][0]
    except IndexError: # If there are no chords
        chordProg = ''
    return chordProg
    
def getGenreDict():
    url = 'https://www.ultimate-guitar.com/advanced_search.html'
    pageUrl = requests.get(url)
    webTree = html.fromstring(pageUrl.content)
    Main = webTree.find_class('b')
    MainGenreList = list(Main[2].iter('optgroup'))
    GenreDict = {}
    for Genre in MainGenreList:
        GenreStr = tostring(Genre, with_tail = False)
        g1 = str.split(re.sub('&#13;\s+','\n',removeTags(GenreStr)),'\n')[1:-1]
        MainGenre = g1[0]
        GenreInd_complete = re.findall(r'\d+',GenreStr)
        if len(GenreInd_complete)>4:
            GenreInd = GenreInd_complete[2:-2:2]
        else:
            GenreInd = GenreInd_complete[2]
        subGenreDict = dict(zip(g1[1:], GenreInd[1:]))
        if bool(subGenreDict):
            GenreDict[MainGenre] = subGenreDict
        else:
            GenreDict[MainGenre] = dict([(MainGenre, GenreInd[0])])
    return GenreDict
# ============================================================================

conn = sqlite3.connect('chordProgdb2.sqlite')
cur = conn.cursor()
cur.executescript('''
/*
Uncomment out the bottom section is want to reset the tables
*/

/*
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS ChordProg;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Song;

CREATE TABLE Artist (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE ChordProg (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    prog   TEXT UNIQUE
);

CREATE TABLE Genre (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
    
);

CREATE TABLE Song (
    id  INTEGER NOT NULL PRIMARY KEY 
        AUTOINCREMENT UNIQUE,
    title TEXT,
    artist_id INTEGER,
    chordProg_id  INTEGER,
    genre_id INTEGER,
    subgenre_id INTEGER
);
*/
''')


allGenresDict = getGenreDict()
#to find all genres: allGenresDict.keys()
mainGenre = 'Country'
genresDict = allGenresDict[mainGenre]

cur.execute('''INSERT OR IGNORE INTO Genre (name) 
    VALUES ( ? )''', (mainGenre, ) )
cur.execute('SELECT id FROM Genre WHERE name = ? ', (mainGenre, ))
main_genre_id = cur.fetchone()[0]   

page = '1' # start at page 1, in str format as will be added to html str

for genre, genrekey in genresDict.iteritems():
    
    # = Get xml tree for first page
    tree1 = getGenreTree(genrekey, page)
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
        looptree = getGenreTree(genrekey, str(looppage))
        loopsongs = looptree.find_class('song result-link')
        for song in loopsongs:
            songLinks.append(song.get('href'))
    
    print('No of tabs: ' + str(len(songLinks)))
    
    cur.execute('''INSERT OR IGNORE INTO Genre (name) 
        VALUES ( ? )''', (genre, ) )
    cur.execute('SELECT id FROM Genre WHERE name = ? ', (genre, ))
    subgenre_id = cur.fetchone()[0]
         
    
    progLen = 4
    for i in songLinks:
        Artist, Song, Chords = getChordsArtistTrack(i)
        chordProg = getChordProg(Chords)
        
        cur.execute('''INSERT OR IGNORE INTO Artist (name) 
            VALUES ( ? )''', ( Artist, ) )
        cur.execute('SELECT id FROM Artist WHERE name = ? ', (Artist, ))
        artist_id = cur.fetchone()[0]    
        
        cur.execute('''INSERT OR IGNORE INTO ChordProg (prog) 
            VALUES ( ? )''', (chordProg, ) )
        cur.execute('SELECT id FROM ChordProg WHERE prog = ? ', (chordProg, ))
        chordProg_id = cur.fetchone()[0]
        
        cur.execute('''INSERT OR REPLACE INTO Song
            (title, artist_id, genre_id, subgenre_id, chordProg_id) 
            VALUES ( ?, ?, ?, ?, ? )''', 
            ( Song, artist_id, main_genre_id, subgenre_id, chordProg_id, ) )
        conn.commit()
    

