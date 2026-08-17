from marine4py.core.checksum import XorChecksum
from marine4py.core.framing import FramingStrategy
from marine4py.core.nmea import NMEASentence
from marine4py.core.registry import REGISTRY


NMEA_FRAMING = FramingStrategy(
    start="$",
    field_sep=",",
    checksum_sep="*",
    checksum_strategy=XorChecksum(),
    line_end="\r\n",
    talker_len=2,
)

REGISTRY.set_framing("nmea", NMEA_FRAMING)

class DefaultSentence(NMEASentence):
    dialect = "nmea"
    framing = NMEA_FRAMING