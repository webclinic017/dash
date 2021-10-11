from man import db
from datetime import datetime
from man import Item
from man import Ud

import oopdatafeed

t = oopdatafeed.Manage()
d = t.toshow()

d_eng = t.toshow_eng()

mini = ['M2', 'M5', 'M15', 'H1', 'H4']
for i in mini:
    for j in range(len(d)):
        if d[i][j] == 'O' and d[mini[mini.index(i)+1]][j] == 'D':
           d[i][j] = 'X'
        if d[i][j] == 'Or' and d[mini[mini.index(i)+1]][j] == 'U':
           d[i][j] = 'Xr'


t.to_db(d, d_eng)

print(d)
print(d_eng)
while True:
    t.update(d, d_eng)