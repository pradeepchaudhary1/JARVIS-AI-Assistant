from llm.client_groq import GroqClient


client = GroqClient()

reply = client.chat(

    [

        {

            "role": "user",

            "content": "Reply only with: JARVIS ONLINE"

        }

    ]

)

print(reply)