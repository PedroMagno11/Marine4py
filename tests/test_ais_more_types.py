# Vetores de teste reais, extraidos do arquivo de regressao do projeto gpsd
# (test/sample.aivdm), com os valores decodificados esperados ja
# documentados junto de cada sentenca -- nao inventamos nenhum numero.

from marine4py.core.nmea import NMEASentence
from marine4py.dialects.ais import payload6bit
from marine4py.dialects.ais.assembler import AisAssembler


def test_decode_type4_base_station_report():
    decoded = payload6bit.decode_type_4("403OviQuMGCqWrRO9>E6fE700@GO")
    assert decoded["msg_type"] == 4
    assert decoded["mmsi"] == 3669702
    assert decoded["year"] == 2007
    assert decoded["month"] == 5
    assert decoded["day"] == 14
    assert decoded["hour"] == 19
    assert decoded["minute"] == 57
    assert decoded["second"] == 39
    assert decoded["position_accuracy"] == 1
    assert decoded["epfd"] == 7
    assert decoded["raim"] is False


def test_decode_type9_sar_aircraft():
    decoded = payload6bit.decode_type_9("91b77=h3h00nHt0Q3r@@07000<0b")
    assert decoded["msg_type"] == 9
    assert decoded["mmsi"] == 111265591
    assert decoded["altitude"] == 15
    assert decoded["sog_knots"] == 0
    assert decoded["second"] == 28


def test_decode_type19_extended_class_b():
    decoded = payload6bit.decode_type_19(
        "C5N3SRgPEnJGEBT>NhWAwwo862PaLELTBJ:V00000000S0D:R220"
    )
    assert decoded["msg_type"] == 19
    assert decoded["mmsi"] == 367059850
    assert decoded["sog_knots"] == 8.7
    assert decoded["cog"] == 335.9
    assert decoded["name"] == "CAPT.J.RIMES"
    assert decoded["ship_type"] == 70
    assert decoded["to_bow"] == 5
    assert decoded["to_stern"] == 21
    assert decoded["to_port"] == 4
    assert decoded["to_starboard"] == 4
    assert decoded["epfd"] == 1
    assert decoded["dte"] == 0


def test_decode_type21_aid_to_navigation_with_name_split_across_two_fields():
    # O nome desse farolete tem 32 caracteres -- nao cabe nos 20 do campo
    # principal (120 bits), entao vem completado pela extensao no fim da
    # mensagem. So fica correto se os dois pedacos forem concatenados
    # ANTES de cortar no '@' de padding.
    assembler = AisAssembler()
    fragments = [
        "!AIVDM,2,1,5,B,E1mg=5J1T4W0h97aRh6ba84<h2d;W:Te=eLvH50```q,0*46",
        "!AIVDM,2,2,5,B,:D44QDlp0C1DU00,2*36",
    ]
    payload = None
    for line in fragments:
        msg = NMEASentence.parse(line, dialect="ais")
        payload = assembler.feed(msg)

    decoded = payload6bit.decode(payload)
    assert decoded["msg_type"] == 21
    assert decoded["mmsi"] == 123456789
    assert decoded["aid_type"] == 20
    assert decoded["name"] == "CHINA ROSE MURPHY EXPRESS ALERT"
    assert round(decoded["lon"], 6) == round(-122.698591667, 6)
    assert round(decoded["lat"], 6) == round(47.9206183333, 6)
    assert decoded["to_bow"] == 5
    assert decoded["to_stern"] == 5
    assert decoded["to_port"] == 5
    assert decoded["to_starboard"] == 5
    assert decoded["epfd"] == 1
    assert decoded["second"] == 50
    assert decoded["off_position"] == 0
    assert decoded["regional"] == 165
    assert decoded["raim"] is False
    assert decoded["virtual_aid"] == 0
    assert decoded["assigned"] == 0


def test_decode_type24_part_a_has_only_name():
    decoded = payload6bit.decode_type_24("H42O55i18tMET00000000000000")
    assert decoded["msg_type"] == 24
    assert decoded["mmsi"] == 271041815
    assert decoded["part_number"] == 0
    assert decoded["name"] == "PROGUY"
    assert "ship_type" not in decoded  # Part A nao tem esses campos


def test_decode_type24_part_b_has_ship_details():
    decoded = payload6bit.decode_type_24("H42O55lti4hhhilD3nink000?050")
    assert decoded["msg_type"] == 24
    assert decoded["mmsi"] == 271041815
    assert decoded["part_number"] == 1
    assert decoded["ship_type"] == 60
    assert decoded["callsign"] == "TC6163"
    assert decoded["to_bow"] == 0
    assert decoded["to_stern"] == 15
    assert decoded["to_port"] == 0
    assert decoded["to_starboard"] == 5
    assert "name" not in decoded  # Part B nao tem nome


def test_vessel_and_infrastructure_type_sets_are_disjoint():
    assert payload6bit.VESSEL_MESSAGE_TYPES.isdisjoint(payload6bit.INFRASTRUCTURE_MESSAGE_TYPES)
    assert payload6bit.VESSEL_MESSAGE_TYPES == {1, 2, 3, 5, 18, 19, 24}
    assert payload6bit.INFRASTRUCTURE_MESSAGE_TYPES == {4, 9, 21}


def test_all_new_types_are_registered_in_decoders():
    for msg_type in (4, 9, 19, 21, 24):
        assert msg_type in payload6bit.DECODERS
