"""
JARVIS Voice Pipeline
Production Version
"""

from voice.listener import VoiceListener
from brain.orchestrator import Brain


class VoicePipeline:

    def __init__(self):

        self.listener = VoiceListener()
        self.brain = Brain()

    def run(self):

        result = self.listener.listen()

        if result["status"] != "success":

            return result

        return self.brain.process(result["text"])