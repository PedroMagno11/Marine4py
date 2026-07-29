from marine4py.core.checksum import NoChecksum, XorChecksum
from marine4py.core.field import FloatField, IntField
from marine4py.core.framing import FramingStrategy


def test_field_decode_encode_roundtrip():
    f = FloatField("Altitude", "altitude")
    assert f.decode("100.00") == 100.0
    assert f.encode(100.0) == "100.0"


def test_field_empty_uses_default():
    f = IntField("Num", "num", default=None)
    assert f.decode("") is None


def test_framing_generic_roundtrip():
    framing = FramingStrategy(start="#", field_sep=";", checksum_sep="*",
                               checksum_strategy=XorChecksum(), line_end="\n", talker_len=2)
    raw = framing.join("XY", "ABC", ["1", "2", "3"])
    parsed = framing.split(raw)
    assert parsed.talker == "XY"
    assert parsed.sentence_id == "ABC"
    assert parsed.fields == ["1", "2", "3"]


def test_framing_no_checksum():
    framing = FramingStrategy(start="$", checksum_sep=None, checksum_strategy=NoChecksum(), talker_len=0)
    raw = framing.join(None, "FOO", ["a", "b"])
    parsed = framing.split(raw)
    assert parsed.sentence_id == "FOO"
    assert parsed.fields == ["a", "b"]
