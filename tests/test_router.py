from llm.router import LLMRouter

router = LLMRouter()

reply = router.ask(

    [

        {

            "role": "user",

            "content": "Reply only with: ROUTER WORKING"

        }

    ]

)

print(reply)