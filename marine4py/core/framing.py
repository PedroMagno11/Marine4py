from dataclasses import dataclass
from typing import Optional, Sequence

from marine4py.core.checksum import ChecksumStrategy, NoChecksum
from marine4py.core.error import ChecksumError, ParseError

"""
FramingStrategy: 
- Esta classe define como quebrar a string bruta em (talker, sentence_id, campos, checksum)
e como remontar isso de volta numa string.
"""

@dataclass
class RawSentence:
    talker: Optional[str]
    sentence_id: str
    fields: list


class FramingStrategy:
    def __init__(
        self,
        start: str = "$",
        field_sep: str = ",",
        checksum_sep: Optional[str] = "*",
        checksum_strategy: ChecksumStrategy = None,
        line_end: str = "\r\n",
        talker_len: int = 2,
    ):
        self.start = start
        self.field_sep = field_sep
        self.checksum_sep = checksum_sep
        self.checksum_strategy = checksum_strategy or NoChecksum()
        self.line_end = line_end
        self.talker_len = talker_len  # 0 = sem talker; cabecalho inteiro vira o sentence_id

    def split(self, raw: str) -> RawSentence:
        raw = raw.strip()
        if not raw.startswith(self.start):
            raise ParseError(f"sentenca nao comeca com {self.start!r}: {raw!r}")
        body = raw[len(self.start):]

        checksum = None
        if self.checksum_sep and self.checksum_sep in body:
            body, checksum = body.rsplit(self.checksum_sep, 1)

        if checksum is not None:
            if not self.checksum_strategy.verify(body, checksum):
                expected = self.checksum_strategy.compute(body)
                raise ChecksumError(
                    f"checksum invalido em {raw!r}: esperado {expected}, recebido {checksum}"
                )

        parts = body.split(self.field_sep)
        header, fields = parts[0], parts[1:]

        if self.talker_len:
            talker, sentence_id = header[: self.talker_len], header[self.talker_len:]
        else:
            talker, sentence_id = None, header

        return RawSentence(talker=talker or None, sentence_id=sentence_id, fields=fields)

    def join(self, talker: Optional[str], sentence_id: str, fields: Sequence[str]) -> str:
        header = f"{talker or ''}{sentence_id}"
        body = self.field_sep.join([header, *fields])
        out = f"{self.start}{body}"
        checksum = self.checksum_strategy.compute(body)
        if self.checksum_sep and checksum:
            out += f"{self.checksum_sep}{checksum}"
        return out + self.line_end
