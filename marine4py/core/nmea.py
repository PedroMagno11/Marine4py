from marine4py.core.error import NMEASentenceTypeError, ParseError, FieldError
from marine4py.core.registry import REGISTRY


class NMEASentenceMeta(type):
    def __new__(mcs, name, bases, ns):
        cls = super().__new__(mcs, name, bases, ns)
        dialect = ns.get("dialect") or getattr(cls, "dialect", None)
        sentence_id = ns.get("sentence_id")
        # so registra classes concretas (com sentence_id proprio declarado)
        if dialect and sentence_id:
            REGISTRY.register(dialect, sentence_id, cls)
        return cls


class NMEASentence(metaclass=NMEASentenceMeta):
    dialect: str = None
    sentence_id: str = None
    framing = None
    fields: tuple = ()

    def __init__(self, talker=None, sentence_id=None, data=(), raw=None):
        self.talker = talker
        self.sentence_id = sentence_id or self.sentence_id
        self.raw = raw  # string original, se disponivel -- so para contexto de erro
        self._raw_fields = list(data)
        self._decode()

    def _decode(self):
        for i, field in enumerate(self.fields):
            raw_val = self._raw_fields[i] if i < len(self._raw_fields) else ""
            try:
                value = field.decode(raw_val)
            except FieldError as exc:
                extra = f" | sentenca: {self.raw!r}" if self.raw else ""
                raise FieldError(
                    f"[{self.dialect}.{self.sentence_id}] campo #{i + 1} "
                    f"({field.attr}): {exc}{extra}"
                ) from exc
            setattr(self, field.attr, value)

    def render(self) -> str:
        raw_fields = [f.encode(getattr(self, f.attr, None)) for f in self.fields]
        return self.framing.join(self.talker, self.sentence_id, raw_fields)

    def __str__(self):
        return self.render()

    def __repr__(self):
        vals = ", ".join(f"{f.attr}={getattr(self, f.attr, None)!r}" for f in self.fields)
        return f"<{self.dialect}.{self.sentence_id} {vals}>"

    @classmethod
    def parse(cls, raw: str, dialect: str = None):
        dialect = dialect or cls.dialect
        if not dialect:
            raise ParseError("dialeto nao informado nem definido na classe")
        framing = REGISTRY.get_framing(dialect)
        parsed = framing.split(raw)
        target = REGISTRY.get_class(dialect, parsed.sentence_id)
        if target is None:
            known = ", ".join(sorted(REGISTRY.sentence_ids(dialect))) or "(nenhuma registrada)"
            raise NMEASentenceTypeError(
                f"sentenca '{parsed.sentence_id}' nao registrada no dialeto '{dialect}'. "
                f"Sentencas conhecidas nesse dialeto: {known}"
            )
        return target(
            talker=parsed.talker,
            sentence_id=parsed.sentence_id,
            data=parsed.fields,
            raw=raw,
        )


def parse(raw: str, dialect: str):
    """Atalho funcional, equivalente a NMEASentence.parse(raw, dialect=dialect)."""
    return NMEASentence.parse(raw, dialect=dialect)
