# -*- coding: utf-8 -*-
"""
Spyder Editor

Created on July 10th
"""

import sqlite3
conn = sqlite3.connect('chordProgdb2.sqlite')
cur = conn.cursor()

cur.execute('''
SELECT chord.prog, COUNT(*)
FROM Song AS master
LEFT JOIN Genre AS subgenre_tbl ON subgenre_tbl.id = master.subgenre_id
LEFT JOIN Genre ON genre.id = master.genre_id
LEFT JOIN ChordProg AS chord ON chord.id = master.chordProg_id
WHERE subgenre_tbl.name = 'Americana'
GROUP BY chord.prog
ORDER BY COUNT(*) DESC
LIMIT 11
;
''')

top10Americana= cur.fetchall()
conn.commit
print(top10Americana)