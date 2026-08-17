"""
Sentencas de RADAR/ARPA ($RAxxx).
"""
 
from marine4py.core.field import Field, FloatField, IntField, StringField
from marine4py.dialects.nmea.nmea_common import DefaultSentence
from marine4py.dialects.utils import LatLonMixin, parse_time, render_time

class TTM(DefaultSentence):
    """
    Tracked Target Message -- alvo rastreado por ARPA (distancia/rumo/
    velocidade relativos ao proprio navio, ponto de maxima aproximacao e
    status do rastreio).
    """
    sentence_id = "TTM"
    fields = (
        IntField("Target Number", "target_number", required=True, validate=lambda v: 0 <= v <= 99),
        FloatField("Target Distance", "target_distance"),
        FloatField("Bearing from Own Ship", "bearing"),
        StringField("Bearing Units", "bearing_units", choices=("T", "R")),
        FloatField("Target Speed", "target_speed"),
        FloatField("Target Course", "target_course"),
        StringField("Course Units", "course_units", choices=("T", "R")),
        FloatField("Distance of Closest Point of Approach", "cpa_distance"),
        FloatField("Time to Closest Point of Approach", "cpa_time"),  # "-" = aumentando
        StringField("Speed/Distance Units", "speed_dist_units", choices=("K", "N", "S")),
        StringField("Target Name", "target_name"),
        StringField("Target Status", "target_status", choices=("L", "Q", "T")),
        StringField("Reference Target", "reference_target", choices=("R",)),
    )
 
 
class RSD(DefaultSentence):
    """
    RADAR System Data -- estado da tela do radar: origem/alcance dos
    marcadores VRM/EBL 1 e 2, cursor, escala e modo de exibicao.
 
    Sentenca aprovada e designada IEC/IMO no padrao oficial (NMEA 0183
    v3.01, *RSD, pag. 63). A ordem de campos abaixo foi conferida
    diretamente contra esse padrao.
    """
    sentence_id = "RSD"
    fields = (
        FloatField("Origin 1 Range", "origin1_range"),
        FloatField("Origin 1 Bearing", "origin1_bearing"),
        FloatField("Variable Range Marker 1", "vrm1"),
        FloatField("Electronic Bearing Line 1", "ebl1"),
        FloatField("Origin 2 Range", "origin2_range"),
        FloatField("Origin 2 Bearing", "origin2_bearing"),
        FloatField("Variable Range Marker 2", "vrm2"),
        FloatField("Electronic Bearing Line 2", "ebl2"),
        FloatField("Cursor Range", "cursor_range"),
        FloatField("Cursor Bearing", "cursor_bearing"),
        FloatField("Range Scale", "range_scale"),
        StringField("Range Units", "range_units", choices=("K", "N", "S")),
        StringField("Display Rotation", "display_rotation", choices=("C", "H", "N")),
    )
 
 
class OSD(DefaultSentence):
    """
    Own Ship Data -- heading, rumo, velocidade, deriva (set/drift) e
    referencias de sensor do proprio navio. E o contexto que falta no TTM
    (que da o alvo em relacao ao navio) para converter bearing relativo em
    bearing verdadeiro, e para o ECDIS/ARPA plotar o alvo no mapa.
    """
    sentence_id = "OSD"
    fields = (
        FloatField("Heading", "heading"),
        StringField("Heading Status", "heading_status", choices=("A", "V")),
        FloatField("Vessel Course", "course"),
        StringField("Course Reference", "course_ref", choices=("B", "M", "W", "R", "P")),
        FloatField("Vessel Speed", "speed"),
        StringField("Speed Reference", "speed_ref", choices=("B", "M", "W", "R", "P")),
        FloatField("Vessel Set", "set_deg"),
        FloatField("Vessel Drift", "drift"),
        StringField("Speed Units", "speed_units", choices=("K", "N", "S")),
    )
 
 
class TLL(DefaultSentence, LatLonMixin):
    """
    Target Latitude and Longitude -- posicao absoluta (lat/lon) de um alvo
    rastreado, complementar ao TTM (que da a posicao so em relacao ao
    proprio navio).
 
    Ao contrario do que a compilacao nao-oficial do Betke sugere ("Format
    unknown"), o TLL E uma sentenca aprovada no padrao oficial da NMEA
    (NMEA 0183 v3.01, Table 5 - Approved Sentence Formatters, pag. 66).
    O layout abaixo foi conferido contra o indice desse padrao oficial e
    confirmado de forma independente (nmea.de/da-tll.html), campo a campo.
    """
    sentence_id = "TLL"
    fields = (
        IntField("Target Number", "target_number", required=True, validate=lambda v: 0 <= v <= 99),
        StringField("Latitude", "lat"),
        StringField("Latitude Direction", "lat_dir"),
        StringField("Longitude", "lon"),
        StringField("Longitude Direction", "lon_dir"),
        StringField("Target Name", "target_name"),
        Field("Timestamp", "timestamp", parse=parse_time, render=render_time),
        StringField("Target Status", "target_status", choices=("L", "Q", "T")),
        StringField("Reference Target", "reference_target", choices=("R",)),
    )