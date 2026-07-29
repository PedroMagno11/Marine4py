from marine4py.core.checksum import XorChecksum
from marine4py.core.field import Field, IntField, StringField
from marine4py.core.framing import FramingStrategy
from marine4py.core.nmea import NMEASentence
from marine4py.core.registry import REGISTRY


AIS_FRAMING = FramingStrategy(
    start="!",
    field_sep=",",
    checksum_sep="*",
    checksum_strategy=XorChecksum(),
    line_end="\r\n",
    talker_len=2,
)
REGISTRY.set_framing("ais", AIS_FRAMING)


def _optional_int(raw):
    return int(raw) if raw else None


class AISSentence(NMEASentence):
    dialect = "ais"
    framing = AIS_FRAMING


class VDM(AISSentence):
    """Mensagem AIS recebida de outra estacao/embarcacao."""
    sentence_id = "VDM"
    fields = (
        IntField("Total Fragments", "frag_count"),
        IntField("Fragment Number", "frag_number"),
        Field("Sequential Message ID", "seq_id", parse=_optional_int, render=lambda v: "" if v is None else str(v)),
        StringField("Radio Channel", "channel"),
        StringField("Payload (6-bit armored)", "payload"),
        IntField("Fill Bits", "fill_bits"),
    )


class VDO(VDM):
    """Mensagem AIS transmitida pelo proprio navio (own-ship)."""
    sentence_id = "VDO"
