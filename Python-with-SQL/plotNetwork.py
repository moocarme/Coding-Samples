# -*- coding: utf-8 -*-
"""
Created on Sun May 15 19:40:36 2016

@author: matt-666
"""

import sqlite3
from lxml import html
import requests
import networkx as nx
from pylab import savefig


def lookup(htmlTree, key):
    '''
    Helper function to find link of given key in the html tree
    '''
    found = False          # want to find the tag after the key
    for child in htmlTree.iter(): # iterate through html tree
        if not found:      # keep iterating until found is True
            try:
                if child.tag == 'a' and (key in child.text): # a finds the links
                    found = True
            except: continue
        else: # when found is True
            if child.tag == 'a': # make sure it is a link
                found = False
                return child


class network_graph(object):
    
    def __init__(self, startpage, pages, database):
        self.graph = nx.Graph() # Initialize graph
        self.startpage = startpage # start index of database
        self.pages = pages # How many links
        self.conn = sqlite3.connect(database)
        self.cur = self.conn.cursor()

    def reset_db_tables(self):
        '''
        Reset database tables
        '''
        ans = raw_input("Are you sure you want to reset tables, y/n?\n")
        if ans in ['y', 'yes', 'Y', 'Yes', 'YES']:
            self.cur.executescript('''
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
            );
            ''')
            self.conn.commit()
        else:
            print 'Not resetting tables'
        
    def create_network(self):
        '''
        Creates graph by iterating through links and adding edges and nodes
        '''
        for i in range(self.pages): # iterate through links
            self.cur.execute('SELECT link FROM Links WHERE id = ? ', (self.startpage + i, ))
            try:
                url = 'https://en.wikipedia.org' + self.cur.fetchone()[0] # database only contains latter part of link
                page = requests.get(url)             # go to URL
                tree = html.fromstring(page.content) # get html tree
                catLink = lookup(tree, 'Categories')      # look for link after 'categories'
                newtree = tree
                categories = ['first'] # initialise category list
                
                # while loop to find where catergory list should end
                while catLink.text != None and ('categor' not in categories[-1]) and (categories[-1] not in categories[:-2]):
                    catLink = lookup(newtree, 'Categories')
                    categories.append(catLink.text)    
                    newurl = 'https://en.wikipedia.org' + catLink.get('href')
                    if categories[-2] != 'first':
                        self.graph.add_edge(categories[-1], categories[-2]) # add to graph if not the first in the list
                    newpage = requests.get(newurl)
                    newtree = html.fromstring(newpage.content)
                
                # update database
                if len(categories) >= 2:
                    self.cur.execute('''INSERT OR IGNORE INTO Category (topic) 
                            VALUES ( ? )''', ( categories[-2], ) )
                    self.cur.execute('SELECT id FROM Category WHERE topic = ? ', (categories[-2], ))
                    category_id = self.cur.fetchone()[0]
                else:
                    category_id = 'Null'
                self.cur.execute('''UPDATE Links SET topic = ?
                         WHERE id = ?''', (category_id, self.startpage + i) )
            except: continue
        self.conn.commit() # commit to database
    
    def plot_graph(self, node_size = 100, node_color = 'b', edge_width = 1, 
                   font_size = 8, font_color = 'r', filename = None):
        '''
        Plots the network
        '''
        pos = nx.spring_layout(self.graph)
        nx.draw_networkx_nodes(self.graph, pos, node_size = node_size, 
                               node_color = node_color)
        nx.draw_networkx_edges(self.graph, pos, width = edge_width)
        nx.draw_networkx_labels(self.graph, pos, font_size = font_size, 
                                font_family='sans-serif',font_color = font_color)
        if filename:
            savefig("wikiNetwork.eps")
            
    def close_connections(self):
        '''
        Close database connections
        '''
        self.cur.close()
        self.conn.close()

if __name__ == '__main__':
    database = 'wikiLinks-test.sqlite'
    ng = network_graph(startpage = 40, pages = 60, database=database)
    ng.create_network()
