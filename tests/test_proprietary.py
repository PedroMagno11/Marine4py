from marine4py.core.error import FieldError
from marine4py.core.nmea import NMEASentence


def test_parse_grme():
    raw = "$PGRME,15.0,M,25.0,M,29.0,M*16"
    msg = NMEASentence.parse(raw, dialect="proprietary")
    assert msg.sentence_id == "GRME"
    assert msg.talker == "P"
    assert msg.hpe == 15.0
    assert msg.vpe == 25.0
    assert msg.osepe == 29.0


def test_parse_grmz():
    raw = "$PGRMZ,328.0,f,3*0C"
    msg = NMEASentence.parse(raw, dialect="proprietary")
    assert msg.sentence_id == "GRMZ"
    assert msg.altitude == 328.0
    assert msg.fix_dimension == 3


def test_parse_grmv():
    raw = "$PGRMV,0.5,-0.3,0.1*76"
    msg = NMEASentence.parse(raw, dialect="proprietary")
    assert msg.sentence_id == "GRMV"
    assert msg.east_velocity == 0.5
    assert msg.north_velocity == -0.3
    assert msg.up_velocity == 0.1


def test_proprietary_roundtrip():
    raw = "$PGRMZ,328.0,f,3*0C"
    msg = NMEASentence.parse(raw, dialect="proprietary")
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="proprietary")
    assert reparsed.altitude == msg.altitude
    assert reparsed.fix_dimension == msg.fix_dimension


def test_proprietary_and_standard_dialects_coexist():
    # mesmo processo, duas FramingStrategy diferentes (talker_len=2 vs 1),
    # nenhuma interfere na outra
    gga = NMEASentence.parse(
        "$GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,100.00,M,-33.9,M,,0000*6D",
        dialect="gps",
    )
    grmz = NMEASentence.parse("$PGRMZ,328.0,f,3*0C", dialect="proprietary")
    assert gga.sentence_id == "GGA"
    assert grmz.sentence_id == "GRMZ"


def test_grmz_choices_validation():
    # fix_dimension so aceita 2 ou 3 (2D/3D); 5 deve falhar
    raw = "$PGRMZ,328.0,f,5*0A"
    try:
        NMEASentence.parse(raw, dialect="proprietary")
        assert False, "deveria ter levantado FieldError"
    except FieldError as exc:
        assert "conjunto permitido" in str(exc)
