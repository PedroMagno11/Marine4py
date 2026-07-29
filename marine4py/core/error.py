class NmeaLibError(Exception):
    """Erro base da biblioteca."""


class ParseError(NmeaLibError):
    """Erro genérico ao interpretar uma sentença."""


class ChecksumError(ParseError):
    """Checksum informado não confere com o calculado."""


class NMEASentenceTypeError(ParseError):
    """Sentença bem formada, mas tipo/dialeto desconhecido pelo registro."""


class FieldError(ParseError):
    """Erro ao converter/validar um campo específico."""
