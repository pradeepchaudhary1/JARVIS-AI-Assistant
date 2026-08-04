from brain.router import Router
from brain.dispatcher import Dispatcher

router = Router()
dispatcher = Dispatcher()

commands = [

    "open chrome",

    "open telegram",

    "open instagram",

    "open facebook",

    "open razorpay",

    "open chatgpt",

    "open lumix branding"

]

for cmd in commands:

    route = router.route(cmd)

    result = dispatcher.dispatch(route, cmd)

    print()

    print(cmd)

    print(route)

    print(result)