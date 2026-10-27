import os
import sys
from pathlib import Path

# Tests run in mock mode: no GPU, no checkpoints needed.
os.environ["CLOAK_MOCK"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
