from abc import ABC, abstractmethod
from functools import reduce
import operator

class ChecksumStrategy(ABC):
    @abstractmethod
    def compute(self, body: str) -> str:
        """Retorna o checksum no formato de string para o corpo dado."""

    def verify(self, body: str, checksum: str) -> bool:
        return self.compute(body).upper() == checksum.upper()
    
    
class NoChecksum(ChecksumStrategy):
    """Dialetos sem checksum: compute() sempre retorna string vazia e tudo valida."""

    def compute(self, body: str) -> str:
        return ""

    def verify(self, body: str, checksum: str) -> bool:
        return True


class XorChecksum(ChecksumStrategy):
    """Checksum padrao do NMEA-0183: XOR de todos os bytes do corpo, hexa maiusculo de 2 digitos."""

    def compute(self, body: str) -> str:
        value = reduce(operator.xor, (ord(c) for c in body), 0)
        return f"{value:02X}"


class Crc16Checksum(ChecksumStrategy):
    """CRC-16/CCITT-FALSE. Exemplo de estrategia alternativa para dialetos proprios."""

    poly = 0x1021
    init = 0xFFFF

    def compute(self, body: str) -> str:
        crc = self.init
        for byte in body.encode("ascii"):
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ self.poly) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
        return f"{crc:04X}"
