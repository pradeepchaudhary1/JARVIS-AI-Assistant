import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from brain.orchestrator import Brain

brain = Brain()

print(brain.process("open youtube"))