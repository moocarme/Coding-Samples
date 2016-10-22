# -*- coding: utf-8 -*-
"""
Created on Sun May 15 19:40:36 2016

Grabs all the links from a wikipedia page and adds it to at sqlite database

@author: matt-666
"""

import sqlite3
from lxml import html
import requests


class wikipedia_scraper(object):
    
    def __init__(self, init_url, pages, database):
        self.init_url = init_url
        self.pages = pages
        self.conn = sqlite3.connect(database)
        self.cur = self.conn.cursor()
    
    def reset_db_tables(self):
        '''
        Resets tables of database
        '''
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
        
    def get_urls(url_tree, parent_id, cur):
        '''
        Helper function to grab all links from the url tree and insert into database
        '''
        for child in url_tree.iter():
            try:
                if child.tag == 'a':
                  # print(child.get('href'))
                   cur.execute('''INSERT OR IGNORE INTO Links (link, parent) 
                       VALUES ( ?, ? )''', ( child.get('href'), parent_id) )
            except: continue
        return None

    def scrape(self):
        '''
        scrape webpages
        '''
        self.cur.execute('SELECT COUNT(link) FROM Links')
        init = int(round(self.cur.fetchone()[0] / 100.)) # start from database length/100 so we dont repeat
        for i in range(self.pages):
            # grab id from inital link
            self.cur.execute('SELECT link FROM Links WHERE id = ? ', (init + i, ))
            try: url = self.cur.fetchone()[0]
            except: url = None
            if i%100 == 0: print "%i pages scraped" % (i)
            if url:
                self.cur.execute('SELECT id FROM Links WHERE link = ? ', (self.init_url, ))
                parenturl_id = self.cur.fetchone()[0]
                try:
                    page = requests.get('https://en.wikipedia.org' + url)
                    tree = html.fromstring(page.content)
                    # all the links in the main content in the class 'mw-content-ltr'
                    tree_body = tree.find_class('mw-content-ltr') 
                    tree_body=tree_body[0] # in list type for some reason
                    self.get_urls(tree_body, parenturl_id, self.cur) # grab the urls from the tree
                except: continue
        self.conn.commit()
    
    def close_connections(self):
        '''
        Close connections to database
        '''
        self.cur.close()
        self.conn.close()

if __name__ == "__main__":
    pages = 200 # get all links from this number of pages
    # Initialise at the main page since it changes everyday
    init_url = 'https://en.wikipedia.org/wiki/Main_Page'
    
    scraper = wikipedia_scraper(init_url, pages, 'wikiLinks-test.sqlite')
    scraper.scrape()
    scraper.close_connections()
