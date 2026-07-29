from marine4py.core.nmea import NMEASentence
from marine4py.dialects.proprietary.sentences import (
    ASHR, ASHRATT, ASHRPOS, FEC, FECGPatt, GRMM, GRMW, KWDWPL, MGNWPL,
    NORBT0, NORC1, RDID, SRF103, SXN, SXN23, UBX, TNL, VTX, VTX0020,
)


def test_grmm_and_grmw_are_registered_directly_no_dispatch_needed():
    grmm = NMEASentence.parse("$PGRMM,WGS 84*06", dialect="proprietary")
    assert type(grmm) is GRMM
    assert grmm.datum == "WGS 84"


def test_sxn_dispatches_by_field_to_sxn23():
    raw = "$PSXN,23,0.30,-0.97,298.57,0.13*1B"
    msg = NMEASentence.parse(raw, dialect="proprietary")
    assert isinstance(msg, SXN23)
    assert msg.sentence_id == "SXN"  # REGISTRY conhece so o fabricante
    assert msg.roll == 0.3
    assert msg.pitch == -0.97
    assert msg.head == 298.57
    assert msg.heave == 0.13


def test_norbt0_bottom_track_real_example():
    raw = "$PNORBT0,1,040721,131335.3341,23.961,-48.122,-32.76800,10.00000,0.00,0x00000000*48"
    msg = NMEASentence.parse(raw, dialect="proprietary")
    assert type(msg) is NORBT0
    assert msg.beam == 1
    assert msg.datestamp.isoformat() == "2021-07-04"
    assert msg.dt1 == 23.961
    assert msg.bv == -32.768
    assert msg.stat == "0x00000000"


def test_norc1_roundtrip_constructed():
    msg = NORC1(
        talker="P", sentence_id="NORC1",
        data=("161109", "132455", "3", "11.0", "0.332", "0.332", "0.332",
              "78.9", "78.9", "78.9", "78.9", "78", "78", "78", "78", "78"),
    )
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="proprietary")
    assert reparsed.cn == msg.cn
    assert reparsed.vx == msg.vx


def test_rdid_roundtrip_constructed():
    msg = RDID(talker="P", sentence_id="RDID", data=("1.5", "-0.8", "270.3"))
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="proprietary")
    assert reparsed.pitch == 1.5
    assert reparsed.roll == -0.8
    assert reparsed.heading == 270.3


def test_srf103_roundtrip_constructed():
    msg = SRF103(talker="P", sentence_id="SRF103", data=("00", "1", "1", "1"))
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="proprietary")
    assert reparsed.sentence == "00"
    assert reparsed.rate == 1


def test_mgnwpl_roundtrip_constructed():
    msg = MGNWPL(
        talker="P", sentence_id="MGNWPL",
        data=("4916.45", "N", "12311.12", "W", "10.0", "M", "WPT1", "obs", "wf", "1"),
    )
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="proprietary")
    assert round(reparsed.latitude, 4) == 49.2742
    assert reparsed.wname == "WPT1"


def test_kwdwpl_roundtrip_constructed():
    msg = KWDWPL(
        talker="P", sentence_id="KWDWPL",
        data=("150803", "V", "4237.14", "N", "07120.83", "W", "", "", "190316", "", "test", "/'"),
    )
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="proprietary")
    assert reparsed.status == "V"
    assert reparsed.wname == "test"


def test_vtx_dispatches_by_field_to_vtx0020():
    msg = VTX0020(
        talker="P", sentence_id="VTX",
        data=("0020", "1", "4237.14", "N", "07120.83", "W", "150.0", "M"),
    )
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="proprietary")
    assert isinstance(reparsed, VTX0020)
    assert reparsed.sentence_id == "VTX"
    assert round(reparsed.latitude, 4) == 42.619


def test_fec_dispatches_by_field_to_gpatt():
    msg = FECGPatt(talker="P", sentence_id="FEC", data=("GPatt", "10.1", "2.2", "0.3"))
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="proprietary")
    assert isinstance(reparsed, FECGPatt)
    assert reparsed.yaw == 10.1


def test_ashr_dispatches_literal_code_to_pos():
    msg = ASHRPOS(
        talker="P", sentence_id="ASHR",
        data=("POS", "1", "8", "092751.0", "3723.09", "N", "12200.32", "W",
              "10.5", "", "0.0", "0.0", "0.0", "1.2", "0.9", "1.1", "1.0", "0"),
    )
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="proprietary")
    assert isinstance(reparsed, ASHRPOS)
    assert reparsed.sat_count == 8


def test_ashr_falls_back_to_att_when_no_literal_code_matches():
    msg = ASHRATT(
        talker="P", sentence_id="ASHR",
        data=("092751.0", "45.0", "T", "0.3", "-0.9", "0.1", "0.01", "0.01", "0.02", "1", "1"),
    )
    reparsed = NMEASentence.parse(str(msg).strip(), dialect="proprietary")
    assert isinstance(reparsed, ASHRATT)
    assert reparsed.true_heading == 45.0
    assert reparsed.roll == 0.3


def test_all_manufacturer_base_dispatchers_have_independent_subtype_dicts():
    assert TNL._subtypes is not UBX._subtypes
    assert SXN._subtypes is not VTX._subtypes
    assert FEC._subtypes is not ASHR._subtypes
    assert "POS" in ASHR._subtypes
    assert "POS" not in TNL._subtypes
