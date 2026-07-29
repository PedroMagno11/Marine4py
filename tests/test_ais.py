from marine4py.core.nmea import NMEASentence
from marine4py.dialects.ais import payload6bit


def test_parse_vdm():
    raw = "!AIVDM,1,1,,A,15M67FC000G?ufbE`FepT@3n00Sa,0*5F"
    msg = NMEASentence.parse(raw, dialect="ais")
    assert msg.sentence_id == "VDM"
    assert msg.talker == "AI"
    assert msg.frag_count == 1
    assert msg.frag_number == 1
    assert msg.channel == "A"
    assert msg.payload == "15M67FC000G?ufbE`FepT@3n00Sa"
    assert msg.fill_bits == 0


def test_decode_payload_type1():
    raw = "!AIVDM,1,1,,A,15M67FC000G?ufbE`FepT@3n00Sa,0*5F"
    msg = NMEASentence.parse(raw, dialect="ais")
    decoded = payload6bit.decode(msg.payload)
    assert decoded["msg_type"] == 1
    assert decoded["mmsi"] == 366053209
    # lat/lon devem cair na baia de San Francisco (vetor de teste classico do AIS)
    assert 37.5 < decoded["lat"] < 38.0
    assert -122.6 < decoded["lon"] < -122.0
