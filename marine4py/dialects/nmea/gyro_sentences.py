"""
Sentencas de giroscopio ($HExxx, $HCxxx, $HNxxx).
"""

from marine4py.core.field import FloatField, StringField
from marine4py.dialects.nmea.nmea_common import DefaultSentence


class HDG(DefaultSentence):
    sentence_id = "HDG"
    fields = (
        FloatField("Magnetic Sensor Heading", "heading", required=True),
        FloatField("Magnetic Deviation", "deviation"),
        StringField("Magnetic Deviation Direction", "deviation_dir", choices=("E", "W")),
        FloatField("Magnetic Variation", "variation"),
        StringField("Magnetic Variation Direction", "variation_dir", choices=("E", "W")),
    )

    @property
    def true_heading(self):
        if self.heading is None:
            return None
        total = self.heading
        if self.deviation is not None:
            total += self.deviation if self.deviation_dir == "E" else -self.deviation
        if self.variation is not None:
            total += self.variation if self.variation_dir == "E" else -self.variation
        return total % 360


class ROT(DefaultSentence):
    sentence_id = "ROT"
    fields = (
        FloatField("Rate of Turn", "rate"),
        StringField("Status", "status", required=True, choices=("A", "V")),
    )