"""
SentenceStream: leitor incremental de sentencas.
"""
from typing import Callable, Iterable, List, Optional, Union
from .error import NMEASentenceTypeError, ParseError
from .registry import REGISTRY


class NMEASentenceStream:
    def __init__(
        self,
        dialects: Union[str, Iterable[str]],
        on_error: Union[str, Callable[[str, List[Exception]], None]] = "raise",
    ):
        """
        dialects:  nome de um dialeto, ou lista de dialetos a tentar por
                   linha (util quando a fonte mistura formatos, ex:
                   ["nmea0183", "nmea0183_proprietary", "ais"]).
        on_error:  o que fazer quando uma linha nao e reconhecida por
                   nenhum dos dialetos configurados:
                     "raise"    -- levanta a excecao (padrao)
                     "skip"     -- ignora a linha silenciosamente
                     callable(line, errors) -- chamado para log/tratamento
                                    customizado; a linha e descartada
        """
        self._dialects = [dialects] if isinstance(dialects, str) else list(dialects)
        if not self._dialects:
            raise ValueError("SentenceStream precisa de ao menos um dialeto")
        self._on_error = on_error
        self._buffer = ""

    def feed(self, chunk: str) -> List[object]:
        """
        Alimenta um pedaco novo de texto (pode ser bytes decodificados
        de um socket, uma leitura parcial de arquivo, etc). Retorna a
        lista de sentencas COMPLETAS reconhecidas nesse pedaco -- uma
        linha ainda incompleta fica bufferizada para a proxima chamada.
        """
        self._buffer += chunk
        *complete_lines, self._buffer = self._buffer.split("\n")

        results = []
        for raw_line in complete_lines:
            sentence = self._parse_line(raw_line)
            if sentence is not None:
                results.append(sentence)
        return results

    def flush(self) -> Optional[object]:
        """
        Tenta interpretar o que sobrou no buffer como uma linha final
        (util quando a fonte termina sem quebra de linha no final).
        Limpa o buffer independente do resultado.
        """
        line, self._buffer = self._buffer, ""
        if not line.strip():
            return None
        return self._parse_line(line)

    def _parse_line(self, raw_line: str) -> Optional[object]:
        line = raw_line.strip("\r\n \t")
        if not line:
            return None

        candidates = self._select_dialects(line)
        errors: List[Exception] = []
        for dialect in candidates:
            try:
                return _parse(line, dialect)
            except ParseError as exc:
                errors.append(exc)

        return self._handle_error(line, errors)

    def _select_dialects(self, line: str) -> List[str]:
        if len(self._dialects) == 1:
            return self._dialects

        first_char = line[:1]
        matches = [
            d for d in self._dialects
            if REGISTRY.get_framing(d).start == first_char
        ]
        # se nenhum dialeto declarou esse caractere inicial, tenta todos
        # mesmo assim -- e mais seguro que descartar a linha de cara.
        return matches or self._dialects

    def _handle_error(self, line: str, errors: List[Exception]):
        if self._on_error == "skip":
            return None
        if callable(self._on_error):
            self._on_error(line, errors)
            return None
        # "raise" (padrao)
        if errors:
            raise errors[-1]
        raise NMEASentenceTypeError(f"linha nao reconhecida por nenhum dialeto: {line!r}")


def _parse(line: str, dialect: str):
    from marine4py.core.nmea import NMEASentence
    return NMEASentence.parse(line, dialect=dialect)
