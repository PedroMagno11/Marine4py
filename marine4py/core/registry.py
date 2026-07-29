from collections import defaultdict
from typing import Dict, Optional

from marine4py.core.error import NMEASentenceTypeError


class NmeaSentenceRegistry:
    def __init__(self):
        self._framings: Dict[str, object] = {}
        self._classes: Dict[str, Dict[str, type]] = defaultdict(dict)

    def set_framing(self, dialect: str, framing) -> None:
        self._framings[dialect] = framing

    def get_framing(self, dialect: str):
        try:
            return self._framings[dialect]
        except KeyError:
            raise NMEASentenceTypeError(f"dialeto desconhecido: {dialect!r}") from None

    def register(self, dialect: str, sentence_id: str, cls: type) -> None:
        self._classes[dialect][sentence_id] = cls

    def get_class(self, dialect: str, sentence_id: str) -> Optional[type]:
        return self._classes.get(dialect, {}).get(sentence_id)

    def dialects(self):
        return list(self._framings.keys())

    def sentence_ids(self, dialect: str):
        return list(self._classes.get(dialect, {}).keys())


REGISTRY = NmeaSentenceRegistry()