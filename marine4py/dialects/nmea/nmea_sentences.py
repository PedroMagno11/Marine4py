"""
Sentenças padrão NMEA.
"""

from marine4py.core.field import FloatField, StringField
from marine4py.dialects.nmea.nmea_common import DefaultSentence
from marine4py.dialects.utils import DepthMixin


class DBT(DefaultSentence, DepthMixin):
    """Depth Below Transducer."""
    sentence_id = "DBT"
    fields = (
        FloatField("Depth Feet", "depth_feet"),
        StringField("Feet Indicator", "feet_indicator", choices=("f",)),
        FloatField("Depth Meters", "depth_meters"),
        StringField("Meters Indicator", "meters_indicator", choices=("M",)),
        FloatField("Depth Fathoms", "depth_fathoms"),
        StringField("Fathoms Indicator", "fathoms_indicator", choices=("F",)),
    )
 
 
class DBK(DefaultSentence, DepthMixin):
    """Depth Below Keel."""
    sentence_id = "DBK"
    fields = (
        FloatField("Depth Feet", "depth_feet"),
        StringField("Feet Indicator", "feet_indicator", choices=("f",)),
        FloatField("Depth Meters", "depth_meters"),
        StringField("Meters Indicator", "meters_indicator", choices=("M",)),
        FloatField("Depth Fathoms", "depth_fathoms"),
        StringField("Fathoms Indicator", "fathoms_indicator", choices=("F",)),
    )
 
 
class DBS(DefaultSentence, DepthMixin):
    """Depth Below Surface."""
    sentence_id = "DBS"
    fields = (
        FloatField("Depth Feet", "depth_feet"),
        StringField("Feet Indicator", "feet_indicator", choices=("f",)),
        FloatField("Depth Meters", "depth_meters"),
        StringField("Meters Indicator", "meters_indicator", choices=("M",)),
        FloatField("Depth Fathoms", "depth_fathoms"),
        StringField("Fathoms Indicator", "fathoms_indicator", choices=("F",)),
    )
 
 
class DPT(DefaultSentence, DepthMixin):
    """Depth of Water (transdutor -> fundo, + offset p/ quilha ou linha d'agua)."""
    sentence_id = "DPT"
    fields = (
        FloatField("Depth Meters", "depth_meters", required=True),
        FloatField("Transducer Offset", "offset"),
    )
 
 
class MTW(DefaultSentence):
    """Water Temperature."""
    sentence_id = "MTW"
    fields = (
        FloatField("Temperature", "temperature", required=True),
        StringField("Unit", "unit", choices=("C",)),
    )