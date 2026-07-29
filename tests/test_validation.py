import pytest

from marine4py.core.error import FieldError
from marine4py.core.field import IntField, StringField
from marine4py.core.nmea import NMEASentence


def test_required_field_missing_raises_field_error():
    # RMC.status agora e required=True -- sentenca com esse campo vazio
    # deve falhar de forma explicita, em vez de silenciosamente virar None.
    raw = "$GPRMC,225446,,4916.45,N,12311.12,W,000.5,054.7,191194,020.3,E*29"
    with pytest.raises(FieldError) as exc_info:
        NMEASentence .parse(raw, dialect="gps")
    msg = str(exc_info.value)
    assert "obrigatorio" in msg
    assert "gps.RMC" in msg  # contexto da sentenca no erro
    assert "status" in msg        # contexto do campo no erro


def test_choices_violation_raises_field_error():
    # RMC.status so aceita 'A' ou 'V'; forcamos um valor fora do conjunto.
    raw = "$GPRMC,225446,X,4916.45,N,12311.12,W,000.5,054.7,191194,020.3,E*71"
    with pytest.raises(FieldError) as exc_info:
        NMEASentence.parse(raw, dialect="gps")
    assert "conjunto permitido" in str(exc_info.value)


def test_custom_validate_callback():
    field = IntField("Percentual", "pct", validate=lambda v: 0 <= v <= 100)
    assert field.decode("50") == 50
    with pytest.raises(FieldError):
        field.decode("150")


def test_field_error_message_includes_field_name_and_raw_value():
    field = IntField("Numero de Satelites", "num_sats")
    with pytest.raises(FieldError) as exc_info:
        field.decode("abc")
    msg = str(exc_info.value)
    assert "Numero de Satelites" in msg
    assert "'abc'" in msg


def test_unknown_sentence_lists_known_ones():
    with pytest.raises(Exception) as exc_info:
        NMEASentence.parse("$GPXXX,1,2,3*53", dialect="gps")
    msg = str(exc_info.value)
    assert "XXX" in msg
    assert "GGA" in msg  # lista de sentencas conhecidas aparece na mensagem


def test_field_without_required_stays_optional_by_default():
    # StringField sem required continua aceitando vazio, retornando default (None)
    field = StringField("Campo Livre", "livre")
    assert field.decode("") is None
