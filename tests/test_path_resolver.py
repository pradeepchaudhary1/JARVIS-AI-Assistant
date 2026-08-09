from tools.path_resolver import PathResolver


tests = [
    "desktop",
    "pictures",
    "videos",
    "downloads",
    "documents",
    "music",
]


for item in tests:

    print()
    print(item)

    result = PathResolver.resolve(item)

    if result:

        print("->", result)

    else:

        print("-> NOT FOUND")