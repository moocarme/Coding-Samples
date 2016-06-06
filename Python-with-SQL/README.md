# Using Python and SQL to Map Wikipedia by Page Category 

Creating a map of the how the categories are connected in wikipedia.

getWikiLinks.py is a python script that iterates through the links on a wikipedia page and stores them in a sqlite database. 
Once it has stored all the links in a given page, it moves to the next page in the database. 
Obviously this can go on ad infinitum so the pages are limited (to say 60) at a time, so we don't anger the ISP. 
The ultimate goal would be a databse of all the links in wikipedia.

Next, the categories of the links are plotted in a network in plotNetwork.py. 
This script goes through a given amount of the wikipedia links from the sqlite database and returns their category. 
The script also goes to the link associated with the category and continues, i.e. 'electromagnetism -> subfields of physics -> physics -> physical sciences -> natural sciences -> nature ...'

The resulting network is then plotted and saved to a png.
