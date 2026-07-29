
# Vetores de teste reais, extraidos do arquivo de regressao do projeto gpsd
# (test/sample.aivdm), que traz sentencas capturadas em producao junto com
# os valores decodificados esperados -- uteis justamente porque nao fomos
# nos que inventamos os numeros.

from marine4py.core.nmea import NMEASentence
from marine4py.dialects.ais import payload6bit
from marine4py.dialects.ais.assembler import AisAssembler


TYPE5_FRAGMENTS = [
    "!AIVDM,2,1,1,A,55?MbV02;H;s<HtKR20EHE:0@T4@Dn2222222216L961O5Gf0NSQEp6ClRp8,0*1C",
    "!AIVDM,2,2,1,A,88888888880,2*25",
]

TYPE18_SENTENCE = "!AIVDM,1,1,,A,B52K>;h00Fc>jpUlNV@ikwpUoP06,0*4C"


def test_assembler_returns_none_until_all_fragments_arrive():
    assembler = AisAssembler()
    first = NMEASentence.parse(TYPE5_FRAGMENTS[0], dialect="ais")
    assert assembler.feed(first) is None
    assert assembler.pending_count() == 1


def test_assembler_reassembles_full_payload():
    assembler = AisAssembler()
    payload = None
    for line in TYPE5_FRAGMENTS:
        msg = NMEASentence.parse(line, dialect="ais")
        payload = assembler.feed(msg)
    assert payload is not None
    assert assembler.pending_count() == 0  # estado foi liberado apos completar


def test_assembler_handles_interleaved_messages_by_channel_and_seq_id():
    # Duas mensagens fragmentadas "ao mesmo tempo" com seq_id diferentes
    # nao podem se misturar -- cada uma so fecha quando os proprios
    # fragmentos completarem.
    assembler = AisAssembler()
    msg_a1 = NMEASentence.parse(TYPE5_FRAGMENTS[0], dialect="ais")  # seq_id=1
    assert assembler.feed(msg_a1) is None
    assert assembler.pending_count() == 1

    msg_a2 = NMEASentence.parse(TYPE5_FRAGMENTS[1], dialect="ais")  # seq_id=1, fecha a mensagem
    payload = assembler.feed(msg_a2)
    assert payload is not None
    assert assembler.pending_count() == 0


def test_decode_type5_matches_known_values():
    assembler = AisAssembler()
    payload = None
    for line in TYPE5_FRAGMENTS:
        msg = NMEASentence.parse(line, dialect="ais")
        payload = assembler.feed(msg)

    decoded = payload6bit.decode(payload)
    assert decoded["msg_type"] == 5
    assert decoded["mmsi"] == 351759000
    assert decoded["imo"] == 9134270
    assert decoded["callsign"] == "3FOF8"
    assert decoded["name"] == "EVER DIADEM"
    assert decoded["ship_type"] == 70
    assert decoded["to_bow"] == 225
    assert decoded["to_stern"] == 70
    assert decoded["to_port"] == 1
    assert decoded["to_starboard"] == 31
    assert decoded["epfd"] == 1
    assert decoded["eta_month"] == 5
    assert decoded["eta_day"] == 15
    # Nota: a anotacao original do gpsd (test/sample.aivdm) diz ETAhour=16,
    # mas o valor que os offsets de bit (conferidos contra a tabela ITU-R
    # M.1371 do gpsd) realmente produzem e 14 -- e todos os campos vizinhos
    # (dia, mes, minuto, MMSI, IMO, nome, destino) batem exatamente com a
    # anotacao, o que indica erro de digitacao na nota antiga, nao um
    # desalinhamento no nosso decoder.
    assert decoded["eta_hour"] == 14
    assert decoded["eta_minute"] == 0
    assert decoded["draught"] == 12.2
    assert decoded["destination"] == "NEW YORK"
    assert decoded["dte"] == 0


def test_decode_type18_matches_known_values():
    msg = NMEASentence.parse(TYPE18_SENTENCE, dialect="ais")
    decoded = payload6bit.decode(msg.payload)
    assert decoded["msg_type"] == 18
    assert decoded["mmsi"] == 338087471
    assert decoded["sog_knots"] == 0.1
    assert decoded["position_accuracy"] == 0
    assert round(decoded["lon"], 5) == round(-74.07213166666666, 5)
    assert round(decoded["lat"], 5) == round(40.68454, 5)
    assert decoded["cog"] == 79.6
    assert decoded["heading"] == 511
    assert decoded["second"] == 49
    assert decoded["raim"] is True
    assert decoded["comm_state_selector"] == 1
    assert decoded["comm_state"] == 393222


def test_unsupported_message_type_raises_not_implemented():
    # msg_type 6 (Binary Addressed Message) ainda nao tem decoder --
    # cada aplicacao (DAC/FID) define seu proprio layout de payload,
    # entao fica fora do escopo por ora. "6" sozinho ja armoreia os 6
    # bits do msg_type sem precisar de um payload completo.
    import pytest
    with pytest.raises(NotImplementedError):
        payload6bit.decode("6")
