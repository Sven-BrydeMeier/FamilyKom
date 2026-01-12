"""
Gerichtsdatenbank fuer Schleswig-Holstein

Enthaelt:
- Amtsgerichte mit Familienabteilungen
- Zustaendige Oberlandesgerichte
- PLZ-Zuordnungen fuer oertliche Zustaendigkeit nach ZPO
"""

from typing import Dict, List, Optional, Tuple

# Oberlandesgerichte
OBERLANDESGERICHTE = {
    "olg_schleswig": {
        "name": "Schleswig-Holsteinisches Oberlandesgericht",
        "kurzname": "OLG Schleswig",
        "adresse": "Gottorfstrasse 2, 24837 Schleswig",
        "telefon": "04621 86-0",
        "fax": "04621 86-200",
        "email": "poststelle@olg.landsh.de"
    }
}

# Amtsgerichte mit Familienabteilungen in Schleswig-Holstein
AMTSGERICHTE = {
    "ag_flensburg": {
        "name": "Amtsgericht Flensburg",
        "kurzname": "AG Flensburg",
        "adresse": "Suedergraben 22, 24937 Flensburg",
        "telefon": "0461 89-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["24937", "24939", "24941", "24943", "24944", "24955", "24960", "24972", "24980", "24983", "24986", "24988", "24989", "24991", "24994", "24996", "24997", "24999"]
    },
    "ag_husum": {
        "name": "Amtsgericht Husum",
        "kurzname": "AG Husum",
        "adresse": "Schlossgang 2, 25813 Husum",
        "telefon": "04841 899-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["25813", "25821", "25826", "25832", "25836", "25840", "25842", "25845", "25849", "25850", "25852", "25853", "25855", "25856", "25858", "25859", "25860", "25862", "25863", "25864", "25866", "25867", "25868", "25869", "25870", "25872", "25873", "25874", "25876", "25878", "25879", "25881", "25882", "25884", "25885", "25886", "25887", "25889"]
    },
    "ag_kiel": {
        "name": "Amtsgericht Kiel",
        "kurzname": "AG Kiel",
        "adresse": "Deliusstrasse 22, 24114 Kiel",
        "telefon": "0431 604-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["24103", "24105", "24106", "24107", "24109", "24111", "24113", "24114", "24116", "24118", "24119", "24143", "24145", "24146", "24147", "24148", "24149", "24159", "24161", "24211", "24214", "24217", "24220", "24222", "24223", "24226", "24229", "24232", "24235", "24238", "24239", "24240", "24241", "24242", "24244", "24245", "24247", "24248", "24250", "24251", "24253", "24254", "24256", "24257", "24259"]
    },
    "ag_luebeck": {
        "name": "Amtsgericht Luebeck",
        "kurzname": "AG Luebeck",
        "adresse": "Am Burgfeld 7, 23568 Luebeck",
        "telefon": "0451 371-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["23552", "23554", "23556", "23558", "23560", "23562", "23564", "23566", "23568", "23569", "23570", "23611", "23617", "23619", "23623", "23626", "23627", "23628", "23629", "23669", "23683", "23684", "23701", "23714", "23715", "23717", "23719", "23730", "23738", "23743", "23744", "23746", "23747", "23749", "23758", "23769", "23774", "23775", "23777", "23779", "23795", "23812", "23813", "23815", "23816", "23818", "23820", "23821", "23823", "23824", "23826", "23827", "23828", "23829", "23843", "23845", "23847", "23858", "23860", "23863", "23866", "23867", "23869"]
    },
    "ag_neumuenster": {
        "name": "Amtsgericht Neumuenster",
        "kurzname": "AG Neumuenster",
        "adresse": "Boostedter Strasse 33, 24534 Neumuenster",
        "telefon": "04321 942-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["24534", "24536", "24537", "24539", "24568", "24576", "24582", "24589", "24594", "24598", "24601", "24610", "24613", "24616", "24619", "24620", "24622", "24623", "24625", "24626", "24627", "24628", "24629", "24631", "24632", "24634", "24635", "24637", "24638", "24640", "24641", "24643", "24644", "24646", "24647", "24649"]
    },
    "ag_pinneberg": {
        "name": "Amtsgericht Pinneberg",
        "kurzname": "AG Pinneberg",
        "adresse": "Am Rathaus 3, 25421 Pinneberg",
        "telefon": "04101 54-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["22844", "22846", "22848", "22850", "22851", "22869", "22880", "22889", "25335", "25336", "25337", "25348", "25355", "25358", "25361", "25364", "25365", "25368", "25370", "25371", "25373", "25376", "25377", "25379", "25421", "25436", "25451", "25462", "25469", "25474", "25479", "25482", "25485", "25486", "25488", "25489", "25491", "25492", "25494", "25495", "25497", "25499"]
    },
    "ag_rendsburg": {
        "name": "Amtsgericht Rendsburg",
        "kurzname": "AG Rendsburg",
        "adresse": "Hindenburgstrasse 17, 24768 Rendsburg",
        "telefon": "04331 141-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["24768", "24782", "24783", "24784", "24787", "24790", "24791", "24793", "24794", "24796", "24797", "24799", "24800", "24802", "24803", "24805", "24806", "24808", "24809", "24811", "24813", "24814", "24816", "24817", "24819", "24850", "24857", "24860", "24861", "24863", "24864", "24866", "24867", "24869", "24870", "24872", "24873", "24876", "24878", "24879", "24881", "24882", "24884", "24885", "24887", "24888", "24890", "24891", "24893", "24894", "24896", "24897", "24899"]
    },
    "ag_eckernfoerde": {
        "name": "Amtsgericht Eckernfoerde",
        "kurzname": "AG Eckernfoerde",
        "adresse": "Reeperbahn 31, 24340 Eckernfoerde",
        "telefon": "04351 712-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["24340", "24351", "24354", "24357", "24358", "24360", "24361", "24363", "24364", "24366", "24367", "24369", "24370", "24372", "24376", "24392", "24395", "24398", "24399", "24401", "24402", "24404", "24405", "24407", "24409"]
    },
    "ag_itzehoe": {
        "name": "Amtsgericht Itzehoe",
        "kurzname": "AG Itzehoe",
        "adresse": "Breitenburger Strasse 31, 25524 Itzehoe",
        "telefon": "04821 66-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["25524", "25541", "25548", "25551", "25554", "25557", "25560", "25563", "25566", "25569", "25572", "25573", "25575", "25576", "25578", "25579", "25581", "25582", "25584", "25585", "25587", "25588", "25590", "25591", "25593", "25594", "25596", "25597", "25599"]
    },
    "ag_elmshorn": {
        "name": "Amtsgericht Elmshorn",
        "kurzname": "AG Elmshorn",
        "adresse": "Koenigstrasse 1, 25335 Elmshorn",
        "telefon": "04121 487-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["25335", "25336", "25337", "25348", "25355", "25358", "25361", "25364", "25365", "25368", "25370", "25371", "25373", "25376", "25377", "25379"]
    },
    "ag_schwarzenbek": {
        "name": "Amtsgericht Schwarzenbek",
        "kurzname": "AG Schwarzenbek",
        "adresse": "Moellner Strasse 30, 21493 Schwarzenbek",
        "telefon": "04151 896-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["21493", "21502", "21509", "21514", "21516", "21521", "21522", "21524", "21526", "21527", "21529"]
    },
    "ag_ratzeburg": {
        "name": "Amtsgericht Ratzeburg",
        "kurzname": "AG Ratzeburg",
        "adresse": "Unter den Linden 1, 23909 Ratzeburg",
        "telefon": "04541 882-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["23909", "23911", "23919", "23923", "23936", "23942", "23946", "23948", "23952", "23954", "23956", "23958", "23966", "23968", "23970"]
    },
    "ag_meldorf": {
        "name": "Amtsgericht Meldorf",
        "kurzname": "AG Meldorf",
        "adresse": "Suederstrasse 2, 25704 Meldorf",
        "telefon": "04832 602-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["25693", "25704", "25709", "25712", "25715", "25718", "25719", "25721", "25724", "25725", "25727", "25729", "25746", "25761", "25764", "25767", "25770", "25774", "25776", "25779", "25782", "25785", "25786", "25788", "25791", "25792", "25794", "25795", "25797", "25799"]
    },
    "ag_heide": {
        "name": "Amtsgericht Heide",
        "kurzname": "AG Heide",
        "adresse": "Neue Anlage 4, 25746 Heide",
        "telefon": "0481 68-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["25746", "25761", "25764", "25767", "25770", "25774", "25776", "25779", "25782", "25785", "25786", "25788", "25791", "25792", "25794", "25795", "25797", "25799"]
    },
    "ag_norderstedt": {
        "name": "Amtsgericht Norderstedt",
        "kurzname": "AG Norderstedt",
        "adresse": "Rathausallee 80, 22846 Norderstedt",
        "telefon": "040 535003-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["22844", "22846", "22848", "22850", "22851", "22869", "22880", "22889", "24568", "24576", "24582", "24589", "24594", "24598"]
    },
    "ag_bad_segeberg": {
        "name": "Amtsgericht Bad Segeberg",
        "kurzname": "AG Bad Segeberg",
        "adresse": "Luebecker Strasse 54, 23795 Bad Segeberg",
        "telefon": "04551 908-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["23795", "23812", "23813", "23815", "23816", "23818", "23820", "23821", "23823", "23824", "23826", "23827", "23828", "23829", "23843", "23845", "23847", "23858", "23860", "23863", "23866", "23867", "23869"]
    },
    "ag_oldenburg_holstein": {
        "name": "Amtsgericht Oldenburg in Holstein",
        "kurzname": "AG Oldenburg i.H.",
        "adresse": "Am Markt 14, 23758 Oldenburg i.H.",
        "telefon": "04361 508-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["23758", "23769", "23774", "23775", "23777", "23779"]
    },
    "ag_ploen": {
        "name": "Amtsgericht Ploen",
        "kurzname": "AG Ploen",
        "adresse": "Schlossberg 4, 24306 Ploen",
        "telefon": "04522 749-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["24211", "24214", "24217", "24220", "24222", "24223", "24226", "24229", "24232", "24235", "24238", "24239", "24240", "24241", "24242", "24244", "24245", "24247", "24248", "24250", "24251", "24253", "24254", "24256", "24257", "24259", "24306", "24321", "24326", "24327", "24329", "24332", "24335", "24336", "24340"]
    },
    "ag_schleswig": {
        "name": "Amtsgericht Schleswig",
        "kurzname": "AG Schleswig",
        "adresse": "Lollfuss 78, 24837 Schleswig",
        "telefon": "04621 808-0",
        "familiengericht": True,
        "olg": "olg_schleswig",
        "plz_bereiche": ["24837", "24848", "24850", "24855", "24857", "24860", "24861"]
    }
}

# Jugendaemter in Schleswig-Holstein
JUGENDAEMTER = {
    "ja_rendsburg": {
        "name": "Jugendamt Kreis Rendsburg-Eckernfoerde",
        "kurzname": "JA Rendsburg-Eckernfoerde",
        "adresse": "Kaiserstrasse 8, 24768 Rendsburg",
        "telefon": "04331 202-0",
        "email": "jugendamt@kreis-rd.de",
        "zustaendig_fuer": ["ag_rendsburg", "ag_eckernfoerde"]
    },
    "ja_kiel": {
        "name": "Jugendamt Stadt Kiel",
        "kurzname": "JA Kiel",
        "adresse": "Neues Rathaus, Andreas-Gayk-Strasse 31, 24103 Kiel",
        "telefon": "0431 901-0",
        "email": "jugendamt@kiel.de",
        "zustaendig_fuer": ["ag_kiel"]
    },
    "ja_luebeck": {
        "name": "Jugendamt Stadt Luebeck",
        "kurzname": "JA Luebeck",
        "adresse": "Kronsforder Allee 2-6, 23560 Luebeck",
        "telefon": "0451 122-0",
        "email": "jugendamt@luebeck.de",
        "zustaendig_fuer": ["ag_luebeck"]
    },
    "ja_flensburg": {
        "name": "Jugendamt Stadt Flensburg",
        "kurzname": "JA Flensburg",
        "adresse": "Rathausplatz 1, 24937 Flensburg",
        "telefon": "0461 85-0",
        "email": "jugendamt@flensburg.de",
        "zustaendig_fuer": ["ag_flensburg"]
    },
    "ja_neumuenster": {
        "name": "Jugendamt Stadt Neumuenster",
        "kurzname": "JA Neumuenster",
        "adresse": "Brachenfelder Strasse 1, 24534 Neumuenster",
        "telefon": "04321 942-0",
        "email": "jugendamt@neumuenster.de",
        "zustaendig_fuer": ["ag_neumuenster"]
    },
    "ja_pinneberg": {
        "name": "Jugendamt Kreis Pinneberg",
        "kurzname": "JA Pinneberg",
        "adresse": "Kurt-Wagener-Strasse 11, 25337 Elmshorn",
        "telefon": "04121 4502-0",
        "email": "jugendamt@kreis-pinneberg.de",
        "zustaendig_fuer": ["ag_pinneberg", "ag_elmshorn", "ag_norderstedt"]
    },
    "ja_steinburg": {
        "name": "Jugendamt Kreis Steinburg",
        "kurzname": "JA Steinburg",
        "adresse": "Viktoriastrasse 16-18, 25524 Itzehoe",
        "telefon": "04821 69-0",
        "email": "jugendamt@steinburg.de",
        "zustaendig_fuer": ["ag_itzehoe"]
    },
    "ja_dithmarschen": {
        "name": "Jugendamt Kreis Dithmarschen",
        "kurzname": "JA Dithmarschen",
        "adresse": "Stettiner Strasse 30, 25746 Heide",
        "telefon": "0481 97-0",
        "email": "jugendamt@dithmarschen.de",
        "zustaendig_fuer": ["ag_meldorf", "ag_heide"]
    },
    "ja_nordfriesland": {
        "name": "Jugendamt Kreis Nordfriesland",
        "kurzname": "JA Nordfriesland",
        "adresse": "Marktstrasse 6, 25813 Husum",
        "telefon": "04841 67-0",
        "email": "jugendamt@nordfriesland.de",
        "zustaendig_fuer": ["ag_husum"]
    },
    "ja_segeberg": {
        "name": "Jugendamt Kreis Segeberg",
        "kurzname": "JA Segeberg",
        "adresse": "Hamburger Strasse 30, 23795 Bad Segeberg",
        "telefon": "04551 951-0",
        "email": "jugendamt@segeberg.de",
        "zustaendig_fuer": ["ag_bad_segeberg"]
    },
    "ja_ostholstein": {
        "name": "Jugendamt Kreis Ostholstein",
        "kurzname": "JA Ostholstein",
        "adresse": "Luebecker Strasse 41, 23701 Eutin",
        "telefon": "04521 788-0",
        "email": "jugendamt@kreis-oh.de",
        "zustaendig_fuer": ["ag_oldenburg_holstein"]
    },
    "ja_ploen": {
        "name": "Jugendamt Kreis Ploen",
        "kurzname": "JA Ploen",
        "adresse": "Hamburger Strasse 17-18, 24306 Ploen",
        "telefon": "04522 743-0",
        "email": "jugendamt@kreis-ploen.de",
        "zustaendig_fuer": ["ag_ploen"]
    },
    "ja_schleswig_flensburg": {
        "name": "Jugendamt Kreis Schleswig-Flensburg",
        "kurzname": "JA Schleswig-Flensburg",
        "adresse": "Flensburger Strasse 7, 24837 Schleswig",
        "telefon": "04621 87-0",
        "email": "jugendamt@schleswig-flensburg.de",
        "zustaendig_fuer": ["ag_schleswig"]
    },
    "ja_stormarn": {
        "name": "Jugendamt Kreis Stormarn",
        "kurzname": "JA Stormarn",
        "adresse": "Mommsenstrasse 14, 23843 Bad Oldesloe",
        "telefon": "04531 160-0",
        "email": "jugendamt@kreis-stormarn.de",
        "zustaendig_fuer": ["ag_bad_segeberg"]
    },
    "ja_herzogtum_lauenburg": {
        "name": "Jugendamt Kreis Herzogtum Lauenburg",
        "kurzname": "JA Herzogtum Lauenburg",
        "adresse": "Barlachstrasse 4, 23909 Ratzeburg",
        "telefon": "04541 888-0",
        "email": "jugendamt@kreis-rz.de",
        "zustaendig_fuer": ["ag_ratzeburg", "ag_schwarzenbek"]
    }
}


def get_zustaendiges_gericht(plz: str) -> Optional[Dict]:
    """
    Ermittelt das zustaendige Amtsgericht basierend auf der PLZ.

    Nach ZPO SS 122 Nr. 1 ist fuer Familiensachen das Gericht zustaendig,
    in dessen Bezirk einer der Ehegatten seinen gewoehnlichen Aufenthalt hat.

    Args:
        plz: Postleitzahl des Wohnorts

    Returns:
        Dict mit Amtsgericht und OLG oder None
    """
    for ag_id, ag_data in AMTSGERICHTE.items():
        if plz in ag_data.get("plz_bereiche", []):
            olg_id = ag_data.get("olg")
            olg_data = OBERLANDESGERICHTE.get(olg_id, {})
            return {
                "amtsgericht_id": ag_id,
                "amtsgericht": ag_data,
                "oberlandesgericht_id": olg_id,
                "oberlandesgericht": olg_data
            }

    # Fallback: AG Rendsburg (Kanzleistandort)
    return {
        "amtsgericht_id": "ag_rendsburg",
        "amtsgericht": AMTSGERICHTE["ag_rendsburg"],
        "oberlandesgericht_id": "olg_schleswig",
        "oberlandesgericht": OBERLANDESGERICHTE["olg_schleswig"],
        "hinweis": "Keine direkte PLZ-Zuordnung gefunden. Vorschlag basiert auf Kanzleistandort."
    }


def get_zustaendiges_jugendamt(amtsgericht_id: str) -> Optional[Dict]:
    """
    Ermittelt das zustaendige Jugendamt basierend auf dem Amtsgericht.

    Args:
        amtsgericht_id: ID des Amtsgerichts

    Returns:
        Dict mit Jugendamt-Daten oder None
    """
    for ja_id, ja_data in JUGENDAEMTER.items():
        if amtsgericht_id in ja_data.get("zustaendig_fuer", []):
            return {
                "jugendamt_id": ja_id,
                "jugendamt": ja_data
            }
    return None


def get_alle_amtsgerichte() -> List[Dict]:
    """Gibt alle Amtsgerichte als Liste zurueck."""
    return [
        {"id": ag_id, **ag_data}
        for ag_id, ag_data in AMTSGERICHTE.items()
    ]


def get_alle_oberlandesgerichte() -> List[Dict]:
    """Gibt alle Oberlandesgerichte als Liste zurueck."""
    return [
        {"id": olg_id, **olg_data}
        for olg_id, olg_data in OBERLANDESGERICHTE.items()
    ]


def get_alle_jugendaemter() -> List[Dict]:
    """Gibt alle Jugendaemter als Liste zurueck."""
    return [
        {"id": ja_id, **ja_data}
        for ja_id, ja_data in JUGENDAEMTER.items()
    ]


def suche_gericht(suchbegriff: str) -> List[Dict]:
    """
    Sucht nach Gerichten basierend auf Namen oder Ort.

    Args:
        suchbegriff: Suchbegriff

    Returns:
        Liste mit passenden Gerichten
    """
    suchbegriff_lower = suchbegriff.lower()
    ergebnisse = []

    for ag_id, ag_data in AMTSGERICHTE.items():
        if (suchbegriff_lower in ag_data["name"].lower() or
            suchbegriff_lower in ag_data["kurzname"].lower() or
            suchbegriff_lower in ag_data["adresse"].lower()):
            ergebnisse.append({"id": ag_id, "typ": "Amtsgericht", **ag_data})

    for olg_id, olg_data in OBERLANDESGERICHTE.items():
        if (suchbegriff_lower in olg_data["name"].lower() or
            suchbegriff_lower in olg_data["kurzname"].lower()):
            ergebnisse.append({"id": olg_id, "typ": "Oberlandesgericht", **olg_data})

    return ergebnisse
