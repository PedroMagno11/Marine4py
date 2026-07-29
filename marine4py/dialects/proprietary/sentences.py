import re

from marine4py.core.checksum import XorChecksum
from marine4py.core.field import Field, FloatField, IntField, StringField
from marine4py.core.framing import FramingStrategy
from marine4py.core.nmea import NMEASentence
from marine4py.core.registry import REGISTRY
from marine4py.dialects.utils import dm_to_decimal, parse_date, parse_time, render_date, render_time


PROPRIETARY_FRAMING = FramingStrategy(
    start="$",
    field_sep=",",
    checksum_sep="*",
    checksum_strategy=XorChecksum(),
    line_end="\r\n",
    talker_len=1, 
)
REGISTRY.set_framing("proprietary", PROPRIETARY_FRAMING)


class LatLonMixin:
    """Expoe latitude/longitude como float (graus decimais), a partir dos campos crus."""

    @property
    def latitude(self):
        return dm_to_decimal(self.lat, self.lat_dir) if getattr(self, "lat", None) else None

    @property
    def longitude(self):
        return dm_to_decimal(self.lon, self.lon_dir) if getattr(self, "lon", None) else None


class GRMSentence(NMEASentence):
    dialect = "proprietary"
    framing = PROPRIETARY_FRAMING


class GRME(GRMSentence):
    """$PGRME - Garmin: Estimated Position Error."""
    sentence_id = "GRME"
    fields = (
        FloatField("Estimated Horizontal Position Error", "hpe"),
        StringField("HPE Unit", "hpe_unit", choices=("M",)),
        FloatField("Estimated Vertical Error", "vpe"),
        StringField("VPE Unit", "vpe_unit", choices=("M",)),
        FloatField("Overall Spherical Equivalent Position Error", "osepe"),
        StringField("OSEPE Unit", "osepe_unit", choices=("M",)),
    )


class GRMZ(GRMSentence):
    """$PGRMZ - Garmin: Altitude Information."""
    sentence_id = "GRMZ"
    fields = (
        FloatField("Altitude", "altitude"),
        StringField("Altitude Unit", "altitude_unit", choices=("f",)),
        IntField("Position Fix Dimensions", "fix_dimension", choices=(2, 3)),
    )


class GRMV(GRMSentence):
    """$PGRMV - Garmin: 3D Velocity."""
    sentence_id = "GRMV"
    fields = (
        FloatField("True East Velocity", "east_velocity"),
        FloatField("True North Velocity", "north_velocity"),
        FloatField("Up Velocity", "up_velocity"),
    )


class GRMM(GRMSentence):
    """$PGRMM - Garmin: Map Datum."""
    sentence_id = "GRMM"
    fields = (
        StringField("Currently Active Datum", "datum"),
    )


class GRMW(GRMSentence):
    """$PGRMW - Garmin: Waypoint Information."""
    sentence_id = "GRMW"
    fields = (
        StringField("Waypoint Name", "wname"),
        FloatField("Altitude", "altitude"),
        StringField("Symbol", "symbol"),
        StringField("Comment", "comment"),
    )


class RDID(NMEASentence):
    """$PRDID - RD Instruments: heading, pitch e roll (DVL)."""
    dialect = "proprietary"
    framing = PROPRIETARY_FRAMING
    sentence_id = "RDID"
    fields = (
        FloatField("Pitch", "pitch"),
        FloatField("Roll", "roll"),
        FloatField("Heading", "heading"),
    )


class SRF103(NMEASentence):
    """$PSRF103 - SiRF: liga/desliga um tipo de sentenca NMEA e sua taxa."""
    dialect = "proprietary"
    framing = PROPRIETARY_FRAMING
    sentence_id = "SRF103"
    fields = (
        StringField("Sentence Type", "sentence"),  # 00=GGA 01=GLL 02=GSA 03=GSV 04=RMC 05=VTG
        IntField("Command", "command"),             # 0=Set 1=Query
        IntField("Rate", "rate"),
        IntField("Checksum Enabled", "checksum"),   # 0=No 1=Yes
    )


class MGNWPL(NMEASentence, LatLonMixin):
    """$PMGNWPL - Magellan: Waypoint Location."""
    dialect = "proprietary"
    framing = PROPRIETARY_FRAMING
    sentence_id = "MGNWPL"
    fields = (
        StringField("Latitude", "lat"),
        StringField("Latitude Direction", "lat_dir"),
        StringField("Longitude", "lon"),
        StringField("Longitude Direction", "lon_dir"),
        FloatField("Altitude", "altitude"),
        StringField("Altitude Unit", "altitude_unit", choices=("M", "F")),
        StringField("Waypoint Name", "wname"),
        StringField("Comment", "comment"),
        StringField("Icon", "icon"),
        StringField("Waypoint Type", "type"),
    )


class KWDWPL(NMEASentence, LatLonMixin):
    """$PKWDWPL - Kenwood: Waypoint Location (transceptores TM-D710A e similares)."""
    dialect = "proprietary"
    framing = PROPRIETARY_FRAMING
    sentence_id = "KWDWPL"
    fields = (
        Field("Time of Receipt", "timestamp", parse=parse_time, render=render_time),
        StringField("GPS Status", "status", choices=("A", "V")),
        StringField("Latitude", "lat"),
        StringField("Latitude Direction", "lat_dir"),
        StringField("Longitude", "lon"),
        StringField("Longitude Direction", "lon_dir"),
        FloatField("Speed over Ground", "sog"),
        FloatField("Course over Ground", "cog"),
        Field("Date", "datestamp", parse=parse_date, render=render_date),
        FloatField("Altitude", "altitude"),
        StringField("Waypoint Name", "wname"),
        StringField("Table and Symbol", "ts"),
    )


class NORBT0(NMEASentence):
    """$PNORBT0 - Nortek DVL: Bottom Track (formato ASCII 0/1)."""
    dialect = "proprietary"
    framing = PROPRIETARY_FRAMING
    sentence_id = "NORBT0"
    fields = (
        IntField("Beam Number", "beam"),
        Field("Date", "datestamp", parse=parse_date, render=render_date),
        Field("Time", "timestamp", parse=parse_time, render=render_time),
        FloatField("Time (Trigger)", "dt1"),
        FloatField("Time (NMEA)", "dt2"),
        FloatField("Beam Velocity", "bv"),
        FloatField("Figure of Merit", "fom"),
        FloatField("Vertical Distance", "dist"),
        StringField("Status", "stat"),
    )


class NORC1(NMEASentence):
    """$PNORC1 - Nortek DVL: Current Data (formato ASCII 1/2)."""
    dialect = "proprietary"
    framing = PROPRIETARY_FRAMING
    sentence_id = "NORC1"
    fields = (
        Field("Date", "datestamp", parse=parse_date, render=render_date),
        Field("Time", "timestamp", parse=parse_time, render=render_time),
        IntField("Cell Number", "cn"),
        FloatField("Cell Position", "cp"),
        FloatField("Velocity X", "vx"),
        FloatField("Velocity Y", "vy"),
        FloatField("Velocity Z", "vz"),
        FloatField("Velocity Z2", "vz2"),
        FloatField("Amplitude Beam 1", "amp1"),
        FloatField("Amplitude Beam 2", "amp2"),
        FloatField("Amplitude Beam 3", "amp3"),
        FloatField("Amplitude Beam 4", "amp4"),
        IntField("Correlation Beam 1", "r1"),
        IntField("Correlation Beam 2", "r2"),
        IntField("Correlation Beam 3", "r3"),
        IntField("Correlation Beam 4", "r4"),
        IntField("Correlation Beam 5", "r5"),
    )


class SubtypedManufacturerSentence(NMEASentence):
    """
    Base para fabricantes cujo formato NAO cola o subtipo no cabecalho
    como o Garmin faz ($PGRMZ,...) -- em vez disso manda o subtipo como
    o PRIMEIRO CAMPO DE DADO ($PTNL,BPQ,... / $PUBX,00,...).

    Nesses casos, o REGISTRY conhece so o codigo do fabricante (ex:
    "TNL", "UBX") como sentence_id. Esta classe intercepta a
    instanciacao via __new__ e troca pra subclasse certa olhando
    data[0] -- e o analogo, no nosso framework, do padrao que a propria
    pynmea2 usa em ProprietarySentence.__new__ pra TNL/UBX/ASH. Nao
    precisou de NENHUMA mudanca no core pra suportar isso: e' um
    __new__ override numa classe-base local, escondido do resto da lib.

    Cada subclasse concreta se registra com o decorator
    `<Base>.subtype("<codigo>")` -- e nao declara `sentence_id` proprio
    (senao colidiria no REGISTRY junto com a classe base).

    Alguns fabricantes (Ashtech e' o caso real) tem uma sentenca cujo
    campo de subtipo NAO e' um codigo literal, e sim um valor que so da
    pra reconhecer por formato (ex: um timestamp). Para esses, use
    `<Base>.fallback(funcao_de_teste)` -- funcao_de_teste(data) -> bool
    -- verificada em ordem, DEPOIS que a busca exata no dict falhar.
    """
    _subtypes: dict = {}
    _fallbacks: list = []

    def __new__(cls, talker=None, sentence_id=None, data=(), raw=None):
        code = data[0] if data else None
        target_cls = cls._subtypes.get(code)
        if target_cls is None:
            for matches, candidate in cls._fallbacks:
                if matches(data):
                    target_cls = candidate
                    break
        if target_cls is None:
            target_cls = cls
        return object.__new__(target_cls)

    @classmethod
    def subtype(cls, code):
        def decorator(subclass):
            cls._subtypes[code] = subclass
            return subclass
        return decorator

    @classmethod
    def fallback(cls, matches):
        """
        Registra uma regra de reconhecimento por formato (nao por codigo
        literal), verificada em ordem apos a busca exata falhar.
        `matches` recebe `data` (a tupla de campos crus) e devolve bool.
        """
        def decorator(subclass):
            cls._fallbacks.append((matches, subclass))
            return subclass
        return decorator


class TNL(SubtypedManufacturerSentence):
    """$PTNL,<subtipo>,... - Trimble. Ver TNL.subtype() para os formatos suportados."""
    dialect = "proprietary"
    framing = PROPRIETARY_FRAMING
    sentence_id = "TNL"
    _subtypes = {}


@TNL.subtype("BPQ")
class TNLBPQ(TNL, LatLonMixin):
    """$PTNL,BPQ - Trimble: posicao com qualidade de fix RTK."""
    fields = (
        StringField("Sentence Subtype", "subtype"),
        Field("Timestamp", "timestamp", parse=parse_time, render=render_time),
        Field("Datestamp", "datestamp", parse=parse_date, render=render_date),
        StringField("Latitude", "lat"),
        StringField("Latitude Direction", "lat_dir"),
        StringField("Longitude", "lon"),
        StringField("Longitude Direction", "lon_dir"),
        # "EHT-5.923": codigo do tipo de altura (EHT = Ellipsoidal
        # Height) colado direto no valor numerico, sem separador --
        # formatacao propria do Trimble. Guardamos crua (StringField)
        # em vez de tentar separar codigo+numero.
        StringField("Height", "height"),
        StringField("Height Unit", "height_unit", choices=("M",)),
        IntField("GPS Quality", "quality"),
    )


class UBX(SubtypedManufacturerSentence):
    """$PUBX,<subtipo>,... - u-blox. Ver UBX.subtype() para os formatos suportados."""
    dialect = "proprietary"
    framing = PROPRIETARY_FRAMING
    sentence_id = "UBX"
    _subtypes = {}


@UBX.subtype("00")
class UBX00(UBX, LatLonMixin):
    """$PUBX,00 - u-blox: relatorio de posicao (Lat/Long Position Data)."""
    fields = (
        StringField("Message ID", "subtype"),
        Field("Timestamp", "timestamp", parse=parse_time, render=render_time),
        StringField("Latitude", "lat"),
        StringField("Latitude Direction", "lat_dir"),
        StringField("Longitude", "lon"),
        StringField("Longitude Direction", "lon_dir"),
        FloatField("Altitude above Ellipsoid", "alt_ref"),
        StringField("Navigation Status", "nav_stat"),
        FloatField("Horizontal Accuracy", "h_acc"),
        FloatField("Vertical Accuracy", "v_acc"),
        FloatField("Speed over Ground (km/h)", "sog"),
        FloatField("Course over Ground", "cog"),
        FloatField("Vertical Velocity (downwards)", "v_vel"),
        StringField("Age of Differential Corrections", "diff_age"),
        FloatField("HDOP", "hdop"),
        FloatField("VDOP", "vdop"),
        FloatField("TDOP", "tdop"),
        IntField("Number of Satellites Used", "num_svs"),
        StringField("Reserved", "reserved"),
        IntField("Dead Reckoning Used", "dr_used"),
    )


@UBX.subtype("04")
class UBX04(UBX):
    """$PUBX,04 - u-blox: hora/data e estado do relogio do receptor."""
    fields = (
        StringField("Message ID", "subtype"),
        Field("Time", "time", parse=parse_time, render=render_time),
        Field("Date", "date", parse=parse_date, render=render_date),
        FloatField("UTC Time of Week", "utc_tow"),
        IntField("UTC Week Number", "utc_week"),
        IntField("Leap Seconds", "leap_sec"),
        IntField("Receiver Clock Bias", "clk_bias"),
        FloatField("Receiver Clock Drift", "clk_drift"),
        IntField("Time Pulse Granularity", "tp_gran"),
    )


class SXN(SubtypedManufacturerSentence):
    """$PSXN,<subtipo>,... - Seapath (sensores de atitude/heave)."""
    dialect = "proprietary"
    framing = PROPRIETARY_FRAMING
    sentence_id = "SXN"
    _subtypes = {}
    _fallbacks = []


@SXN.subtype("23")
class SXN23(SXN):
    """$PSXN,23 - Seapath: roll, pitch, heading, heave."""
    fields = (
        StringField("Message Type", "message_type"),
        FloatField("Roll", "roll"),
        FloatField("Pitch", "pitch"),
        FloatField("Heading", "head"),
        FloatField("Heave", "heave"),
    )


class VTX(SubtypedManufacturerSentence):
    """$PVTX,<subtipo>,... - Vectronix Moskito TI (telemetro a laser)."""
    dialect = "proprietary"
    framing = PROPRIETARY_FRAMING
    sentence_id = "VTX"
    _subtypes = {}
    _fallbacks = []


@VTX.subtype("0020")
class VTX0020(VTX, LatLonMixin):
    """$PVTX,0020 - Vectronix: localizacao propria (lat/lon/altitude)."""
    fields = (
        StringField("Subtype", "subtype"),
        IntField("Measurement ID", "measurement_id"),
        StringField("Latitude", "lat"),
        StringField("Latitude Direction", "lat_dir"),
        StringField("Longitude", "lon"),
        StringField("Longitude Direction", "lon_dir"),
        FloatField("Altitude above WGS84 ellipsoid, meters", "altitude"),
        StringField("Altitude Units", "altitude_units"),
    )


class FEC(SubtypedManufacturerSentence):
    """$PFEC,<subtipo>,... - Furuno."""
    dialect = "proprietary"
    framing = PROPRIETARY_FRAMING
    sentence_id = "FEC"
    _subtypes = {}
    _fallbacks = []


@FEC.subtype("GPatt")
class FECGPatt(FEC):
    """$PFEC,GPatt - Furuno: atitude (yaw/pitch/roll)."""
    fields = (
        StringField("Subtype", "subtype"),
        FloatField("Yaw", "yaw"),
        FloatField("Pitch", "pitch"),
        FloatField("Roll", "roll"),
    )


class ASHR(SubtypedManufacturerSentence):
    """
    $PASHR,<subtipo>,... - Ashtech.

    Caso especial: a sentenca ATT (RT300) NAO tem codigo de subtipo
    literal -- o que estaria nessa posicao e' direto um timestamp
    (formato hhmmss.ss). Por isso ela e' reconhecida por `fallback()`
    (regex), verificado so depois que a busca exata no dict de codigos
    (POS/HPR/LTN/VEL) falhar.
    """
    dialect = "proprietary"
    framing = PROPRIETARY_FRAMING
    sentence_id = "ASHR"
    _subtypes = {}
    _fallbacks = []


@ASHR.subtype("POS")
class ASHRPOS(ASHR, LatLonMixin):
    """$PASHR,POS - Ashtech: posicao."""
    fields = (
        StringField("Subtype", "subtype"),
        IntField("Solution Type", "mode"),
        IntField("Satellites Used", "sat_count"),
        Field("Timestamp", "timestamp", parse=parse_time, render=render_time),
        StringField("Latitude", "lat"),
        StringField("Latitude Direction", "lat_dir"),
        StringField("Longitude", "lon"),
        StringField("Longitude Direction", "lon_dir"),
        FloatField("Altitude above WGS84 ellipsoid, meters", "altitude"),
        StringField("Empty", "_empty"),
        FloatField("True Track/Course Over Ground", "course"),
        FloatField("Speed Over Ground", "spd_over_grnd"),
        FloatField("Vertical Velocity", "vertical_velocity"),
        FloatField("PDOP", "pdop"),
        FloatField("HDOP", "hdop"),
        FloatField("VDOP", "vdop"),
        FloatField("TDOP", "tdop"),
        IntField("Base Station ID", "station_id"),
    )


@ASHR.fallback(lambda data: bool(data) and re.match(r"^\d{6}\.\d{2,3}$", data[0] or ""))
class ASHRATT(ASHR):
    """
    $PASHR,<timestamp>,... - Ashtech RT300: atitude. Reconhecida por
    fallback (regex), nao por codigo literal -- ver docstring de ASHR.
    """
    fields = (
        Field("Timestamp", "timestamp", parse=parse_time, render=render_time),
        FloatField("Heading Angle", "true_heading"),
        StringField("Is True Heading", "is_true_heading"),
        FloatField("Roll Angle", "roll"),
        FloatField("Pitch Angle", "pitch"),
        FloatField("Heave", "heave"),
        FloatField("Roll Accuracy Estimate", "roll_accuracy"),
        FloatField("Pitch Accuracy Estimate", "pitch_accuracy"),
        FloatField("Heading Accuracy Estimate", "heading_accuracy"),
        IntField("Aiding Status", "aiding_status"),
        IntField("IMU Status", "imu_status"),
    )
