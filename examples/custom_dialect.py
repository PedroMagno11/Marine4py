from marine4py.core.checksum import XorChecksum
from marine4py.core.field import Field, FloatField, StringField
from marine4py.core.framing import FramingStrategy
from marine4py.core.nmea import NMEASentence
from marine4py.core.registry import REGISTRY


MEU_FRAMING = FramingStrategy(
    start="@",
    field_sep="|",
    checksum_sep="*",
    checksum_strategy=XorChecksum(),
    line_end="\n",
    talker_len=0,  # este protocolo nao tem conceito de "talker"
)
REGISTRY.set_framing("meu_protocolo", MEU_FRAMING)


class MeuProtocoloSentence(NMEASentence):
    dialect = "meu_protocolo"
    framing = MEU_FRAMING


# 2. Declare suas sentencas normalmente
class TLM(MeuProtocoloSentence):
    """Telemetria ficticia: timestamp epoch | bateria % | status."""
    sentence_id = "TLM"
    fields = (
        Field("Timestamp", "timestamp", parse=int, render=str),
        FloatField("Bateria", "battery"),
        StringField("Status", "status"),
    )


if __name__ == "__main__":
    msg = TLM(sentence_id="TLM", data=("1732000000", "87.5", "OK"))
    raw = str(msg)
    print("gerado  :", raw.strip())

    parsed = NMEASentence.parse(raw, dialect="meu_protocolo")
    print("parseado:", repr(parsed))
    assert parsed.battery == 87.5
    assert parsed.status == "OK"
    print("round-trip OK")
