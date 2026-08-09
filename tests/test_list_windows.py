import pygetwindow as gw

print("=" * 50)
print("Open Windows")
print("=" * 50)

for title in gw.getAllTitles():
    if title.strip():
        print(title)