from marine4py.core.checksum import XorChecksum
from marine4py.core.field import Field, FloatField, StringField
from marine4py.core.framing import FramingStrategy
from marine4py.core.nmea import NMEASentence
from marine4py.core.registry import REGISTRY


MEU_FRAMING = FramingStrategy(
    start="@", field_sep="|", checksum_sep="*",
    checksum_strategy=XorChecksum(), line_end="\n", talker_len=0,
)
REGISTRY.set_framing("meu_protocolo_teste", MEU_FRAMING)


class MeuProtocoloSentence(NMEASentence):
    dialect = "meu_protocolo_teste"
    framing = MEU_FRAMING


class TLM(MeuProtocoloSentence):
    sentence_id = "TLM"
    fields = (
        Field("Timestamp", "timestamp", parse=int, render=str),
        FloatField("Bateria", "battery"),
        StringField("Status", "status"),
    )


def test_custom_dialect_roundtrip():
    msg = TLM(sentence_id="TLM", data=("1732000000", "87.5", "OK"))
    raw = str(msg)
    parsed = NMEASentence.parse(raw, dialect="meu_protocolo_teste")
    assert parsed.timestamp == 1732000000
    assert parsed.battery == 87.5
    assert parsed.status == "OK"


def test_custom_dialect_bad_checksum_raises():
    from marine4py.core.error import ChecksumError
    import pytest
    with pytest.raises(ChecksumError):
        NMEASentence.parse("@TLM|1732000000|87.5|OK*00\n", dialect="meu_protocolo_teste")
