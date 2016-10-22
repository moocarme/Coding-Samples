# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 16:49:11 2016

@author: matt-666
"""

import matplotlib.pyplot as plt
from collections import Counter
from nltk.corpus import stopwords
import random
import pickle
import numpy as np

# = Helper Functions =========================================================

def WeightedPick(d):
    '''
    Chooses next word dependent on the number of occurences, such that more 
    frequent words will get chose more often
    '''
    r = random.uniform(0, sum(d.values()))
    s = 0.0
    for k, w in d.iteritems():
        s += w
        if r < s: return k
    return k

# =============================================================================

class lyric_analysis(object):
    
    def __init__(self, lyrics):
        self.lyrics = lyrics
        
    def create_dict(self):
        '''
        Compress into onle long list    
        '''
        flatSongLyrics = [item for sublist in self.lyrics for item in sublist]

        flatSongLyrics_noStopwords = [word for word in flatSongLyrics if word not in (stopwords.words('english'))]

        # = the word 'chorus' remains, so we remove
        flatSongLyrics_noStopwords[:]  = [x for x in flatSongLyrics_noStopwords if x != 'chorus']

        #Count all instances of words that are not stop words
        wordCount = Counter(flatSongLyrics_noStopwords)

        # = sort dictionary by value
        self.sortedKeys, self.sortedVals = [], []
        for key, value in sorted(wordCount.iteritems(), key=lambda (k,v): (v,k)):
            self.sortedKeys.append(key.title())
            self.sortedVals.append(value)
        # = have to reverse since the sort is in ascending order
        self.sortedKeys.reverse(); self.sortedVals.reverse()
        return None

    def plot_word_freq(self, resolution = 40):
        '''
        Plot sorted word frequencies
        '''        
        plt.figure()
        plt.bar(range(resolution), np.asarray(self.sortedVals[:resolution])/float(sum(self.sortedVals))*100., align='center')
        plt.xticks(range(resolution), self.sortedKeys[:resolution], rotation = 60)
        plt.xlabel('Lyric'); plt.ylabel('Count (%)')
        return None
        
    def plot_cumulative_distribution(self):
        '''
        Plot cumulative distribution 
        '''
        plt.figure()
        plt.plot(np.cumsum(self.sortedVals)/float(sum(self.sortedVals)))
        plt.xlabel('Number of words'); plt.ylabel('Cumulative distribution function')
        return None
        
    def lyric_model(self):
        '''
        Create dictionary of dictionary to see what words come are likely to 
        come after each one
        '''
        self.lyricDict= {}
        for song in self.lyrics:
            for word in range(len(song)-1):
                try:
                    self.lyricDict.setdefault(song[word], {})[song[word+1]] += 1
                except KeyError: # if key doesnt exist
                    self.lyricDict.setdefault(song[word], {})[song[word+1]] = 1
        return None

    def create_chorus(self, mydict, chorus_len, lyric_len):
        '''
        Creates string object of a typical verse or chorus dependent on the number 
        of words in a line, and number of lines in a verse/chorus given the 
        dictionary of possible words and the possible following words, with their
        ocuurences
        '''
        robo_lyric = [random.choice(mydict.keys())] # initiliaxe with random word
        for j in range(chorus_len):
            for i in range(lyric_len):
                robo_lyric.append(WeightedPick(self.lyricDict[robo_lyric[-1]]))
        
        for i in range(chorus_len):
            robo_lyric.insert((i+1)*lyric_len+i,'\n')  
        return(' '.join(robo_lyric))

    def generate_lyrics(self, lyric_len = 10, chorus_len = 4, seed = 666):
        '''
        Generate lyrics
        '''
        random.seed(seed)
        chorus = self.create_chorus(self.lyricDict, chorus_len, lyric_len)
        verse1 = self.create_chorus(self.lyricDict, chorus_len, lyric_len)
        verse2 = self.create_chorus(self.lyricDict, chorus_len, lyric_len)
        mySong = verse1 + '\n\r\n' + chorus + '\n\r\n' + verse2 + '\n\r\n' + chorus 
        return mySong
        
# ==============================================================================
        
if __name__=="__main__":
    # = grab from pickle file
    songLyrics = pickle.load(open("songLyrics.p", "rb"))
    analysis = lyric_analysis(songLyrics) # initialise
    analysis.create_dict()                # create dictionary of words removing stop words
    analysis.plot_word_freq(resolution = 40) # plot most frequent words
    analysis.plot_cumulative_distribution()  # plot cumulative distribution
    analysis.lyric_model()                   # create dictionary of lyrics and following words
    analysis.generate_lyrics(lyric_len = 10, chorus_len = 4) # make a song
