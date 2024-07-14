import json
from pathlib import Path

def loadLottieAnimationFile(filepath: str = None) -> str:
    if filepath != None and Path(filepath).is_file():
        with open(filepath, "r") as f:
            return json.load(f)
    return None