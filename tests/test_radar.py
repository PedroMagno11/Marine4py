from marine4py.core.nmea import NMEASentence


def test_parse_ttm():
    raw = "$RATTM,11,25.3,236.1,T,4.2,187.0,T,1.8,-3.5,N,SHIP A,T,*13"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.sentence_id == "TTM"
    assert msg.talker == "RA"
    assert msg.target_number == 11
    assert msg.target_distance == 25.3
    assert msg.bearing == 236.1
    assert msg.bearing_units == "T"
    assert msg.target_speed == 4.2
    assert msg.cpa_distance == 1.8
    assert msg.cpa_time == -3.5  # negativo == distancia aumentando
    assert msg.speed_dist_units == "N"
    assert msg.target_name == "SHIP A"
    assert msg.target_status == "T"
    assert msg.reference_target is None


def test_ttm_roundtrip():
    raw = "$RATTM,11,25.3,236.1,T,4.2,187.0,T,1.8,-3.5,N,SHIP A,T,*13"
    msg = NMEASentence.parse(raw, dialect="nmea")
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="nmea")
    assert reparsed.target_number == msg.target_number
    assert reparsed.target_name == msg.target_name
    assert reparsed.cpa_time == msg.cpa_time


def test_parse_ttm_alvo_recem_adquirido_sem_dados_de_rastreio():
    raw = "$RATTM,05,12.0,090.0,R,,,,,,,,,*1F"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.target_number == 5
    assert msg.target_speed is None
    assert msg.target_status is None


def test_parse_rsd():
    raw = "$RARSD,,,,,,,,,4.5,270.0,12.0,N,H*65"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.sentence_id == "RSD"
    assert msg.talker == "RA"
    assert msg.cursor_range == 4.5
    assert msg.cursor_bearing == 270.0
    assert msg.range_scale == 12.0
    assert msg.range_units == "N"
    assert msg.display_rotation == "H"  # head-up


def test_rsd_roundtrip():
    raw = "$RARSD,,,,,,,,,4.5,270.0,12.0,N,H*65"
    msg = NMEASentence.parse(raw, dialect="nmea")
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="nmea")
    assert reparsed.cursor_range == msg.cursor_range
    assert reparsed.display_rotation == msg.display_rotation


def test_parse_osd():
    raw = "$IIOSD,045.0,A,046.0,M,12.3,M,001.5,000.4,N*66"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.sentence_id == "OSD"
    assert msg.heading == 45.0
    assert msg.heading_status == "A"
    assert msg.course == 46.0
    assert msg.course_ref == "M"
    assert msg.speed == 12.3
    assert msg.speed_ref == "M"
    assert msg.set_deg == 1.5
    assert msg.drift == 0.4
    assert msg.speed_units == "N"


def test_osd_roundtrip():
    raw = "$IIOSD,045.0,A,046.0,M,12.3,M,001.5,000.4,N*66"
    msg = NMEASentence.parse(raw, dialect="nmea")
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="nmea")
    assert reparsed.heading == msg.heading
    assert reparsed.speed == msg.speed


def test_parse_tll():
    raw = "$RATLL,03,4916.45,N,12311.12,W,SHIP B,163042.00,T,*51"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.sentence_id == "TLL"
    assert msg.target_number == 3
    assert msg.target_name == "SHIP B"
    assert msg.target_status == "T"
    assert msg.timestamp.hour == 16
    assert round(msg.latitude, 4) == 49.2742
    assert round(msg.longitude, 4) == -123.1853


def test_tll_roundtrip():
    raw = "$RATLL,03,4916.45,N,12311.12,W,SHIP B,163042.00,T,*51"
    msg = NMEASentence.parse(raw, dialect="nmea")
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="nmea")
    assert reparsed.target_number == msg.target_number
    assert round(reparsed.latitude, 4) == round(msg.latitude, 4)