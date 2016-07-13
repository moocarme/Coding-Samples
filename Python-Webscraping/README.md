# Why Does All Country Music Sound the Same?

### Hypothesis
The motivation of this project is to try to understand why all country music sounds the same. I hypothesize that all country music sounds the same becasue many songs all use the same chord progession, whereas many other genres of music have a greater variation in the chord 
progressions used.
A chord progression is the different chords used in songs, as well as the order in which they are used. For example Pearl Jam's 'Elderly woman...' uses a chord progression D C G G for the much of the verse and chorus.
Both the notes used and their respective order is needed. The assumption that the guitar plays the characteristic 'sound' of the song and can be infered from the data gained from what the guitar plays.

### Files
This project contains files that grabs tabluture from the internet, specifically '[ultimate-guitar.com](ultimate-guitar.com)' and reads them. 

- **getChords.py** - webscraper that gets the chords script retrives the chords and passes them to a SQL relational database with tables for the song, artist, genre and chord progression. Only 5 star rated tablatures are used in standard tuning. 
- **accessSQLdatabase.py** - database access example used to generate data for the figures.
- **lyricScraper.py** - webscraper that gets the country music lyrics from the website [anycountrymusiclyrics.com](anycountrymusiclyrics.com) using the beautifulSoup package, and save in pickle file.
- **lyricsAnalysis.py** - remove stopwords, using natural language toolkit, sort and plot most common words.

### Usage
To run use the getChords.py that generates the database, scraping through all tabs of all sub genres of a given genre.

### Discussion
One issue I came across was that ultimate-guitar.com only allows 500 search results, yet there are over 5,000 5-star rated chord tabs for some of sub genres, separating by artist may lead to a greater number of tabs to be processed and so trends may become clearer.

Next it would insightful to look up find out why these same top 3, and top 8 chords are being used, as there may be an underlying trend I am unaware of. 
This could be done with statistical analysis which would be the topic of further work. Also other features of the songs could be analysed separately using the echonest API, alternatively I could develop my own feature analyses using machine learning methods.

### getChords.py Data Dictionary

- *allGenresDict* - dictionary containing all the genres (dict)
- *mainGenre* - particular genre to add to database (str)
- *genresDict* - dictionary containg all subgenres of a particular genre (dict)
- *cur* - SQL cursor (sqlite object)
- *conn* - SQL connection (sqlite object)
- *main_genre_id* - id of main genre in the genre table (int)
- *sub_genre_id* - id of sub genre in the genre table (int)
- *page* - page to start scraping (int)
- *maxpage* - max pages to scrape of the sub genre (int)
- *songs* - list of song links on the page (list)
- *songLinks* - cleaned up list of song links (list)
- *looppage* - current page scraping (int)
- *looptree* - the webtree of current webpage url being scraped (lxml object)
- *loopsongs* - list of songs from the current webpae being scraped
- *webpage* - the url of the webpage being scraped (requests object)
- *tree1* - the webtree of webpage url (lxml object)
- *progLen* - length of chord progression (int)
- *Song* - Name of song from webpage (str)
- *Artist* - Name of artist from webpage (str)
- *Chords* - list of chords scraped from the web page (list)
- *chordProg* - chord progression from the list of chords (str)
- *tabXpath* - xml path to the content of the webpage containing the guitar tablature (str)
- *tab* - the content that contains the guita tablature (str)
- *tabContentClass* - iterable that contains all the 'js-tab-content' content (lxml object)
- *chordsList* - list of all chords in the webpage
