# Vetores de teste reais, extraidos da propria suite de testes da pynmea2
# (test/test_proprietary.py) -- sentencas capturadas de receptores de
# verdade, com os valores decodificados esperados ja documentados.

from marine4py.core.nmea import NMEASentence
from marine4py.dialects.proprietary.sentences import TNLBPQ, UBX00, UBX04


def test_tnl_dispatches_to_bpq_subclass():
    raw = "$PTNL,BPQ,224445.06,021207,3723.09383914,N,12200.32620132,W,EHT-5.923,M,5*60"
    msg = NMEASentence.parse(raw, dialect="proprietary")
    assert isinstance(msg, TNLBPQ)
    assert msg.sentence_id == "TNL"  # registrado no REGISTRY so pelo fabricante
    assert msg.talker == "P"


def test_tnl_bpq_fields():
    raw = "$PTNL,BPQ,224445.06,021207,3723.09383914,N,12200.32620132,W,EHT-5.923,M,5*60"
    msg = NMEASentence.parse(raw, dialect="proprietary")
    assert msg.datestamp.isoformat() == "2007-12-02"
    assert round(msg.latitude, 9) == 37.384897319
    assert round(msg.longitude, 11) == round(-122.00543668866666, 11)
    assert msg.quality == 5


def test_tnl_bpq_roundtrip():
    raw = "$PTNL,BPQ,224445.06,021207,3723.09383914,N,12200.32620132,W,EHT-5.923,M,5*60"
    msg = NMEASentence.parse(raw, dialect="proprietary")
    assert str(msg).strip() == raw  # esse aqui bate exato: nenhum campo float


def test_ubx_dispatches_to_correct_subtype():
    raw_00 = "$PUBX,00,074440.00,4703.74203,N,00736.82976,E,576.991,D3,2.0,2.0,0.091,0.00,-0.032,,0.76,1.05,0.65,14,0,0*70"
    raw_04 = "$PUBX,04,073824.00,131014,113903.99,1814,16,495176,342.504,21*18"

    msg00 = NMEASentence.parse(raw_00, dialect="proprietary")
    msg04 = NMEASentence.parse(raw_04, dialect="proprietary")

    assert isinstance(msg00, UBX00)
    assert isinstance(msg04, UBX04)
    assert msg00.sentence_id == msg04.sentence_id == "UBX"  # mesmo fabricante, subtipos diferentes


def test_ubx00_position_fields():
    raw = "$PUBX,00,074440.00,4703.74203,N,00736.82976,E,576.991,D3,2.0,2.0,0.091,0.00,-0.032,,0.76,1.05,0.65,14,0,0*70"
    msg = NMEASentence.parse(raw, dialect="proprietary")
    assert msg.timestamp.hour == 7
    assert msg.timestamp.minute == 44
    assert msg.lat_dir == "N"
    assert round(msg.latitude, 6) == round(47.06236716666667, 6)
    assert msg.num_svs == 14


def test_ubx00_roundtrip_via_reparse():
    # o valor bate; a string exata pode diferir em zeros a direita de
    # float (0.00 -> 0.0 no re-render), mesma normalizacao ja aceita
    # pro resto do projeto (ver GGA/GRMZ) -- por isso reparseamos em
    # vez de comparar a string literal.
    raw = "$PUBX,00,074440.00,4703.74203,N,00736.82976,E,576.991,D3,2.0,2.0,0.091,0.00,-0.032,,0.76,1.05,0.65,14,0,0*70"
    msg = NMEASentence.parse(raw, dialect="proprietary")
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="proprietary")
    assert reparsed.lat == msg.lat
    assert reparsed.num_svs == msg.num_svs
    assert reparsed.sog == msg.sog


def test_ubx04_clock_fields():
    raw = "$PUBX,04,073824.00,131014,113903.99,1814,16,495176,342.504,21*18"
    msg = NMEASentence.parse(raw, dialect="proprietary")
    assert msg.date.isoformat() == "2014-10-13"
    assert msg.time.hour == 7
    assert msg.time.minute == 38
    assert msg.clk_bias == 495176


def test_ubx04_roundtrip():
    raw = "$PUBX,04,073824.00,131014,113903.99,1814,16,495176,342.504,21*18"
    msg = NMEASentence.parse(raw, dialect="proprietary")
    assert str(msg).strip() == raw


def test_all_three_manufacturers_coexist_in_same_dialect():
    grme = NMEASentence.parse("$PGRME,15.0,M,25.0,M,29.0,M*16", dialect="proprietary")
    tnl = NMEASentence.parse(
        "$PTNL,BPQ,224445.06,021207,3723.09383914,N,12200.32620132,W,EHT-5.923,M,5*60",
        dialect="proprietary",
    )
    ubx = NMEASentence.parse("$PUBX,04,073824.00,131014,113903.99,1814,16,495176,342.504,21*18", dialect="proprietary")
    assert (grme.sentence_id, tnl.sentence_id, ubx.sentence_id) == ("GRME", "TNL", "UBX")
