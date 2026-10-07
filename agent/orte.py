"""Koordinaten bekannter Orte, um Entfernungen ohne Geocoding-Dienst zu schätzen."""

import math

ORTE = {
    "bremen": (53.0793, 8.8017),
    "bremerhaven": (53.5396, 8.5809),
    "delmenhorst": (53.0511, 8.6317),
    "oldenburg": (53.1435, 8.2146),
    "achim": (53.0138, 9.0264),
    "verden": (52.9227, 9.2345),
    "osterholz": (53.2297, 8.7951),
    "cuxhaven": (53.8615, 8.6944),
    "wilhelmshaven": (53.5300, 8.1059),
    "emden": (53.3670, 7.2060),
    "leer": (53.2316, 7.4610),
    "vechta": (52.7290, 8.2850),
    "cloppenburg": (52.8475, 8.0450),
    "rotenburg": (53.1110, 9.4110),
    "stade": (53.5990, 9.4760),
    "osnabrück": (52.2799, 8.0472),
    "hamburg": (53.5511, 9.9937),
    "lüneburg": (53.2464, 10.4115),
    "hannover": (52.3759, 9.7320),
    "celle": (52.6226, 10.0805),
    "braunschweig": (52.2689, 10.5268),
    "wolfsburg": (52.4227, 10.7865),
    "hildesheim": (52.1508, 9.9511),
    "göttingen": (51.5413, 9.9158),
    "kiel": (54.3233, 10.1228),
    "lübeck": (53.8655, 10.6866),
    "schwerin": (53.6355, 11.4012),
    "bielefeld": (52.0302, 8.5325),
    "münster": (51.9607, 7.6261),
    "dortmund": (51.5136, 7.4653),
    "essen": (51.4556, 7.0116),
    "duisburg": (51.4344, 6.7623),
    "düsseldorf": (51.2277, 6.7735),
    "köln": (50.9375, 6.9603),
    "bonn": (50.7374, 7.0982),
    "berlin": (52.5200, 13.4050),
    "leipzig": (51.3397, 12.3731),
    "dresden": (51.0504, 13.7373),
    "frankfurt": (50.1109, 8.6821),
    "stuttgart": (48.7758, 9.1829),
    "münchen": (48.1351, 11.5820),
    "nürnberg": (49.4521, 11.0767),
}


def km(a, b):
    """Luftlinie in km zwischen zwei (lat, lon)-Paaren."""
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def finde_ort(text):
    """Sucht den ersten bekannten Ortsnamen im Text und gibt (name, koordinaten) zurück."""
    t = (text or "").lower()
    treffer = [(t.find(name), name) for name in ORTE if name in t]
    if not treffer:
        return None, None
    _, name = min(treffer)
    return name.title(), ORTE[name]
