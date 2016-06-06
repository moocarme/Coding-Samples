# -*- coding: utf-8 -*-
"""
Created on Sun May 15 19:40:36 2016

Grabs all the links from a wikipedia page and adds it to at sqlite database

@author: matt-666
"""

import sqlite3
from lxml import html
import requests

# Open connection
conn = sqlite3.connect('wikiLinks.sqlite')
cur = conn.cursor()

cur.executescript('''
/*
Uncomment below to reset tables
*/

/*
DROP TABLE IF EXISTS Links;
DROP TABLE IF EXISTS Category;

CREATE TABLE Links (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    link    TEXT UNIQUE,
    parent INTEGER,
    topic INTEGER
);

CREATE TABLE Category (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    topic TEXT UNIQUE

)
*/
''')

# Helper function to grab all links from the url tree and insert into database
def get_urls(url_tree, parent_id):
    for child in url_tree.iter():
        try:
            if child.tag == 'a':
#               print(child.get('href'))
               cur.execute('''INSERT OR IGNORE INTO Links (link, parent) 
                   VALUES ( ?, ? )''', ( child.get('href'), parent_id) )
        except: continue
    return None

# Initialise at the main page since it changes everyday
init_url = 'https://en.wikipedia.org/wiki/Main_Page'

pages = 20 # get all links from this number of pages

cur.execute('SELECT COUNT(link) FROM Links ')
init = int(round(cur.fetchone()[0] / 100.)) # start from database length/100 so we dont repeat


# Iterate through pages and grab links from those pages
for i in range(pages):
    # grab id from inital link
    cur.execute('SELECT link FROM Links WHERE id = ? ', (init + i, ))
    try: url = cur.fetchone()[0]
    except: url = None
    
    if url:
        cur.execute('SELECT id FROM Links WHERE link = ? ', (init_url, ))
        parenturl_id = cur.fetchone()[0]
        try:
            page = requests.get('https://en.wikipedia.org' + url)
            tree = html.fromstring(page.content)
            # all the links in the main content in the class 'mw-content-ltr'
            tree_body = tree.find_class('mw-content-ltr') 
            tree_body=tree_body[0] # in list type for some reason
            t1 = get_urls(tree_body, parenturl_id) # grab the urls from the tree
        except: continue
conn.commit()

