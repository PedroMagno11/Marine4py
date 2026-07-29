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


def bitstring_to_armor(bits: str):
    """
    Converte uma string de '0'/'1' de volta
    para o payload ASCII-armored (6 bits/caractere).
 
    Se o comprimento de `bits` nao for multiplo de 6, o ultimo caractere e
    completado com zeros a direita (fill bits) -- por isso a funcao retorna
    tambem quantos bits de preenchimento foram usados, que e exatamente o
    valor que vai no campo "Fill Bits" da sentenca VDM/VDO.
 
    Retorna (payload_armored, fill_bits).
    """
    fill_bits = (6 - len(bits) % 6) % 6
    padded = bits + ("0" * fill_bits)
 
    chars = []
    for i in range(0, len(padded), 6):
        value = int(padded[i: i + 6], 2)
        # exato inverso do "if value > 40: value -= 8" do armor_to_bitstring
        chars.append(chr(value + 48) if value <= 40 else chr(value + 56))
    return "".join(chars), fill_bits


def get_uint(bits: str, start: int, length: int) -> int:
    return int(bits[start: start + length], 2)

def put_uint(bits: list, start: int, length: int, value: int) -> None:
    """
    Escreve `value` (unsigned ou signed -- numeros negativos sao gravados em
    complemento de dois, exatamente como get_int() os interpreta na leitura)
    em `bits` -- uma lista mutavel de caracteres '0'/'1' -- na posicao
    [start:start+length].
    """
    value &= (1 << length) - 1  
    bits[start: start + length] = list(f"{value:0{length}b}")

def _sixbit_value(ch: str) -> int:
    # Inverso de _sixbit_char(): '@'-'_' (ord 64-95) -> 0-31, ' '-'?' (ord 32-63) -> 32-63
    o = ord(ch)
    if 64 <= o <= 95:
        return o - 64
    if 32 <= o <= 63:
        return o
    raise ValueError(f"caractere {ch!r} fora da tabela 6-bit ASCII do AIS")

def put_string(bits: list, start: int, length_bits: int, text: str) -> None:
    """
    Escreve `text` como um campo 6-bit ASCII (nome do navio, callsign,
    destino, vendor_id...) -- inverso de get_string(). O texto e' truncado
    ou completado a direita com '@' (padding) ate preencher `length_bits`
    exatamente, igual os receptores AIS reais fazem.
    """
    n_chars = length_bits // 6
    text = text.upper()[:n_chars].ljust(n_chars, "@")
    for i, ch in enumerate(text):
        put_uint(bits, start + i * 6, 6, _sixbit_value(ch))

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


def encode_type_1(
    mmsi: int,
    msg_type: int = 1,
    nav_status: int = 15,        # 15 = "not defined" (default do padrao)
    rot: int = -128,             # -128 = "nao disponivel"
    sog_knots: float = 102.3,    # 102.3 = "nao disponivel"
    lon: float = 181.0,          # 181.0 = "nao disponivel"
    lat: float = 91.0,           # 91.0 = "nao disponivel"
    cog: float = 360.0,          # 360.0 = "nao disponivel"
    heading: int = 511,          # 511 = "nao disponivel"
) -> tuple:
    """
    Monta o payload 6-bit armored de uma Position Report Class A (tipos 1/2/3)
    a partir de campos estruturados -- e o inverso de decode_type_1().
 
    Os defaults sao os valores de "campo nao disponivel" definidos pelo
    proprio padrao AIS para cada campo (nao zero), entao quem so quer
    reportar posicao e velocidade pode omitir o resto sem gerar dado
    fisicamente incorreto (heading=0 pareceria "rumo norte", por exemplo).
 
    Retorna (payload_armored, fill_bits) -- prontos para virar os campos
    `payload` e `fill_bits` de uma sentenca VDM/VDO.
    """
    bits = ["0"] * 168
    put_uint(bits, 0, 6, msg_type)
    put_uint(bits, 6, 2, 0)                          # repeat indicator
    put_uint(bits, 8, 30, mmsi)
    put_uint(bits, 38, 4, nav_status)
    put_uint(bits, 42, 8, rot)
    put_uint(bits, 50, 10, round(sog_knots * 10))
    put_uint(bits, 60, 1, 0)                         # position accuracy
    put_uint(bits, 61, 28, round(lon * 600000))
    put_uint(bits, 89, 27, round(lat * 600000))
    put_uint(bits, 116, 12, round(cog * 10))
    put_uint(bits, 128, 9, heading)
    # 137-142 timestamp(seg), 143-144 maneuver, 145-147 spare, 148 raim,
    # 149-167 comm state: ficam no default "0" -- suficiente para round-trip
    # de posicao/velocidade/rumo, que e o que decode_type_1 expoe.
    return bitstring_to_armor("".join(bits))


def encode_type_5(
    mmsi: int,
    imo: int = 0,
    callsign: str = "",
    name: str = "",
    ship_type: int = 0,
    to_bow: int = 0,
    to_stern: int = 0,
    to_port: int = 0,
    to_starboard: int = 0,
    epfd: int = 0,
    eta_month: int = 0,     # 0 = "nao disponivel"
    eta_day: int = 0,       # 0 = "nao disponivel"
    eta_hour: int = 24,     # 24 = "nao disponivel"
    eta_minute: int = 60,   # 60 = "nao disponivel"
    draught: float = 0.0,
    destination: str = "",
    dte: int = 1,           # 1 = "dado nao disponivel/nao confiavel" (default do padrao)
    ais_version: int = 0,
) -> tuple:
    """
    Monta o payload de uma Static and Voyage Related Data (tipo 5) --
    inverso de decode_type_5(). Mensagem de 424 bits: em enlaces reais ela
    quase sempre precisa ser fragmentada em 2 sentencas !AIVDM (ver
    AisAssembler do lado do decode; aqui quem particiona o `payload`
    resultante em 2 campos de sentenca e' responsabilidade de quem monta o
    envelope NMEA, nao desta funcao).
 
    Retorna (payload_armored, fill_bits).
    """
    bits = ["0"] * 424
    put_uint(bits, 0, 6, 5)
    put_uint(bits, 6, 2, 0)                 # repeat indicator
    put_uint(bits, 8, 30, mmsi)
    put_uint(bits, 38, 2, ais_version)
    put_uint(bits, 40, 30, imo)
    put_string(bits, 70, 42, callsign)
    put_string(bits, 112, 120, name)
    put_uint(bits, 232, 8, ship_type)
    put_uint(bits, 240, 9, to_bow)
    put_uint(bits, 249, 9, to_stern)
    put_uint(bits, 258, 6, to_port)
    put_uint(bits, 264, 6, to_starboard)
    put_uint(bits, 270, 4, epfd)
    put_uint(bits, 274, 4, eta_month)
    put_uint(bits, 278, 5, eta_day)
    put_uint(bits, 283, 5, eta_hour)
    put_uint(bits, 288, 6, eta_minute)
    put_uint(bits, 294, 8, round(draught * 10))
    put_string(bits, 302, 120, destination)
    put_uint(bits, 422, 1, dte)
    # bit 423: spare -- fica 0
    return bitstring_to_armor("".join(bits))
 
 
def encode_type_18(
    mmsi: int,
    sog_knots: float = 102.3,
    lon: float = 181.0,
    lat: float = 91.0,
    cog: float = 360.0,
    heading: int = 511,
    position_accuracy: int = 0,
    raim: bool = False,
) -> tuple:
    """
    Monta o payload de uma Standard Class B CS Position Report (tipo 18) --
    inverso de decode_type_18(). Mensagem de 168 bits, sempre em 1 sentenca.
 
    Retorna (payload_armored, fill_bits).
    """
    bits = ["0"] * 168
    put_uint(bits, 0, 6, 18)
    put_uint(bits, 6, 2, 0)                 # repeat indicator
    put_uint(bits, 8, 30, mmsi)
    # bits 38-45: reserved (nao decodificado) -- fica 0
    put_uint(bits, 46, 10, round(sog_knots * 10))
    put_uint(bits, 56, 1, position_accuracy)
    put_uint(bits, 57, 28, round(lon * 600000))
    put_uint(bits, 85, 27, round(lat * 600000))
    put_uint(bits, 112, 12, round(cog * 10))
    put_uint(bits, 124, 9, heading)
    # bits 133-147: second/flags de Class B (nao decodificados) -- ficam 0
    put_uint(bits, 147, 1, int(raim))
    return bitstring_to_armor("".join(bits))
 
 
def encode_type_19(
    mmsi: int,
    sog_knots: float = 102.3,
    lon: float = 181.0,
    lat: float = 91.0,
    cog: float = 360.0,
    heading: int = 511,
    name: str = "",
    ship_type: int = 0,
    to_bow: int = 0,
    to_stern: int = 0,
    to_port: int = 0,
    to_starboard: int = 0,
    epfd: int = 0,
    position_accuracy: int = 0,
    raim: bool = False,
    dte: int = 1,
    assigned: int = 0,
) -> tuple:
    """
    Monta o payload de uma Extended Class B CS Position Report (tipo 19) --
    inverso de decode_type_19(). Mensagem de 312 bits, sempre em 1 sentenca
    -- e' o tipo 18 "fundido" com a identificacao estatica que no Class A
    vem separada (tipo 5).
 
    Retorna (payload_armored, fill_bits).
    """
    bits = ["0"] * 312
    put_uint(bits, 0, 6, 19)
    put_uint(bits, 6, 2, 0)                 # repeat indicator
    put_uint(bits, 8, 30, mmsi)
    # bits 38-45: reserved -- fica 0
    put_uint(bits, 46, 10, round(sog_knots * 10))
    put_uint(bits, 56, 1, position_accuracy)
    put_uint(bits, 57, 28, round(lon * 600000))
    put_uint(bits, 85, 27, round(lat * 600000))
    put_uint(bits, 112, 12, round(cog * 10))
    put_uint(bits, 124, 9, heading)
    # bits 133-142: second/regional reserved -- ficam 0
    put_string(bits, 143, 120, name)
    put_uint(bits, 263, 8, ship_type)
    put_uint(bits, 271, 9, to_bow)
    put_uint(bits, 280, 9, to_stern)
    put_uint(bits, 289, 6, to_port)
    put_uint(bits, 295, 6, to_starboard)
    put_uint(bits, 301, 4, epfd)
    put_uint(bits, 305, 1, int(raim))
    put_uint(bits, 306, 1, dte)
    put_uint(bits, 307, 1, assigned)
    return bitstring_to_armor("".join(bits))
 
 
def encode_type_24a(mmsi: int, name: str = "") -> tuple:
    """
    Monta a Part A (part_number=0) de uma Static Data Report (tipo 24) --
    so o nome. Navios Class B mandam Part A e Part B (encode_type_24b) como
    DUAS sentencas !AIVDM separadas de fragmento unico cada -- diferente do
    tipo 5, aqui NAO e' fragmentacao (frag_count/frag_number continuam 1/1
    em ambas): e' o proprio msg_type 24 que tem dois formatos de corpo,
    diferenciados por part_number dentro do payload.
 
    Retorna (payload_armored, fill_bits).
    """
    bits = ["0"] * 160
    put_uint(bits, 0, 6, 24)
    put_uint(bits, 6, 2, 0)                 # repeat indicator
    put_uint(bits, 8, 30, mmsi)
    put_uint(bits, 38, 2, 0)                # part_number = 0 (Part A)
    put_string(bits, 40, 120, name)
    return bitstring_to_armor("".join(bits))
 
 
def encode_type_24b(
    mmsi: int,
    ship_type: int = 0,
    vendor_id: str = "",
    unit_model_code: int = 0,
    serial_number: int = 0,
    callsign: str = "",
    to_bow: int = 0,
    to_stern: int = 0,
    to_port: int = 0,
    to_starboard: int = 0,
    epfd: int = 0,
) -> tuple:
    """
    Monta a Part B (part_number=1) de uma Static Data Report (tipo 24) --
    ship_type/vendor/callsign/dimensoes. Ver docstring de encode_type_24a
    sobre a relacao entre Part A e Part B.
 
    Retorna (payload_armored, fill_bits).
    """
    bits = ["0"] * 168
    put_uint(bits, 0, 6, 24)
    put_uint(bits, 6, 2, 0)                 # repeat indicator
    put_uint(bits, 8, 30, mmsi)
    put_uint(bits, 38, 2, 1)                # part_number = 1 (Part B)
    put_uint(bits, 40, 8, ship_type)
    put_string(bits, 48, 18, vendor_id)
    put_uint(bits, 66, 4, unit_model_code)
    put_uint(bits, 70, 20, serial_number)
    put_string(bits, 90, 42, callsign)
    put_uint(bits, 132, 9, to_bow)
    put_uint(bits, 141, 9, to_stern)
    put_uint(bits, 150, 6, to_port)
    put_uint(bits, 156, 6, to_starboard)
    put_uint(bits, 162, 4, epfd)
    return bitstring_to_armor("".join(bits))

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
