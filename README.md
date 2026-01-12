# FamilyKom

**Familienrechts-Applikation** für RHM - Radtke, Heigener und Meier Kanzlei, Rendsburg

Version 1.0 | Januar 2026

## Projektübersicht

FamilyKom ist eine umfassende digitale Plattform für die effiziente Zusammenarbeit zwischen Anwälten und Mandanten in familienrechtlichen Angelegenheiten. Die Anwendung integriert Berechnungstools für Unterhalt und Zugewinnausgleich mit einem modernen Dokumentenmanagementsystem.

### Kernfunktionen

- **Mandantenportal** mit Code-basiertem Zugang und Aktenverknüpfung
- **Anwaltsportal** mit umfassenden Berechnungstools
- **Administrator-Dashboard** für Systemverwaltung
- **Berechnungsmodule:**
  - Kindesunterhalt nach Düsseldorfer Tabelle 2025
  - Trennungs- und nachehelicher Unterhalt
  - Zugewinnausgleich mit VPI-Indexierung
  - RVG-Gebührenberechnung

## Technologie-Stack

| Komponente | Technologie |
|------------|-------------|
| Frontend | Streamlit (Python) |
| Backend/Datenbank | Supabase (PostgreSQL, Auth, Storage) |
| Cache | Upstash Redis |
| Dokumentenverarbeitung | PyPDF2, python-docx, openpyxl |

## Projektstruktur

```
FamilyKom/
├── app.py                      # Streamlit Hauptanwendung
├── requirements.txt            # Python-Abhängigkeiten
├── pyproject.toml             # Projekt-Konfiguration
├── .env.example               # Umgebungsvariablen-Vorlage
│
├── config/                    # Konfiguration
│   ├── settings.py            # Anwendungseinstellungen
│   └── constants.py           # Konstanten (Tabellen, Sätze)
│
├── src/
│   ├── calculators/           # Berechnungsmodule
│   │   ├── kindesunterhalt.py
│   │   ├── ehegattenunterhalt.py
│   │   ├── zugewinn.py
│   │   └── rvg.py
│   │
│   ├── database/              # Datenbankschicht
│   │   ├── schema.sql         # PostgreSQL-Schema
│   │   ├── supabase_client.py
│   │   └── redis_cache.py
│   │
│   ├── pages/                 # Streamlit-Seiten
│   │   ├── mandant/
│   │   ├── anwalt/
│   │   └── admin/
│   │
│   └── utils/                 # Hilfsfunktionen
│
├── data/                      # Datendateien
└── tests/                     # Tests
```

## Installation

### Voraussetzungen

- Python 3.11+
- Supabase-Projekt (PostgreSQL, Auth, Storage)
- Upstash Redis-Instanz

### Setup

1. **Repository klonen:**
   ```bash
   git clone <repository-url>
   cd FamilyKom
   ```

2. **Virtuelle Umgebung erstellen:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # oder: venv\Scripts\activate  # Windows
   ```

3. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Umgebungsvariablen konfigurieren:**
   ```bash
   cp .env.example .env
   # .env mit Ihren Werten ausfüllen
   ```

5. **Datenbank einrichten:**
   - Schema in Supabase SQL-Editor ausführen: `src/database/schema.sql`

6. **Anwendung starten:**
   ```bash
   streamlit run app.py
   ```

## Konfiguration

### Umgebungsvariablen (.env)

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Upstash Redis
UPSTASH_REDIS_URL=https://your-redis.upstash.io
UPSTASH_REDIS_TOKEN=your-redis-token

# Anwendung
APP_ENV=development
APP_DEBUG=true
APP_SECRET_KEY=your-secret-key
```

## Berechnungsmodule

### Kindesunterhalt

Berechnung nach der **Düsseldorfer Tabelle 2025**:
- Einkommensbereinigung nach OLG-Leitlinien Schleswig-Holstein
- Gruppenanpassung bei Anzahl der Unterhaltsberechtigten
- Kindergeldanrechnung (255 EUR ab 2025)
- Selbstbehaltsprüfung und Mangelfallberechnung

### Ehegattenunterhalt

- **Trennungsunterhalt** (Paragraph 1361 BGB)
- **Nachehelicher Unterhalt** (Paragraphen 1569 ff. BGB)
- Differenzmethode mit Erwerbstätigenbonus (1/10)
- Prüfung aller Unterhaltstatbestände

### Zugewinnausgleich

- Berechnung nach Paragraphen 1373 ff. BGB
- VPI-Indexierung des Anfangsvermögens
- Berücksichtigung privilegierter Erwerbe (Erbschaften/Schenkungen)

### RVG-Gebühren

- Gebührentabelle Stand 01.06.2025 (KostBRÄG 2025)
- Gegenstandswertberechnung nach FamGKG
- Scheidungsverfahren mit Folgesachen
- Außergerichtliche und gerichtliche Vertretung

## Demo-Zugaenge

### Schnellzugang (Demo-Buttons)

Auf der Login-Seite koennen Sie mit einem Klick als Demo-Benutzer einloggen:

- **Als Anwalt** - Zugang als Rechtsanwalt Dr. Thomas Mueller
- **Als Mitarbeiter** - Zugang als Kanzleimitarbeiterin Sandra Schmidt
- **Als Mandant** - Zugang als Mandant Max Mustermann
- **Als Administrator** - Zugang zum Admin-Dashboard

### Manuelle Anmeldung

**Anwaelte:**

| E-Mail | Passwort |
|--------|----------|
| ra.mueller@rhm-kanzlei.de | anwalt123 |
| ra.radtke@rhm-kanzlei.de | anwalt123 |
| ra.heigener@rhm-kanzlei.de | anwalt123 |
| ra.meier@rhm-kanzlei.de | anwalt123 |

**Mitarbeiter:**

| E-Mail | Passwort |
|--------|----------|
| sekretariat@rhm-kanzlei.de | mitarbeiter123 |
| buchhaltung@rhm-kanzlei.de | mitarbeiter123 |

**Administrator:**

| E-Mail | Passwort |
|--------|----------|
| admin@rhm-kanzlei.de | admin123 |

**Mandanten (Zugangscodes):**

| Mandant | Zugangscode |
|---------|-------------|
| Max Mustermann | MUSTERMANN2026 |
| Lisa Schmidt | SCHMIDT2026 |
| Demo-Mandant | DEMO123456 |

## Rechtliche Grundlagen

Die Anwendung basiert auf:

- **Düsseldorfer Tabelle 2025** (OLG Düsseldorf)
- **OLG-Leitlinien Schleswig-Holstein 2025**
- **RVG** (Rechtsanwaltsvergütungsgesetz)
- **FamGKG** (Familiengerichtskostengesetz)
- **BGB** Paragraphen 1361, 1373 ff., 1569 ff.

## Lizenz

Proprietär - Entwickelt für RHM Kanzlei, Rendsburg

---

RHM - Radtke, Heigener und Meier
Kanzlei für Familienrecht, Rendsburg
