from brain.dispatcher import Dispatcher

dispatcher = Dispatcher()

tests = [

    "minimize chrome",

    "restore chrome",

    "maximize chrome",

]

for t in tests:

    print()
    print(t)
    print(dispatcher.dispatch("launcher", t))