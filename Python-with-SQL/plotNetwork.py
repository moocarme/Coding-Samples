# -*- coding: utf-8 -*-
"""
Created on Sun May 15 19:40:36 2016

@author: matt-666
"""

import sqlite3
from lxml import html
import requests
import networkx as nx
from pylab import *

# connect to sql database

conn = sqlite3.connect('wikiLinks.sqlite')
cur = conn.cursor()

cur.executescript('''
/*
Uncomment out the bottom section is want to reset the tables
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


# Helper function to find link of given key in the html tree
def lookup(d, key):
    found = False          # want to find the tag after the key
    for child in d.iter(): # iterate through html tree
        if not found:      # keep iterating unitl found is True
            try:
                if child.tag == 'a' and (key in child.text): # a finds the links
#                    print(child.text)   
                    found = True
            except: continue
        else: # when found is True
            if child.tag == 'a': # make sure it is a link
#                print(child.text, child.attrib)
                found = False
                return child


G = nx.Graph() # Initialize graph

startpage = 40 # start index of database
testpages = 60 # How many links

for i in range(testpages): # iterate through links
    cur.execute('SELECT link FROM Links WHERE id = ? ', (startpage + i, ))
    try:
        url = 'https://en.wikipedia.org' + cur.fetchone()[0] # database only contains latter part of link
        page = requests.get(url)             # go to URL
        tree = html.fromstring(page.content) # get html tree
        t1 = lookup(tree, 'Categories')      # look for link after 'categories'
        newtree = tree
        categories = ['first'] # initialise category list
        
        # while loop to find where catergory list should end
        while t1.text != None and 'categor' not in categories[-1] and categories[-1] not in categories[:-2]:
            t1 = lookup(newtree, 'Categories')
            categories.append(t1.text)    
            newurl = 'https://en.wikipedia.org' + t1.get('href')
            if categories[-2] != 'first':
                G.add_edge(categories[-1], categories[-2]) # add to graph if not the first in the list
        #    print(t1.text)
            newpage = requests.get(newurl)
            newtree = html.fromstring(newpage.content)
#        print(categories)
        
        # update database
        if len(categories) >= 2:
            cur.execute('''INSERT OR IGNORE INTO Category (topic) 
                    VALUES ( ? )''', ( categories[-2], ) )
            cur.execute('SELECT id FROM Category WHERE topic = ? ', (categories[-2], ))
            category_id = cur.fetchone()[0]
        else:
            category_id = 'Null'
        cur.execute('''UPDATE Links SET topic = ?
                 WHERE id = ?''', (category_id, startpage + i) )
    except: continue
conn.commit() # commit to database

# plot network plot
pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G,pos,node_size=100,node_color='b')
nx.draw_networkx_edges(G,pos,width=1)
nx.draw_networkx_labels(G,pos,font_size=8,font_family='sans-serif',font_color='r')
savefig("wikiNetwork.png") 
show()