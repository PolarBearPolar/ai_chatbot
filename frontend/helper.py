import json
from pathlib import Path

def loadLottieAnimationFile(filepath: str = None) -> str:
    if filepath != None and Path(filepath).is_file():
        with open(filepath, "r") as f:
            return json.load(f)
    return None

def getKeyIndex(dictionary: dict = {}, lkpKey: str = None) -> int:
    index = 0
    for i, key in enumerate(dictionary.keys()):
        if key == lkpKey:
            index = i
    return index