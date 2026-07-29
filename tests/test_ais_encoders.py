from marine4py.dialects.ais import payload6bit


def test_roundtrip_type5_static_and_voyage_data():
    payload, fill_bits = payload6bit.encode_type_5(
        mmsi=366999999,
        imo=9074729,
        callsign="WDA9674",
        name="MT MITCHELL",
        ship_type=99,
        to_bow=90, to_stern=90, to_port=10, to_starboard=10,
        epfd=1,
        eta_month=1, eta_day=2, eta_hour=8, eta_minute=0,
        draught=6.0,
        destination="SEATTLE",
        dte=0,
    )
    assert fill_bits == (6 - 424 % 6) % 6

    decoded = payload6bit.decode_type_5(payload)
    assert decoded["msg_type"] == 5
    assert decoded["mmsi"] == 366999999
    assert decoded["imo"] == 9074729
    assert decoded["callsign"] == "WDA9674"
    assert decoded["name"] == "MT MITCHELL"
    assert decoded["ship_type"] == 99
    assert decoded["to_bow"] == 90
    assert decoded["to_stern"] == 90
    assert decoded["eta_month"] == 1
    assert decoded["eta_day"] == 2
    assert decoded["draught"] == 6.0
    assert decoded["destination"] == "SEATTLE"
    assert decoded["dte"] == 0


def test_roundtrip_type18_class_b_position_report():
    payload, _ = payload6bit.encode_type_18(
        mmsi=338123456,
        sog_knots=5.4,
        lon=-70.05,
        lat=42.35,
        cog=91.0,
        heading=90,
        position_accuracy=1,
        raim=True,
    )
    decoded = payload6bit.decode_type_18(payload)
    assert decoded["msg_type"] == 18
    assert decoded["mmsi"] == 338123456
    assert decoded["sog_knots"] == 5.4
    assert abs(decoded["lat"] - 42.35) < 1e-4
    assert abs(decoded["lon"] - (-70.05)) < 1e-4
    assert decoded["cog"] == 91.0
    assert decoded["heading"] == 90
    assert decoded["position_accuracy"] == 1
    assert decoded["raim"] is True


def test_roundtrip_type18_default_unavailable_values():
    """Sem argumentos alem do mmsi, os defaults devem ser os valores
    padronizados de 'campo nao disponivel' do AIS, nao zero."""
    payload, _ = payload6bit.encode_type_18(mmsi=338123456)
    decoded = payload6bit.decode_type_18(payload)
    assert decoded["sog_knots"] == 102.3
    assert decoded["lon"] == 181.0
    assert decoded["lat"] == 91.0
    assert decoded["cog"] == 360.0
    assert decoded["heading"] == 511


def test_roundtrip_type19_extended_class_b():
    payload, _ = payload6bit.encode_type_19(
        mmsi=338123456,
        sog_knots=5.4,
        lon=-70.05,
        lat=42.35,
        cog=91.0,
        heading=90,
        name="SAILAWAY",
        ship_type=36,
        to_bow=8, to_stern=2, to_port=2, to_starboard=2,
        epfd=1,
        raim=True,
        dte=0,
        assigned=1,
    )
    decoded = payload6bit.decode_type_19(payload)
    assert decoded["msg_type"] == 19
    assert decoded["mmsi"] == 338123456
    assert decoded["name"] == "SAILAWAY"
    assert decoded["ship_type"] == 36
    assert decoded["to_bow"] == 8
    assert decoded["to_stern"] == 2
    assert decoded["raim"] is True
    assert decoded["dte"] == 0
    assert decoded["assigned"] == 1


def test_roundtrip_type24_part_a_name_only():
    payload, _ = payload6bit.encode_type_24a(mmsi=338123456, name="SAILAWAY")
    decoded = payload6bit.decode_type_24(payload)
    assert decoded["msg_type"] == 24
    assert decoded["mmsi"] == 338123456
    assert decoded["part_number"] == 0
    assert decoded["name"] == "SAILAWAY"
    assert "ship_type" not in decoded  # Part A nao carrega campos de Part B


def test_roundtrip_type24_part_b_ship_details():
    payload, _ = payload6bit.encode_type_24b(
        mmsi=338123456,
        ship_type=36,
        vendor_id="GRM",
        unit_model_code=3,
        serial_number=12345,
        callsign="KA1234",
        to_bow=8, to_stern=2, to_port=2, to_starboard=2,
        epfd=1,
    )
    decoded = payload6bit.decode_type_24(payload)
    assert decoded["part_number"] == 1
    assert decoded["ship_type"] == 36
    assert decoded["vendor_id"] == "GRM"
    assert decoded["unit_model_code"] == 3
    assert decoded["serial_number"] == 12345
    assert decoded["callsign"] == "KA1234"
    assert decoded["to_bow"] == 8
    assert decoded["epfd"] == 1


def test_type5_name_and_destination_truncate_to_field_width():
    """name (120 bits = 20 chars) e destination (idem) devem truncar
    silenciosamente textos maiores, igual receptores AIS reais fazem --
    nao e' responsabilidade do encoder validar tamanho, e' comportamento
    de protocolo."""
    payload, _ = payload6bit.encode_type_5(
        mmsi=1,
        name="A" * 30,
        destination="B" * 30,
    )
    decoded = payload6bit.decode_type_5(payload)
    assert decoded["name"] == "A" * 20
    assert decoded["destination"] == "B" * 20