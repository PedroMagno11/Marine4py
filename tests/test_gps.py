from marine4py.core.nmea import NMEASentence

def test_parse_gga():
    raw = "$GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,100.00,M,-33.9,M,,0000*6D"
    msg = NMEASentence.parse(raw, dialect="gps")
    assert msg.sentence_id == "GGA"
    assert msg.talker == "GP"
    assert msg.lat == "1929.045"
    assert msg.lat_dir == "S"
    assert msg.gps_qual == 1
    assert msg.num_sats == 4
    assert msg.altitude == 100.0
    assert round(msg.latitude, 4) == -19.4841
    assert round(msg.longitude, 4) == 24.1751


def test_gga_roundtrip():
    raw = "$GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,100.00,M,-33.9,M,,0000*6D"
    msg = NMEASentence.parse(raw, dialect="gps")
    regenerated = str(msg).strip()
    reparsed = NMEASentence.parse(regenerated, dialect="gps")
    assert reparsed.lat == msg.lat
    assert reparsed.altitude == msg.altitude


def test_parse_rmc():
    raw = "$GPRMC,225446,A,4916.45,N,12311.12,W,000.5,054.7,191194,020.3,E*68"
    msg = NMEASentence.parse(raw, dialect="gps")
    assert msg.sentence_id == "RMC"
    assert msg.status == "A"
    assert msg.spd_over_grnd == 0.5
    assert msg.true_course == 54.7
    assert msg.datestamp.year == 1994
    assert msg.datestamp.month == 11
    assert msg.datestamp.day == 19


def test_parse_vtg():
    raw = "$GPVTG,054.7,T,034.4,M,005.5,N,010.2,K*48"
    msg = NMEASentence.parse(raw, dialect="gps")
    assert msg.sentence_id == "VTG"
    assert msg.true_track == 54.7
    assert msg.spd_over_grnd_kmph == 10.2


def test_parse_gsa():
    raw = "$GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39"
    msg = NMEASentence.parse(raw, dialect="gps")
    assert msg.sentence_id == "GSA"
    assert msg.mode_selection == "A"
    assert msg.mode_fix_type == 3
    assert msg.sv_id01 == "04"
    assert msg.sv_id03 is None  # campo vazio na sentenca original
    assert msg.pdop == 2.5


def test_parse_gsv():
    raw = "$GPGSV,3,1,11,03,03,111,00,04,15,270,00,06,01,010,00,13,06,292,00*74"
    msg = NMEASentence.parse(raw, dialect="gps")
    assert msg.sentence_id == "GSV"
    assert msg.total_num_msgs == 3
    assert msg.num_sv_in_view == 11
    assert msg.sv_prn_num_1 == 3
    assert msg.azimuth_4 == 292


def test_parse_zda():
    raw = "$GPZDA,201530.00,04,07,2002,00,00*60"
    msg = NMEASentence.parse(raw, dialect="gps")
    assert msg.sentence_id == "ZDA"
    assert msg.day == 4
    assert msg.month == 7
    assert msg.year == 2002
    assert msg.timestamp.hour == 20


def test_parse_gll():
    raw = "$GPGLL,4916.45,N,12311.12,W,225444,A*31"
    msg = NMEASentence.parse(raw, dialect="gps")
    assert msg.sentence_id == "GLL"
    assert msg.status == "A"
    assert round(msg.latitude, 4) == 49.2742
    assert round(msg.longitude, 4) == -123.1853


def test_gsv_roundtrip():
    raw = "$GPGSV,3,1,11,03,03,111,00,04,15,270,00,06,01,010,00,13,06,292,00*74"
    msg = NMEASentence.parse(raw, dialect="gps")
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="gps")
    assert reparsed.sv_prn_num_1 == msg.sv_prn_num_1
    assert reparsed.num_sv_in_view == msg.num_sv_in_view
