"""
Sentenças padrão de GPS ($GPxxx, $GNxxx, etc).
"""

from marine4py.core.checksum import XorChecksum
from marine4py.core.field import Field, FloatField, IntField, StringField
from marine4py.core.framing import FramingStrategy
from marine4py.core.nmea import NMEASentence
from marine4py.core.registry import REGISTRY
from marine4py.dialects.utils import dm_to_decimal, parse_date, parse_time, render_date, render_time


GPS_FRAMING = FramingStrategy(
    start="$",
    field_sep=",",
    checksum_sep="*",
    checksum_strategy=XorChecksum(),
    line_end="\r\n",
    talker_len=2,
)

REGISTRY.set_framing("gps", GPS_FRAMING)

class LatLonMixin:
    """Expoe latitude/longitude como float (graus decimais), a partir dos campos crus."""

    @property
    def latitude(self):
        return dm_to_decimal(self.lat, self.lat_dir) if getattr(self, "lat", None) else None

    @property
    def longitude(self):
        return dm_to_decimal(self.lon, self.lon_dir) if getattr(self, "lon", None) else None


class GPSSentence(NMEASentence):
    dialect = "gps"
    framing = GPS_FRAMING


class GGA(GPSSentence, LatLonMixin):
    """Global Positioning System Fix Data."""
    sentence_id = "GGA"
    fields = (
        Field("Timestamp", "timestamp", parse=parse_time, render=render_time),
        StringField("Latitude", "lat"),
        StringField("Latitude Direction", "lat_dir"),
        StringField("Longitude", "lon"),
        StringField("Longitude Direction", "lon_dir"),
        IntField("GPS Quality Indicator", "gps_qual"),
        IntField("Number of Satellites", "num_sats"),
        FloatField("Horizontal Dilution of Precision", "horizontal_dil"),
        FloatField("Antenna Altitude", "altitude"),
        StringField("Altitude Units", "altitude_units"),
        FloatField("Geoidal Separation", "geo_sep"),
        StringField("Geoidal Separation Units", "geo_sep_units"),
        StringField("Age of GPS Data", "age_gps_data"),
        StringField("Reference Station ID", "ref_station_id"),
    )


class RMC(GPSSentence, LatLonMixin):
    """Recommended Minimum Navigation Information."""
    sentence_id = "RMC"
    fields = (
        Field("Timestamp", "timestamp", parse=parse_time, render=render_time),
        StringField("Status", "status", required=True, choices=("A", "V")),
        StringField("Latitude", "lat"),
        StringField("Latitude Direction", "lat_dir"),
        StringField("Longitude", "lon"),
        StringField("Longitude Direction", "lon_dir"),
        FloatField("Speed over Ground", "spd_over_grnd"),
        FloatField("True Course", "true_course"),
        Field("Datestamp", "datestamp", parse=parse_date, render=render_date),
        StringField("Magnetic Variation", "mag_variation"),
        StringField("Magnetic Variation Direction", "mag_var_dir"),
    )


class VTG(GPSSentence):
    """Track made good and Ground speed."""
    sentence_id = "VTG"
    fields = (
        FloatField("True Track", "true_track"),
        StringField("True Track Symbol", "true_track_sym"),
        FloatField("Magnetic Track", "mag_track"),
        StringField("Magnetic Track Symbol", "mag_track_sym"),
        FloatField("Speed (knots)", "spd_over_grnd_kts"),
        StringField("Speed Knots Symbol", "spd_over_grnd_kts_sym"),
        FloatField("Speed (km/h)", "spd_over_grnd_kmph"),
        StringField("Speed Km/h Symbol", "spd_over_grnd_kmph_sym"),
    )
class GSA(GPSSentence):
    """GPS DOP and active satellites."""
    sentence_id = "GSA"
    fields = (
        StringField("Selection Mode", "mode_selection", choices=("A", "M")),
        IntField("Fix Mode", "mode_fix_type", required=True, choices=(1, 2, 3)),
        StringField("Satellite 1 PRN", "sv_id01"),
        StringField("Satellite 2 PRN", "sv_id02"),
        StringField("Satellite 3 PRN", "sv_id03"),
        StringField("Satellite 4 PRN", "sv_id04"),
        StringField("Satellite 5 PRN", "sv_id05"),
        StringField("Satellite 6 PRN", "sv_id06"),
        StringField("Satellite 7 PRN", "sv_id07"),
        StringField("Satellite 8 PRN", "sv_id08"),
        StringField("Satellite 9 PRN", "sv_id09"),
        StringField("Satellite 10 PRN", "sv_id10"),
        StringField("Satellite 11 PRN", "sv_id11"),
        StringField("Satellite 12 PRN", "sv_id12"),
        FloatField("PDOP", "pdop"),
        FloatField("HDOP", "hdop"),
        FloatField("VDOP", "vdop"),
    )


class GSV(GPSSentence):
    """
    Satellites in view. Cada sentenca GSV descreve ate 4 satelites; quando
    ha mais satelites visiveis do que isso, o receptor manda varias
    sentencas GSV em sequencia (ver total_num_msgs/msg_num). v1 modela os
    4 slots como campos opcionais -- se a sentenca trouxer menos, os
    excedentes ficam None.
    """
    sentence_id = "GSV"
    fields = (
        IntField("Total Number of Messages", "total_num_msgs", required=True),
        IntField("Message Number", "msg_num", required=True),
        IntField("Satellites in View", "num_sv_in_view", required=True),
        IntField("Satellite 1 PRN", "sv_prn_num_1"),
        IntField("Satellite 1 Elevation", "elevation_deg_1"),
        IntField("Satellite 1 Azimuth", "azimuth_1"),
        IntField("Satellite 1 SNR", "snr_1"),
        IntField("Satellite 2 PRN", "sv_prn_num_2"),
        IntField("Satellite 2 Elevation", "elevation_deg_2"),
        IntField("Satellite 2 Azimuth", "azimuth_2"),
        IntField("Satellite 2 SNR", "snr_2"),
        IntField("Satellite 3 PRN", "sv_prn_num_3"),
        IntField("Satellite 3 Elevation", "elevation_deg_3"),
        IntField("Satellite 3 Azimuth", "azimuth_3"),
        IntField("Satellite 3 SNR", "snr_3"),
        IntField("Satellite 4 PRN", "sv_prn_num_4"),
        IntField("Satellite 4 Elevation", "elevation_deg_4"),
        IntField("Satellite 4 Azimuth", "azimuth_4"),
        IntField("Satellite 4 SNR", "snr_4"),
    )


class ZDA(GPSSentence):
    """Time & Date - UTC, Day, Month, Year and Local Time Zone."""
    sentence_id = "ZDA"
    fields = (
        Field("Timestamp", "timestamp", parse=parse_time, render=render_time, required=True),
        IntField("Day", "day", required=True, validate=lambda v: 1 <= v <= 31),
        IntField("Month", "month", required=True, validate=lambda v: 1 <= v <= 12),
        IntField("Year", "year", required=True),
        IntField("Local Zone Hours", "local_zone"),
        IntField("Local Zone Minutes", "local_zone_minutes"),
    )


class GLL(GPSSentence, LatLonMixin):
    """Geographic Position - Latitude/Longitude."""
    sentence_id = "GLL"
    fields = (
        StringField("Latitude", "lat"),
        StringField("Latitude Direction", "lat_dir"),
        StringField("Longitude", "lon"),
        StringField("Longitude Direction", "lon_dir"),
        Field("Timestamp", "timestamp", parse=parse_time, render=render_time),
        StringField("Status", "status", required=True, choices=("A", "V")),
    )


class HDT(GPSSentence):
    """Heading - True."""
    sentence_id = "HDT"
    fields = (
        FloatField("Heading Degrees True", "heading", required=True),
        StringField("True Indicator", "true_indicator", choices=("T",)),
    )
