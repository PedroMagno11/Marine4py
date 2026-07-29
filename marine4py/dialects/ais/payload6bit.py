"""
Decodificador do payload 6-bit "armored" carregado dentro do campo
'payload' das sentenças AIVDM/AIVDO.

Isso e um protocolo dentro do protocolo: cada caractere ASCII representa
6 bits, que juntos formam os campos BINARIOS das mensagens AIS (tipos 1
a 27). 
OBS:não tem nada a ver com o parsing por virgula do resto da
sentenca NMEA.

"""

def armor_to_bitstring(payload: str) -> str:
    """Converte o payload ASCII-armored (6 bits/caractere) numa string de '0'/'1'."""
    bits = []
    for ch in payload:
        value = ord(ch) - 48
        if value > 40:
            value -= 8
        bits.append(f"{value:06b}")
    return "".join(bits)


def get_uint(bits: str, start: int, length: int) -> int:
    return int(bits[start: start + length], 2)


def get_int(bits: str, start: int, length: int) -> int:
    value = get_uint(bits, start, length)
    if value >= 1 << (length - 1):
        value -= 1 << length
    return value


def _sixbit_char(value: int) -> str:
    # Tabela "Sixbit ASCII" do padrao AIS: 0-31 -> '@'..'_', 32-63 -> ' '..'?'
    return chr(value + 64) if value < 32 else chr(value)


def _decode_sixbit_text(bits: str, start: int, length_bits: int) -> str:
    """Decodifica texto 6-bit ASCII cru, sem cortar no '@' nem remover espacos."""
    chars = []
    for i in range(0, length_bits, 6):
        chunk = bits[start + i: start + i + 6]
        if len(chunk) < 6:
            break
        chars.append(_sixbit_char(int(chunk, 2)))
    return "".join(chars)


def get_string(bits: str, start: int, length_bits: int) -> str:
    """
    Decodifica um campo de texto 6-bit ASCII (usado em nome do navio,
    callsign, destino, etc). Por convencao do padrao, o texto termina no
    primeiro '@' (padding); qualquer coisa depois e descartada, e espacos
    a direita sao removidos (nomes curtos vem space-filled).
    """
    text = _decode_sixbit_text(bits, start, length_bits)
    at_index = text.find("@")
    if at_index != -1:
        text = text[:at_index]
    return text.strip()


def decode_type_1(payload: str) -> dict:
    """
    Position Report Class A (tipos 1, 2 e 3 compartilham o mesmo layout).
    Retorna os campos principais como dict.
    """
    bits = armor_to_bitstring(payload)
    return {
        "msg_type": get_uint(bits, 0, 6),
        "mmsi": get_uint(bits, 8, 30),
        "nav_status": get_uint(bits, 38, 4),
        "rot": get_int(bits, 42, 8),
        "sog_knots": get_uint(bits, 50, 10) / 10.0,
        "lon": get_int(bits, 61, 28) / 600000.0,
        "lat": get_int(bits, 89, 27) / 600000.0,
        "cog": get_uint(bits, 116, 12) / 10.0,
        "heading": get_uint(bits, 128, 9),
    }


def decode_type_5(payload: str) -> dict:
    """
    Static and Voyage Related Data. Mensagem de 424 bits, tipicamente
    dividida em 2 sentencas !AIVDM (ver AisAssembler para remontar antes
    de chamar esta funcao).
    """
    bits = armor_to_bitstring(payload)
    return {
        "msg_type": get_uint(bits, 0, 6),
        "mmsi": get_uint(bits, 8, 30),
        "ais_version": get_uint(bits, 38, 2),
        "imo": get_uint(bits, 40, 30),
        "callsign": get_string(bits, 70, 42),
        "name": get_string(bits, 112, 120),
        "ship_type": get_uint(bits, 232, 8),
        "to_bow": get_uint(bits, 240, 9),
        "to_stern": get_uint(bits, 249, 9),
        "to_port": get_uint(bits, 258, 6),
        "to_starboard": get_uint(bits, 264, 6),
        "epfd": get_uint(bits, 270, 4),
        "eta_month": get_uint(bits, 274, 4),
        "eta_day": get_uint(bits, 278, 5),
        "eta_hour": get_uint(bits, 283, 5),
        "eta_minute": get_uint(bits, 288, 6),
        "draught": get_uint(bits, 294, 8) / 10.0,
        "destination": get_string(bits, 302, 120),
        "dte": get_uint(bits, 422, 1),
    }


def decode_type_18(payload: str) -> dict:
    """Standard Class B CS Position Report. Mensagem de 168 bits, 1 sentenca."""
    bits = armor_to_bitstring(payload)
    return {
        "msg_type": get_uint(bits, 0, 6),
        "mmsi": get_uint(bits, 8, 30),
        "sog_knots": get_uint(bits, 46, 10) / 10.0,
        "position_accuracy": get_uint(bits, 56, 1),
        "lon": get_int(bits, 57, 28) / 600000.0,
        "lat": get_int(bits, 85, 27) / 600000.0,
        "cog": get_uint(bits, 112, 12) / 10.0,
        "heading": get_uint(bits, 124, 9),
        "second": get_uint(bits, 133, 6),
        "raim": bool(get_uint(bits, 147, 1)),
        "comm_state_selector": get_uint(bits, 148, 1),
        "comm_state": get_uint(bits, 149, 19),
    }


def decode_type_4(payload: str) -> dict:
    """Base Station Report. Estacao fixa em terra, nao e uma embarcacao."""
    bits = armor_to_bitstring(payload)
    return {
        "msg_type": get_uint(bits, 0, 6),
        "mmsi": get_uint(bits, 8, 30),
        "year": get_uint(bits, 38, 14),
        "month": get_uint(bits, 52, 4),
        "day": get_uint(bits, 56, 5),
        "hour": get_uint(bits, 61, 5),
        "minute": get_uint(bits, 66, 6),
        "second": get_uint(bits, 72, 6),
        "position_accuracy": get_uint(bits, 78, 1),
        "lon": get_int(bits, 79, 28) / 600000.0,
        "lat": get_int(bits, 107, 27) / 600000.0,
        "epfd": get_uint(bits, 134, 4),
        "raim": bool(get_uint(bits, 148, 1)),
    }


def decode_type_9(payload: str) -> dict:
    """Standard SAR Aircraft Position Report. Aeronave de busca e resgate, nao e embarcacao."""
    bits = armor_to_bitstring(payload)
    return {
        "msg_type": get_uint(bits, 0, 6),
        "mmsi": get_uint(bits, 8, 30),
        "altitude": get_uint(bits, 38, 12),
        "sog_knots": get_uint(bits, 50, 10),
        "position_accuracy": get_uint(bits, 60, 1),
        "lon": get_int(bits, 61, 28) / 600000.0,
        "lat": get_int(bits, 89, 27) / 600000.0,
        "cog": get_uint(bits, 116, 12) / 10.0,
        "second": get_uint(bits, 128, 6),
        "dte": get_uint(bits, 142, 1),
        "assigned": get_uint(bits, 146, 1),
        "raim": bool(get_uint(bits, 147, 1)),
    }


def decode_type_19(payload: str) -> dict:
    """Extended Class B CS Position Report. Mensagem de 312 bits, 1 sentenca."""
    bits = armor_to_bitstring(payload)
    return {
        "msg_type": get_uint(bits, 0, 6),
        "mmsi": get_uint(bits, 8, 30),
        "sog_knots": get_uint(bits, 46, 10) / 10.0,
        "position_accuracy": get_uint(bits, 56, 1),
        "lon": get_int(bits, 57, 28) / 600000.0,
        "lat": get_int(bits, 85, 27) / 600000.0,
        "cog": get_uint(bits, 112, 12) / 10.0,
        "heading": get_uint(bits, 124, 9),
        "second": get_uint(bits, 133, 6),
        "name": get_string(bits, 143, 120),
        "ship_type": get_uint(bits, 263, 8),
        "to_bow": get_uint(bits, 271, 9),
        "to_stern": get_uint(bits, 280, 9),
        "to_port": get_uint(bits, 289, 6),
        "to_starboard": get_uint(bits, 295, 6),
        "epfd": get_uint(bits, 301, 4),
        "raim": bool(get_uint(bits, 305, 1)),
        "dte": get_uint(bits, 306, 1),
        "assigned": get_uint(bits, 307, 1),
    }


def decode_type_21(payload: str) -> dict:
    """
    Aid-to-Navigation Report (boias, faroletes...). O nome pode vir
    partido em dois pedacos -- os 20 caracteres do campo principal (120
    bits) mais uma extensao opcional de ate 14 caracteres (88 bits) no
    fim da mensagem, quando o nome nao coube no campo padrao. Por isso
    decodificamos os dois pedacos como texto 6-bit CRU (sem aplicar o
    corte no '@' em cada um separadamente) e so concatenamos e cortamos
    no final -- senao um '@' de padding no meio do primeiro pedaco
    truncaria o nome antes da extensao.
    """
    bits = armor_to_bitstring(payload)
    raw_name = _decode_sixbit_text(bits, 43, 120)
    if len(bits) > 272:
        extra_len = min(len(bits) - 272, 88)
        raw_name += _decode_sixbit_text(bits, 272, extra_len)
    at_index = raw_name.find("@")
    if at_index != -1:
        raw_name = raw_name[:at_index]
    name = raw_name.strip()

    return {
        "msg_type": get_uint(bits, 0, 6),
        "mmsi": get_uint(bits, 8, 30),
        "aid_type": get_uint(bits, 38, 5),
        "name": name,
        "position_accuracy": get_uint(bits, 163, 1),
        "lon": get_int(bits, 164, 28) / 600000.0,
        "lat": get_int(bits, 192, 27) / 600000.0,
        "to_bow": get_uint(bits, 219, 9),
        "to_stern": get_uint(bits, 228, 9),
        "to_port": get_uint(bits, 237, 6),
        "to_starboard": get_uint(bits, 243, 6),
        "epfd": get_uint(bits, 249, 4),
        "second": get_uint(bits, 253, 6),
        "off_position": get_uint(bits, 259, 1),
        "regional": get_uint(bits, 260, 8),
        "raim": bool(get_uint(bits, 268, 1)),
        "virtual_aid": get_uint(bits, 269, 1),
        "assigned": get_uint(bits, 270, 1),
    }


def decode_type_24(payload: str) -> dict:
    """
    Static Data Report. Unico tipo com DOIS formatos de payload sob o
    mesmo msg_type -- Part A (so nome) e Part B (ship_type/vendor_id/
    callsign/dimensoes) -- escolhidos pelo campo part_number (bits
    38-39) dentro da propria mensagem, nao pelo envelope da sentenca.
    """
    bits = armor_to_bitstring(payload)
    part_number = get_uint(bits, 38, 2)
    result = {
        "msg_type": get_uint(bits, 0, 6),
        "mmsi": get_uint(bits, 8, 30),
        "part_number": part_number,
    }
    if part_number == 0:
        result["name"] = get_string(bits, 40, 120)
    elif part_number == 1:
        result.update({
            "ship_type": get_uint(bits, 40, 8),
            # o campo "vendor ID" de 42 bits NAO e texto 6-bit puro: os
            # primeiros 18 bits sao o codigo do fabricante (3 chars),
            # os 4 seguintes um codigo de modelo, os ultimos 20 um
            # numero de serie -- por isso decodificamos em 3 pedacos,
            # nao como get_string() direto.
            "vendor_id": get_string(bits, 48, 18),
            "unit_model_code": get_uint(bits, 66, 4),
            "serial_number": get_uint(bits, 70, 20),
            "callsign": get_string(bits, 90, 42),
            "to_bow": get_uint(bits, 132, 9),
            "to_stern": get_uint(bits, 141, 9),
            "to_port": get_uint(bits, 150, 6),
            "to_starboard": get_uint(bits, 156, 6),
            "epfd": get_uint(bits, 162, 4),
        })
    else:
        raise ValueError(f"AIS tipo 24: part_number invalido: {part_number}")
    return result


VESSEL_MESSAGE_TYPES = frozenset({1, 2, 3, 5, 18, 19, 24})
INFRASTRUCTURE_MESSAGE_TYPES = frozenset({4, 9, 21})


DECODERS = {
    1: decode_type_1,
    2: decode_type_1,
    3: decode_type_1,
    4: decode_type_4,
    5: decode_type_5,
    9: decode_type_9,
    18: decode_type_18,
    19: decode_type_19,
    21: decode_type_21,
    24: decode_type_24,
}


def decode(payload: str) -> dict:
    """Detecta o msg_type (primeiros 6 bits) e despacha pro decoder certo."""
    bits = armor_to_bitstring(payload)
    msg_type = get_uint(bits, 0, 6)
    decoder = DECODERS.get(msg_type)
    if decoder is None:
        raise NotImplementedError(
            f"decoder para AIS msg_type {msg_type} ainda nao implementado"
        )
    return decoder(payload)
