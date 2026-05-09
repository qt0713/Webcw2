import json
import re
from dataclasses import dataclass, field
from typing import Dict, List

WORD_RE = re.compile(r"[A-Za-z0-9']+")


@dataclass
class InvertedIndex:
    data: Dict[str, Dict[str, Dict[str, List[int] | int]]] = field(default_factory=dict)

    def add_document(self, url: str, text: str) -> None:
        tokens = tokenize(text)
        for position, token in enumerate(tokens):
            entry = self.data.setdefault(token, {}).setdefault(url, {"count": 0, "positions": []})
            entry["count"] += 1
            entry["positions"].append(position)

    def to_dict(self) -> Dict[str, Dict[str, Dict[str, List[int] | int]]]:
        return self.data

    @classmethod
    def from_dict(cls, raw: Dict[str, Dict[str, Dict[str, List[int] | int]]]) -> "InvertedIndex":
        return cls(data=raw)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=2, sort_keys=True)

    @classmethod
    def load(cls, path: str) -> "InvertedIndex":
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return cls.from_dict(data)


def tokenize(text: str) -> List[str]:
    return [match.group(0).lower() for match in WORD_RE.finditer(text)]
