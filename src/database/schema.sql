-- FamilyKom Datenbankschema für Supabase
-- Familienrechts-Applikation für RHM Kanzlei Rendsburg
-- Version 1.1 | Januar 2026 - Erweitert gemäß Pflichtenheft

-- =============================================================================
-- EXTENSIONS
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- ENUM TYPES
-- =============================================================================

-- Benutzerrollen
CREATE TYPE user_role AS ENUM ('admin', 'anwalt', 'mitarbeiter', 'mandant');

-- Falltypen
CREATE TYPE case_type AS ENUM (
    'kindesunterhalt',
    'trennungsunterhalt',
    'nachehelicher_unterhalt',
    'scheidung',
    'zugewinnausgleich',
    'sorgerecht',
    'umgangsrecht',
    'versorgungsausgleich'
);

-- Fallstatus
CREATE TYPE case_status AS ENUM ('aktiv', 'ruhend', 'abgeschlossen', 'archiviert');

-- Dokumenttypen (erweitert)
CREATE TYPE document_type AS ENUM (
    'entgeltabrechnung',
    'steuerbescheid',
    'lohnsteuerbescheinigung',
    'kontoauszug',
    'geburtsurkunde',
    'heiratsurkunde',
    'grundbuchauszug',
    'handelsregisterauszug',
    'mietvertrag',
    'kreditvertrag',
    'arbeitsvertrag',
    'kuendigungsschreiben',
    'kindergeldbescheid',
    'elterngeldbescheid',
    'rentenauskunft',
    'versicherungspolice',
    'wertgutachten',
    'schriftsatz',
    'beschluss',
    'urteil',
    'vollmacht',
    'korrespondenz_gegner',
    'korrespondenz_gericht',
    'sonstiges'
);

-- Dokumentstatus für Slots
CREATE TYPE slot_status AS ENUM ('fehlend', 'hochgeladen', 'in_pruefung', 'akzeptiert', 'abgelehnt');

-- OCR Status
CREATE TYPE ocr_status AS ENUM ('pending', 'processing', 'completed', 'failed');

-- Freigabestatus
CREATE TYPE approval_status AS ENUM ('ausstehend', 'freigegeben', 'abgelehnt', 'kommentiert');

-- Ruleset Status
CREATE TYPE ruleset_status AS ENUM ('pending', 'active', 'deprecated');

-- Geschlecht
CREATE TYPE gender AS ENUM ('maennlich', 'weiblich', 'divers');

-- =============================================================================
-- USERS TABLE (Benutzer)
-- =============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth_id UUID UNIQUE, -- Referenz zu Supabase Auth
    email VARCHAR(255) UNIQUE NOT NULL,
    role user_role NOT NULL DEFAULT 'mandant',

    -- Persönliche Daten
    anrede VARCHAR(20),
    titel VARCHAR(50),
    vorname VARCHAR(100) NOT NULL,
    nachname VARCHAR(100) NOT NULL,

    -- Kontakt
    telefon VARCHAR(50),
    mobiltelefon VARCHAR(50),

    -- Für Anwälte
    rechtsanwaltsnummer VARCHAR(50),
    fachanwalt_fuer TEXT[],

    -- Status
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    two_factor_enabled BOOLEAN DEFAULT false,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

-- =============================================================================
-- CLIENTS TABLE (Mandanten)
-- =============================================================================
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Persönliche Daten
    anrede VARCHAR(20),
    titel VARCHAR(50),
    vorname VARCHAR(100) NOT NULL,
    nachname VARCHAR(100) NOT NULL,
    geburtsname VARCHAR(100),
    geburtsdatum DATE,
    geburtsort VARCHAR(100),
    staatsangehoerigkeit VARCHAR(50) DEFAULT 'deutsch',
    geschlecht gender,

    -- Kontakt
    email VARCHAR(255),
    telefon VARCHAR(50),
    mobiltelefon VARCHAR(50),

    -- Adresse
    strasse VARCHAR(200),
    hausnummer VARCHAR(20),
    plz VARCHAR(10),
    ort VARCHAR(100),
    land VARCHAR(50) DEFAULT 'Deutschland',

    -- Familienstand
    familienstand VARCHAR(50),
    eheschliessungsdatum DATE,
    trennungsdatum DATE,

    -- Berufliche Situation
    beruf VARCHAR(200),
    arbeitgeber VARCHAR(200),
    beschaeftigt_seit DATE,

    -- Finanzen
    bruttoeinkommen DECIMAL(12,2),
    nettoeinkommen DECIMAL(12,2),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- OPPONENTS TABLE (Gegner/Antragsgegner)
-- =============================================================================
CREATE TABLE opponents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Persönliche Daten
    anrede VARCHAR(20),
    titel VARCHAR(50),
    vorname VARCHAR(100),
    nachname VARCHAR(100) NOT NULL,
    geburtsname VARCHAR(100),
    geburtsdatum DATE,

    -- Kontakt
    email VARCHAR(255),
    telefon VARCHAR(50),

    -- Adresse
    strasse VARCHAR(200),
    hausnummer VARCHAR(20),
    plz VARCHAR(10),
    ort VARCHAR(100),

    -- Berufliche Situation
    beruf VARCHAR(200),
    arbeitgeber VARCHAR(200),
    bruttoeinkommen DECIMAL(12,2),
    nettoeinkommen DECIMAL(12,2),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- OPPONENT_LAWYERS TABLE (Gegnerische Anwälte)
-- =============================================================================
CREATE TABLE opponent_lawyers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Kanzleidaten
    kanzlei_name VARCHAR(200),
    anrede VARCHAR(20),
    titel VARCHAR(50),
    vorname VARCHAR(100),
    nachname VARCHAR(100) NOT NULL,

    -- Kontakt
    email VARCHAR(255),
    telefon VARCHAR(50),
    fax VARCHAR(50),

    -- Adresse
    strasse VARCHAR(200),
    hausnummer VARCHAR(20),
    plz VARCHAR(10),
    ort VARCHAR(100),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- OLG_GUIDELINES TABLE (OLG-Leitlinien)
-- =============================================================================
CREATE TABLE olg_guidelines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    olg_name VARCHAR(100) NOT NULL,
    olg_bezirk VARCHAR(100) NOT NULL,
    gueltig_ab DATE NOT NULL,
    gueltig_bis DATE,

    -- Leitlinien-Parameter (JSONB für Flexibilität)
    berufsbedingte_aufwendungen JSONB,
    altersvorsorge JSONB,
    erwerbstaetigenbonus DECIMAL(4,2),
    selbstbehalt JSONB,
    besonderheiten JSONB,

    -- Dokument
    dokument_url VARCHAR(500),

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- CASES TABLE (Akten/Mandate)
-- =============================================================================
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Aktenzeichen
    case_number VARCHAR(50) UNIQUE NOT NULL,
    case_type case_type NOT NULL,
    status case_status DEFAULT 'aktiv',

    -- Beteiligte
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
    opponent_id UUID REFERENCES opponents(id) ON DELETE SET NULL,
    lawyer_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    opponent_lawyer_id UUID REFERENCES opponent_lawyers(id) ON DELETE SET NULL,

    -- Zuständigkeit
    olg_id UUID REFERENCES olg_guidelines(id) ON DELETE SET NULL,
    gericht VARCHAR(200),
    gerichtliches_aktenzeichen VARCHAR(100),

    -- Mandanten-Zugang
    access_code VARCHAR(20) UNIQUE,
    access_code_valid_until TIMESTAMPTZ,

    -- Wichtige Daten
    eingangsdatum DATE DEFAULT CURRENT_DATE,
    trennungsdatum DATE,
    scheidungsantrag_zustellung DATE,

    -- Notizen
    beschreibung TEXT,
    interne_notizen TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- CHILDREN TABLE (Kinder)
-- =============================================================================
CREATE TABLE children (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    client_id UUID REFERENCES clients(id) ON DELETE CASCADE,

    vorname VARCHAR(100) NOT NULL,
    nachname VARCHAR(100) NOT NULL,
    geburtsdatum DATE NOT NULL,
    geschlecht gender,

    -- Wohnsituation
    lebt_bei VARCHAR(50), -- 'mandant', 'gegner', 'abwechselnd'
    lebt_bei_pflichtigem BOOLEAN DEFAULT false,

    -- Finanzen
    eigenes_einkommen DECIMAL(10,2) DEFAULT 0,
    ausbildungsverguetung DECIMAL(10,2) DEFAULT 0,
    kindergeld_empfaenger VARCHAR(50),

    -- Status
    in_ausbildung BOOLEAN DEFAULT false,
    ausbildung_art VARCHAR(100),
    privilegiert BOOLEAN DEFAULT true, -- § 1603 Abs. 2 BGB

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- DOCUMENTS TABLE (Dokumente)
-- =============================================================================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,

    -- Metadaten
    document_type document_type DEFAULT 'sonstiges',
    titel VARCHAR(255) NOT NULL,
    beschreibung TEXT,
    dateiname VARCHAR(255) NOT NULL,
    dateipfad VARCHAR(500) NOT NULL,
    dateityp VARCHAR(50),
    dateigroesse INTEGER,

    -- OCR
    ocr_text TEXT,
    ocr_verarbeitet BOOLEAN DEFAULT false,
    ocr_datum TIMESTAMPTZ,

    -- Herkunft
    hochgeladen_von UUID REFERENCES users(id),
    quelle VARCHAR(50), -- 'mandant', 'anwalt', 'gericht', 'gegner'

    -- Freigabe
    mandant_sichtbar BOOLEAN DEFAULT false,
    anwalt_freigabe TIMESTAMPTZ,

    -- Verknüpfungen
    bezug_zeitraum_von DATE,
    bezug_zeitraum_bis DATE,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- INCOME_RECORDS TABLE (Einkommenserfassung)
-- =============================================================================
CREATE TABLE income_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    person VARCHAR(50) NOT NULL, -- 'mandant' oder 'gegner'

    -- Zeitraum
    monat INTEGER NOT NULL CHECK (monat BETWEEN 1 AND 12),
    jahr INTEGER NOT NULL CHECK (jahr BETWEEN 1900 AND 2100),

    -- Brutto
    brutto_gesamt DECIMAL(12,2),
    grundgehalt DECIMAL(12,2),
    ueberstunden DECIMAL(10,2),
    zulagen DECIMAL(10,2),
    sonderzahlungen DECIMAL(10,2), -- Urlaubs-/Weihnachtsgeld

    -- Abzüge
    lohnsteuer DECIMAL(10,2),
    solidaritaetszuschlag DECIMAL(10,2),
    kirchensteuer DECIMAL(10,2),
    krankenversicherung DECIMAL(10,2),
    rentenversicherung DECIMAL(10,2),
    arbeitslosenversicherung DECIMAL(10,2),
    pflegeversicherung DECIMAL(10,2),

    -- Sonstige Abzüge
    betriebliche_altersvorsorge DECIMAL(10,2),
    vermoegenswirksame_leistungen DECIMAL(10,2),
    sonstige_abzuege DECIMAL(10,2),

    -- Netto
    netto_gesamt DECIMAL(12,2),

    -- Automatisch aus OCR?
    automatisch_erfasst BOOLEAN DEFAULT false,
    manuell_geprueft BOOLEAN DEFAULT false,
    geprueft_von UUID REFERENCES users(id),
    geprueft_am TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(case_id, person, monat, jahr)
);

-- =============================================================================
-- ASSETS TABLE (Vermögensgegenstände)
-- =============================================================================
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,

    eigentuemer VARCHAR(50) NOT NULL, -- 'mandant', 'gegner', 'gemeinsam'
    kategorie VARCHAR(50) NOT NULL, -- 'immobilie', 'fahrzeug', 'konto', 'wertpapier', 'sonstig'
    bezeichnung VARCHAR(255) NOT NULL,
    beschreibung TEXT,

    -- Werte
    wert_anfang DECIMAL(14,2), -- Wert bei Eheschließung
    wert_anfang_datum DATE,
    wert_ende DECIMAL(14,2), -- Wert bei Stichtag
    wert_ende_datum DATE,

    -- Für privilegierte Erwerbe (Erbschaft/Schenkung)
    ist_privilegiert BOOLEAN DEFAULT false,
    privilegierter_erwerb_art VARCHAR(50), -- 'erbschaft', 'schenkung'
    privilegierter_erwerb_datum DATE,
    privilegierter_erwerb_wert DECIMAL(14,2),

    -- Verbindlichkeiten
    verbindlichkeit DECIMAL(14,2) DEFAULT 0,
    verbindlichkeit_datum DATE,

    -- Dokumente
    nachweis_vorhanden BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- CALCULATIONS TABLE (Gespeicherte Berechnungen)
-- =============================================================================
CREATE TABLE calculations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id),

    berechnungsart VARCHAR(50) NOT NULL, -- 'kindesunterhalt', 'ehegattenunterhalt', 'zugewinn', 'rvg'
    titel VARCHAR(255),
    beschreibung TEXT,

    -- Eingabewerte und Ergebnis als JSONB
    eingabewerte JSONB NOT NULL,
    ergebnis JSONB NOT NULL,

    -- Versionsinfo
    version VARCHAR(20),
    tabellen_stand DATE, -- z.B. Düsseldorfer Tabelle Datum

    -- Freigabe
    mandant_sichtbar BOOLEAN DEFAULT false,
    freigabe_datum TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- DOCUMENT_REQUESTS TABLE (Dokumentenanforderungen)
-- =============================================================================
CREATE TABLE document_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,

    anforderung_art document_type NOT NULL,
    beschreibung TEXT NOT NULL,
    prioritaet VARCHAR(20) DEFAULT 'normal', -- 'niedrig', 'normal', 'hoch', 'dringend'

    angefordert_von UUID NOT NULL REFERENCES users(id),
    angefordert_am TIMESTAMPTZ DEFAULT NOW(),

    faellig_bis DATE,

    -- Status
    status VARCHAR(20) DEFAULT 'offen', -- 'offen', 'eingegangen', 'erledigt', 'storniert'
    erfuellt_durch UUID REFERENCES documents(id),
    erfuellt_am TIMESTAMPTZ,

    erinnerung_gesendet BOOLEAN DEFAULT false,
    erinnerung_datum TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- DUESSELDORFER_TABELLE TABLE (Jährliche Tabellenwerte)
-- =============================================================================
CREATE TABLE duesseldorfer_tabelle (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    gueltig_ab DATE NOT NULL,
    gueltig_bis DATE,

    -- Werte als JSONB (flexibel für Änderungen)
    einkommensgruppen JSONB NOT NULL,
    tabellenbetraege JSONB NOT NULL,
    bedarfskontrollbetraege JSONB NOT NULL,
    selbstbehalt JSONB NOT NULL,
    kindergeld INTEGER NOT NULL,

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(gueltig_ab)
);

-- =============================================================================
-- AUDIT_LOG TABLE (Protokollierung)
-- =============================================================================
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    user_id UUID REFERENCES users(id),
    action VARCHAR(50) NOT NULL, -- 'create', 'read', 'update', 'delete', 'login', 'logout'
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,

    old_values JSONB,
    new_values JSONB,

    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- INVITATIONS TABLE (Einladungscodes für Mandanten) - NEU
-- =============================================================================
CREATE TABLE invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,

    -- Code-Hash (nicht im Klartext speichern)
    code_hash VARCHAR(255) NOT NULL UNIQUE,

    -- Gültigkeit
    expires_at TIMESTAMPTZ NOT NULL,
    single_use BOOLEAN DEFAULT true,

    -- Verwendung
    used_at TIMESTAMPTZ,
    used_by UUID REFERENCES users(id),

    -- Ersteller
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- CASE_MEMBERSHIPS TABLE (Aktenzuordnung) - NEU
-- =============================================================================
CREATE TABLE case_memberships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    role_in_case VARCHAR(50) NOT NULL, -- 'mandant', 'gegner', 'anwalt', 'sachbearbeiter'

    -- Berechtigungen
    can_view_documents BOOLEAN DEFAULT true,
    can_upload_documents BOOLEAN DEFAULT true,
    can_view_calculations BOOLEAN DEFAULT false,
    can_approve_drafts BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(case_id, user_id)
);

-- =============================================================================
-- REQUEST_SLOTS TABLE (Strukturierte Upload-Slots) - NEU
-- =============================================================================
CREATE TABLE request_slots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID NOT NULL REFERENCES document_requests(id) ON DELETE CASCADE,

    slot_type document_type NOT NULL,
    label VARCHAR(255) NOT NULL, -- z.B. "Gehaltsabrechnung Januar 2026"
    beschreibung TEXT,

    -- Status
    status slot_status DEFAULT 'fehlend',

    -- Verknüpfung zum hochgeladenen Dokument
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,

    -- Reihenfolge
    sort_order INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- DRAFTS TABLE (Entwürfe zur Freigabe) - NEU
-- =============================================================================
CREATE TABLE drafts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,

    -- Art des Entwurfs
    draft_type VARCHAR(50) NOT NULL, -- 'schreiben_mandant', 'schreiben_gegner', 'schriftsatz_gericht'
    titel VARCHAR(255) NOT NULL,

    -- Inhalt
    content TEXT NOT NULL,
    content_html TEXT,

    -- Verknüpfte Berechnung (optional)
    calculation_id UUID REFERENCES calculations(id) ON DELETE SET NULL,

    -- Anlagen
    attachments JSONB, -- Array von document_ids

    -- Freigabe-Workflow
    requires_client_approval BOOLEAN DEFAULT false,
    approval_status approval_status DEFAULT 'ausstehend',

    -- Ersteller
    created_by UUID NOT NULL REFERENCES users(id),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- APPROVALS TABLE (Freigaben/Ablehnungen) - NEU
-- =============================================================================
CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Verknüpfung (einer der folgenden)
    draft_id UUID REFERENCES drafts(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    calculation_id UUID REFERENCES calculations(id) ON DELETE CASCADE,

    -- Freigabe-Details
    approved_by UUID NOT NULL REFERENCES users(id),
    status approval_status NOT NULL,
    comment TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraint: mindestens eine Verknüpfung erforderlich
    CONSTRAINT approval_has_entity CHECK (
        (draft_id IS NOT NULL)::int +
        (document_id IS NOT NULL)::int +
        (calculation_id IS NOT NULL)::int = 1
    )
);

-- =============================================================================
-- RULESETS TABLE (OLG-Regelwerke mit Versionierung) - NEU
-- =============================================================================
CREATE TABLE rulesets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    olg_name VARCHAR(100) NOT NULL,
    olg_bezirk VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,

    gueltig_ab DATE NOT NULL,
    gueltig_bis DATE,

    -- Status
    status ruleset_status DEFAULT 'pending',

    -- Alle Parameter als JSONB
    parameters JSONB NOT NULL,
    -- Struktur:
    -- {
    --   "berufsbedingte_aufwendungen": {"pauschal_prozent": 0.05, "minimum": 50, "maximum": 150},
    --   "altersvorsorge": {"prozent_vom_brutto": 0.04},
    --   "erwerbstaetigenbonus": 0.10,
    --   "selbstbehalt": {...},
    --   "methoden": {...}
    -- }

    -- Metadaten
    quelle_url VARCHAR(500),
    geprueft_von UUID REFERENCES users(id),
    geprueft_am TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(olg_bezirk, version)
);

-- =============================================================================
-- COURT_OLG_MAPPING TABLE (Gericht zu OLG Zuordnung) - NEU
-- =============================================================================
CREATE TABLE court_olg_mapping (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    gericht_name VARCHAR(200) NOT NULL,
    gericht_typ VARCHAR(50) NOT NULL, -- 'AG', 'LG', 'OLG'
    plz VARCHAR(10),
    ort VARCHAR(100),

    -- Zuordnung zum OLG-Bezirk
    olg_bezirk VARCHAR(100) NOT NULL,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(gericht_name, gericht_typ)
);

-- =============================================================================
-- OCR_QUEUE TABLE (OCR-Verarbeitungsqueue) - NEU
-- =============================================================================
CREATE TABLE ocr_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,

    status ocr_status DEFAULT 'pending',
    priority INTEGER DEFAULT 0, -- höher = wichtiger

    -- Verarbeitungsdetails
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Ergebnisse
    ocr_confidence DECIMAL(5,4), -- 0.0000 bis 1.0000
    extracted_data JSONB, -- Strukturierte Extraktion

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- PAYSLIP_EXTRACTIONS TABLE (Lohnabrechnungs-Extraktion) - NEU
-- =============================================================================
CREATE TABLE payslip_extractions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    income_record_id UUID REFERENCES income_records(id) ON DELETE SET NULL,

    -- Extrahierte Rohdaten
    raw_extraction JSONB NOT NULL,

    -- Confidence pro Feld
    field_confidence JSONB,

    -- Bestätigung
    confirmed BOOLEAN DEFAULT false,
    confirmed_by UUID REFERENCES users(id),
    confirmed_at TIMESTAMPTZ,

    -- Manuelle Korrekturen
    manual_corrections JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_auth_id ON users(auth_id);

-- Clients
CREATE INDEX idx_clients_user_id ON clients(user_id);
CREATE INDEX idx_clients_name ON clients(nachname, vorname);

-- Cases
CREATE INDEX idx_cases_client_id ON cases(client_id);
CREATE INDEX idx_cases_lawyer_id ON cases(lawyer_id);
CREATE INDEX idx_cases_case_number ON cases(case_number);
CREATE INDEX idx_cases_access_code ON cases(access_code);
CREATE INDEX idx_cases_status ON cases(status);

-- Documents
CREATE INDEX idx_documents_case_id ON documents(case_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_created_at ON documents(created_at);

-- Income Records
CREATE INDEX idx_income_records_case_id ON income_records(case_id);
CREATE INDEX idx_income_records_period ON income_records(jahr, monat);

-- Assets
CREATE INDEX idx_assets_case_id ON assets(case_id);
CREATE INDEX idx_assets_kategorie ON assets(kategorie);

-- Calculations
CREATE INDEX idx_calculations_case_id ON calculations(case_id);
CREATE INDEX idx_calculations_type ON calculations(berechnungsart);

-- Audit Log
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);

-- =============================================================================
-- ROW LEVEL SECURITY POLICIES
-- =============================================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE opponents ENABLE ROW LEVEL SECURITY;
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE income_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE calculations ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_requests ENABLE ROW LEVEL SECURITY;

-- Policies werden basierend auf den Auth-Anforderungen implementiert
-- Beispiel für cases:

-- Anwälte können ihre eigenen Fälle sehen
CREATE POLICY "Anwälte sehen eigene Fälle"
    ON cases FOR SELECT
    USING (
        lawyer_id IN (
            SELECT id FROM users
            WHERE auth_id = auth.uid()
            AND role IN ('anwalt', 'admin')
        )
    );

-- Mandanten können ihre eigenen Fälle sehen
CREATE POLICY "Mandanten sehen eigene Fälle"
    ON cases FOR SELECT
    USING (
        client_id IN (
            SELECT id FROM clients
            WHERE user_id IN (
                SELECT id FROM users WHERE auth_id = auth.uid()
            )
        )
    );

-- Admins können alles sehen
CREATE POLICY "Admins sehen alles"
    ON cases FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE auth_id = auth.uid()
            AND role = 'admin'
        )
    );

-- =============================================================================
-- FUNCTIONS
-- =============================================================================

-- Funktion zum Generieren von Aktenzeichen
CREATE OR REPLACE FUNCTION generate_case_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    jahr INTEGER;
    laufnummer INTEGER;
    neues_aktenzeichen VARCHAR(50);
BEGIN
    jahr := EXTRACT(YEAR FROM CURRENT_DATE);

    SELECT COALESCE(MAX(
        CAST(SUBSTRING(case_number FROM '[0-9]+$') AS INTEGER)
    ), 0) + 1
    INTO laufnummer
    FROM cases
    WHERE case_number LIKE jahr || '/%';

    neues_aktenzeichen := jahr || '/' || LPAD(laufnummer::TEXT, 4, '0');

    RETURN neues_aktenzeichen;
END;
$$ LANGUAGE plpgsql;

-- Funktion zum Generieren von Zugangscodes
CREATE OR REPLACE FUNCTION generate_access_code()
RETURNS VARCHAR(20) AS $$
DECLARE
    chars VARCHAR(62) := 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789';
    code VARCHAR(20) := '';
    i INTEGER;
BEGIN
    FOR i IN 1..12 LOOP
        code := code || SUBSTR(chars, FLOOR(RANDOM() * LENGTH(chars) + 1)::INTEGER, 1);
    END LOOP;
    RETURN code;
END;
$$ LANGUAGE plpgsql;

-- Trigger für automatisches Aktenzeichen
CREATE OR REPLACE FUNCTION set_case_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.case_number IS NULL OR NEW.case_number = '' THEN
        NEW.case_number := generate_case_number();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_case_number
    BEFORE INSERT ON cases
    FOR EACH ROW
    EXECUTE FUNCTION set_case_number();

-- Trigger für automatischen Zugangscode
CREATE OR REPLACE FUNCTION set_access_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.access_code IS NULL THEN
        NEW.access_code := generate_access_code();
        NEW.access_code_valid_until := NOW() + INTERVAL '90 days';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_access_code
    BEFORE INSERT ON cases
    FOR EACH ROW
    EXECUTE FUNCTION set_access_code();

-- Trigger für updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Updated_at Trigger für alle relevanten Tabellen
CREATE TRIGGER trigger_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trigger_clients_updated_at BEFORE UPDATE ON clients FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trigger_opponents_updated_at BEFORE UPDATE ON opponents FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trigger_cases_updated_at BEFORE UPDATE ON cases FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trigger_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trigger_income_records_updated_at BEFORE UPDATE ON income_records FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trigger_assets_updated_at BEFORE UPDATE ON assets FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trigger_calculations_updated_at BEFORE UPDATE ON calculations FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

-- OLG Schleswig-Holstein Leitlinien 2025
INSERT INTO olg_guidelines (
    olg_name,
    olg_bezirk,
    gueltig_ab,
    berufsbedingte_aufwendungen,
    altersvorsorge,
    erwerbstaetigenbonus,
    selbstbehalt,
    besonderheiten
) VALUES (
    'Schleswig-Holsteinisches Oberlandesgericht',
    'Schleswig',
    '2025-01-01',
    '{"pauschal_prozent": 0.05, "minimum": 50, "maximum": 150}',
    '{"prozent_vom_brutto": 0.04}',
    0.10,
    '{"minderjaehrig_erwerbstaetig": 1450, "minderjaehrig_nicht_erwerbstaetig": 1200, "volljaehrig": 1750, "ehegatte_erwerbstaetig": 1600, "ehegatte_nicht_erwerbstaetig": 1475, "eltern": 2650}',
    '{"selbstaendige_durchschnitt_jahre": 3, "wohnvorteil": "objektiver_mietwert_abzgl_belastungen"}'
);

-- Düsseldorfer Tabelle 2025
INSERT INTO duesseldorfer_tabelle (
    gueltig_ab,
    einkommensgruppen,
    tabellenbetraege,
    bedarfskontrollbetraege,
    selbstbehalt,
    kindergeld
) VALUES (
    '2025-01-01',
    '{"1": [0, 2100], "2": [2101, 2500], "3": [2501, 2900], "4": [2901, 3300], "5": [3301, 3700], "6": [3701, 4100], "7": [4101, 4500], "8": [4501, 4900], "9": [4901, 5300], "10": [5301, 5700], "11": [5701, 6400], "12": [6401, 7200], "13": [7201, 8200], "14": [8201, 9700], "15": [9701, 11200]}',
    '{"1": {"0": 482, "1": 554, "2": 649, "3": 693}, "2": {"0": 507, "1": 582, "2": 682, "3": 728}, "3": {"0": 531, "1": 610, "2": 714, "3": 763}, "4": {"0": 555, "1": 638, "2": 747, "3": 797}, "5": {"0": 579, "1": 665, "2": 779, "3": 832}, "6": {"0": 617, "1": 710, "2": 831, "3": 888}, "7": {"0": 656, "1": 754, "2": 883, "3": 943}, "8": {"0": 695, "1": 798, "2": 935, "3": 998}, "9": {"0": 733, "1": 843, "2": 987, "3": 1054}, "10": {"0": 772, "1": 887, "2": 1039, "3": 1109}, "11": {"0": 810, "1": 931, "2": 1090, "3": 1164}, "12": {"0": 849, "1": 976, "2": 1142, "3": 1220}, "13": {"0": 888, "1": 1020, "2": 1194, "3": 1275}, "14": {"0": 927, "1": 1065, "2": 1247, "3": 1331}, "15": {"0": 965, "1": 1109, "2": 1299, "3": 1387}}',
    '{"1": 1200, "2": 1500, "3": 1600, "4": 1700, "5": 1800, "6": 1900, "7": 2000, "8": 2100, "9": 2200, "10": 2300, "11": 2400, "12": 2500, "13": 2600, "14": 2700, "15": 2800}',
    '{"minderjaehrig_erwerbstaetig": 1450, "minderjaehrig_nicht_erwerbstaetig": 1200, "volljaehrig": 1750}',
    255
);
