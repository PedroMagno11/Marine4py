import pytest

from marine4py.core.error import ChecksumError
from marine4py.core.stream import NMEASentenceStream



GGA_RAW = "$GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,100.00,M,-33.9,M,,0000*6D"
VTG_RAW = "$GPVTG,054.7,T,034.4,M,005.5,N,010.2,K*48"
GRMZ_RAW = "$PGRMZ,328.0,f,3*0C"
AIS_TYPE18_RAW = "!AIVDM,1,1,,A,B52K>;h00Fc>jpUlNV@ikwpUoP06,0*4C"


def test_feed_complete_line_in_one_chunk():
    stream = NMEASentenceStream(dialects="gps")
    results = stream.feed(GGA_RAW + "\r\n")
    assert len(results) == 1
    assert results[0].sentence_id == "GGA"


def test_feed_sentence_split_across_two_chunks():
    stream = NMEASentenceStream(dialects="gps")
    # quebra a sentenca no meio, simulando um socket entregando em partes
    metade1, metade2 = GGA_RAW[:30], GGA_RAW[30:]
    assert stream.feed(metade1) == []  # ainda incompleta, nada retornado
    results = stream.feed(metade2 + "\r\n")
    assert len(results) == 1
    assert results[0].sentence_id == "GGA"


def test_feed_multiple_lines_in_one_chunk():
    stream = NMEASentenceStream(dialects="gps")
    chunk = GGA_RAW + "\r\n" + VTG_RAW + "\r\n"
    results = stream.feed(chunk)
    assert [s.sentence_id for s in results] == ["GGA", "VTG"]


def test_flush_handles_trailing_line_without_newline():
    stream = NMEASentenceStream(dialects="gps")
    assert stream.feed(VTG_RAW) == []  # sem \n, fica no buffer
    sentence = stream.flush()
    assert sentence is not None
    assert sentence.sentence_id == "VTG"


def test_multi_dialect_stream_routes_each_line_correctly():
    stream = NMEASentenceStream(dialects=["gps", "proprietary", "ais"])
    log = "\r\n".join([GGA_RAW, GRMZ_RAW, AIS_TYPE18_RAW]) + "\r\n"
    results = stream.feed(log)
    kinds = [(type(s).__module__.split(".")[-2], s.sentence_id) for s in results]
    assert kinds == [
        ("gps", "GGA"),
        ("proprietary", "GRMZ"),
        ("ais", "VDM"),
    ]


def test_on_error_skip_ignores_bad_lines():
    stream = NMEASentenceStream(dialects="gps", on_error="skip")
    log = "linha invalida sem cifrao\r\n" + VTG_RAW + "\r\n"
    results = stream.feed(log)
    assert len(results) == 1
    assert results[0].sentence_id == "VTG"


def test_on_error_raise_propagates_exception():
    stream = NMEASentenceStream(dialects="gps")  # default: on_error="raise"
    with pytest.raises(ChecksumError):
        stream.feed("$GPXXX,bad*00\r\n")


def test_on_error_callback_receives_line_and_errors():
    captured = []

    def handler(line, errors):
        captured.append((line, len(errors)))

    stream = NMEASentenceStream(dialects="gps", on_error=handler)
    results = stream.feed("linha ruim\r\n" + VTG_RAW + "\r\n")
    assert len(results) == 1  # a linha ruim foi descartada, nao interrompeu o stream
    assert len(captured) == 1
    assert captured[0][0] == "linha ruim"


def test_requires_at_least_one_dialect():
    with pytest.raises(ValueError):
        NMEASentenceStream(dialects=[])
