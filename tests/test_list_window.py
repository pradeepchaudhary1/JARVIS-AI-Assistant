import pygetwindow as gw

for w in gw.getAllTitles():
    if w.strip():
        print(w)