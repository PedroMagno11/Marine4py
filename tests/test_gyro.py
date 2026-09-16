from marine4py.core.nmea import NMEASentence
from marine4py.dialects.nmea.gyro_sentences import HDG, ROT


def test_parse_hdg():
    raw = "$HEHDG,045.0,2.0,E,3.5,W*53"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.sentence_id == "HDG"
    assert msg.talker == "HE"
    assert msg.heading == 45.0
    assert msg.deviation == 2.0
    assert msg.deviation_dir == "E"
    assert msg.variation == 3.5
    assert msg.variation_dir == "W"


def test_hdg_true_heading_soma_desvio_e_variacao_com_sinal():
    raw = "$HEHDG,045.0,2.0,E,3.5,W*53"
    msg = NMEASentence.parse(raw, dialect="nmea")
    # 45 + 2 (E, soma) - 3.5 (W, subtrai) = 43.5
    assert round(msg.true_heading, 2) == 43.5


def test_hdg_true_heading_sem_desvio_nem_variacao_retorna_heading_bruto():
    raw = "$HEHDG,090.0,,,,*4D"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.deviation is None
    assert msg.variation is None
    assert msg.true_heading == 90.0


def test_hdg_roundtrip():
    raw = "$HEHDG,045.0,2.0,E,3.5,W*53"
    msg = NMEASentence.parse(raw, dialect="nmea")
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="nmea")
    assert reparsed.heading == msg.heading
    assert reparsed.deviation == msg.deviation


def test_parse_rot():
    raw = "$HEROT,-15.5,A*37"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.sentence_id == "ROT"
    assert msg.rate == -15.5  # negativo == proa girando para bombordo
    assert msg.status == "A"


def test_parse_rot_dado_invalido():
    raw = "$TIROT,,V*02"
    msg = NMEASentence.parse(raw, dialect="nmea")
    assert msg.rate is None
    assert msg.status == "V"


def test_rot_roundtrip():
    raw = "$HEROT,-15.5,A*37"
    msg = NMEASentence.parse(raw, dialect="nmea")
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="nmea")
    assert reparsed.rate == msg.rate
    assert reparsed.status == msg.status


def test_hdg_criar_do_zero_sem_parse_previo():
    # encode puro: instancia a classe direto, sem passar por NMEASentence.parse
    msg = HDG(talker="HE", sentence_id="HDG", data=("045.0", "2.0", "E", "3.5", "W"))
    assert str(msg) == "$HEHDG,45.0,2.0,E,3.5,W*63\r\n"
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="nmea")
    assert reparsed.heading == 45.0
    assert reparsed.true_heading == 43.5


def test_rot_criar_do_zero_com_dado_invalido():
    msg = ROT(talker="TI", sentence_id="ROT", data=("", "V"))
    assert str(msg) == "$TIROT,,V*02\r\n"
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="nmea")
    assert reparsed.rate is None
    assert reparsed.status == "V"