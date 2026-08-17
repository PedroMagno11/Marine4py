from marine4py.core.nmea import NMEASentence


def test_parse_dbt():
    raw = "$SDDBT,25.0,f,7.6,M,4.1,F*35"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.sentence_id == "DBT"
    assert msg.talker == "SD"
    assert msg.depth_feet == 25.0
    assert msg.depth_meters == 7.6
    assert msg.depth_fathoms == 4.1
    assert msg.depth == 7.6  # preferencia por metros quando disponivel


def test_dbt_roundtrip():
    raw = "$SDDBT,25.0,f,7.6,M,4.1,F*35"
    msg = NMEASentence.parse(raw, dialect="nmea")
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="nmea")
    assert reparsed.depth_meters == msg.depth_meters
    assert reparsed.depth_feet == msg.depth_feet


def test_dbt_depth_fallback_para_pes_quando_metros_ausente():
    raw = "$SDDBT,25.0,f,,,4.1,F*57"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.depth_meters is None
    assert round(msg.depth, 4) == round(25.0 * 0.3048, 4)


def test_parse_dbk():
    raw = "$SDDBK,,f,3.2,M,,F*18"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.sentence_id == "DBK"
    assert msg.depth_meters == 3.2
    assert msg.depth == 3.2


def test_parse_dbs():
    raw = "$SDDBS,,f,5.5,M,,F*01"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.sentence_id == "DBS"
    assert msg.depth_meters == 5.5


def test_parse_dpt():
    raw = "$SDDPT,7.6,0.3*55"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.sentence_id == "DPT"
    assert msg.depth_meters == 7.6
    assert msg.offset == 0.3
    assert msg.depth == 7.6


def test_dpt_offset_negativo_transdutor_para_quilha():
    raw = "$SDDPT,7.6,-0.5*7E"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.offset == -0.5


def test_parse_mtw():
    raw = "$SDMTW,18.5,C*08"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.sentence_id == "MTW"
    assert msg.temperature == 18.5
    assert msg.unit == "C"


def test_mtw_roundtrip():
    raw = "$SDMTW,18.5,C*08"
    msg = NMEASentence.parse(raw, dialect="nmea")
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="nmea")
    assert reparsed.temperature == msg.temperature