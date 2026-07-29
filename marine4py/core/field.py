from dataclasses import dataclass
from typing import Any, Callable, Optional, Tuple

from marine4py.core.error import FieldError

"""
Field: descreve um campo de uma sentenca -- nome legivel, atributo python,
como converter string->valor (parse) e valor->string (render).
"""
def _identity(x):
    return x


@dataclass
class Field:
    name: str
    attr: str
    parse: Callable[[str], Any] = _identity
    render: Callable[[Any], str] = lambda v: "" if v is None else str(v)
    required: bool = False
    default: Any = None
    choices: Optional[Tuple[Any, ...]] = None
    validate: Optional[Callable[[Any], bool]] = None

    def decode(self, raw: str):
        if raw == "":
            if self.required:
                raise FieldError(
                    f"campo obrigatorio '{self.name}' ({self.attr}) esta vazio ou ausente"
                )
            return self.default

        try:
            value = self.parse(raw)
        except FieldError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise FieldError(
                f"campo '{self.name}' ({self.attr}): valor invalido {raw!r}: {exc}"
            ) from exc

        if self.choices is not None and value not in self.choices:
            raise FieldError(
                f"campo '{self.name}' ({self.attr}): valor {value!r} fora do "
                f"conjunto permitido {self.choices}"
            )

        if self.validate is not None and not self.validate(value):
            raise FieldError(
                f"campo '{self.name}' ({self.attr}): valor {value!r} nao passou na validacao"
            )

        return value

    def encode(self, value) -> str:
        if value is None:
            return ""
        return self.render(value)


class StringField(Field):
    def __init__(self, name, attr, **kw):
        super().__init__(name, attr, parse=str, render=str, **kw)


class IntField(Field):
    def __init__(self, name, attr, **kw):
        super().__init__(name, attr, parse=int, render=str, **kw)


class FloatField(Field):
    def __init__(self, name, attr, **kw):
        super().__init__(name, attr, parse=float, render=repr, **kw)