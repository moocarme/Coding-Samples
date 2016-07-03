# Looking at Data-Mined Guitar Tablature to Investigate Why All Country Music Sounds Similar 

### Hypothesis
The motivation of this project is to try to understand why all country music sounds the same. I hypothesize that all country music sounds the same becasue many songs all use the same chord progession, whereas many other genres of music have a greater variation in the chord 
progressions used.
A chord progression is the different chords used in songs, as well as the order in which they are used. For example Pearl Jam's 'Elderly woman...' uses a chord progression D C G G for the much of the verse and chorus.
Both the notes used and their respective order is needed. The assumption that the guitar plays the characteristic 'sound' of the song and can be infered from the data gained from what the guitar plays.

### Files
This project contains files that grabs tabluture from the internet, specifically '[ultimate-guitar.com](ultimate-guitar.com)' and reads them. 
The 'getChordsandPlot.py' script retrives the chords that users of the site have entered. Only 5 star rated tablatures are used in standard tuning. 
Mining them for data on the various notes played in songs, the end goal would be analyse different genres of music to show that country music shows less variation in the chords and chord progressions used compared to other genres of Music

### Usage
To run use the getChordsandPlot.py that sums up chord progressions used in country music.
The output is  2 bar charts, the first shows the count of chord progressions, the second shows the usage of various chords.

We find that Chords involving variations of G, C, and D are very popular in country music and those three chords account for about 45% of the total chords, if we look at the top 8 chords (G, C, D, A, F, Am, Em, E) they account for almost 75%. For context there are over 800 various chord combinations (see: [here](https://tabs.ultimate-guitar.com/m/misc/all_the_chords_crd.htm)). So we can see how these 8 chords and their various combinations can lead to music that may sound similar.

Compared to other genres such as Jazz, which incidentally has the same top 3 chords, in the same order, G-C-D yet only accounts for 37% of total chord usage. If we look to the top 8 chords, which again are the same chords, yet in a different order they account for 62% of all chords used.

### Discussion
One Issue I cam across was that ultimate-guitar.com only allows 500 search results, yet there are over 20,000 5-star rated chord tabs for some of the genres, separating by sub genre, or even by artist may lead to a greater number of tabs to be processed and so trends may become clearer.

Next it would insightful to look up find out why these same top 3, and top 8 chords are being used, as there may be an underlying trend I am unaware of. Also worth invetigating is whether the use of chords outside the top 8 are key in varying the characteristic sound that might explain why all country music sounds similar.
This could be done with statistical analysis which would be the topic of further work. Also other features of the songs could be analysed separately using the echonest API, alternatively I could develop my own feature analyses using machine learning methods.
