from tools.path_searcher import PathSearcher


tests = [
    "Desktop",
    "Pictures",
    "Videos",
    "JARVIS-AI-Assistant",
]


for item in tests:

    result = PathSearcher.find(item)

    print()
    print(item)
    print("->", result)