import datetime

def parse_time(raw: str):
    if not raw:
        return None
    hour = int(raw[0:2])
    minute = int(raw[2:4])
    second = float(raw[4:])
    whole = int(second)
    micro = int(round((second - whole) * 1_000_000))
    return datetime.time(hour, minute, whole, micro)


def render_time(t) -> str:
    if t is None:
        return ""
    return f"{t.hour:02d}{t.minute:02d}{t.second:02d}.{t.microsecond // 10000:02d}"


def parse_date(raw: str):
    if not raw:
        return None
    day, month, year = int(raw[0:2]), int(raw[2:4]), int(raw[4:6])
    year += 2000 if year < 80 else 1900
    return datetime.date(year, month, day)


def render_date(d) -> str:
    if d is None:
        return ""
    return f"{d.day:02d}{d.month:02d}{d.year % 100:02d}"


def dm_to_decimal(raw: str, direction: str):
    """Converte DDDMM.MMMM e direcao (N/S/E/W) para graus decimais."""
    if not raw:
        return None
    dot = raw.index(".")
    degrees = int(raw[: dot - 2])
    minutes = float(raw[dot - 2:])
    value = degrees + minutes / 60
    if direction in ("S", "W"):
        value = -value
    return value

class LatLonMixin:
    """Expoe latitude/longitude como float (graus decimais), a partir dos campos crus."""

    @property
    def latitude(self):
        return dm_to_decimal(self.lat, self.lat_dir) if getattr(self, "lat", None) else None

    @property
    def longitude(self):
        return dm_to_decimal(self.lon, self.lon_dir) if getattr(self, "lon", None) else None

class DepthMixin:
    """ Expõe profundidade em metros """
    @property
    def depth(self):
        meters = getattr(self, "depth_meters", None)
        if meters is not None:
            return meters
        feet = getattr(self, "depth_feet", None)
        if feet is not None:
            return feet * 0.3048
        fathoms = getattr(self, "depth_fathoms", None)
        if fathoms is not None:
            return fathoms * 1.8288
        return None