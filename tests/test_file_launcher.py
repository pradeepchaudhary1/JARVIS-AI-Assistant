"""
Test File & Folder Launcher
Phase 2.2 - Step 5.1
"""

from tools.file_launcher import FileLauncher


tests = [
    "desktop",
    "downloads",
    "documents",
    "pictures",
]


for item in tests:

    print()
    print(item)

    result = FileLauncher.open(item)

    print("path alias: desktop")
print(FileLauncher.open("desktop"))

print()

print("path alias: pictures")
print(FileLauncher.open("pictures"))

print()

print("path alias: videos")
print(FileLauncher.open("videos"))
