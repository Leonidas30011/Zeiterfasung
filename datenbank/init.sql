	-- =========================================
-- SQLite 3: Zeiterfassung
-- =========================================
-- Hinweis: In SQLite müssen Foreign Keys explizit aktiviert werden.
PRAGMA foreign_keys = ON;

-- =========================================
-- Tabelle: personen
-- =========================================
CREATE TABLE IF NOT EXISTS personen (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL UNIQUE,
    role    TEXT NOT NULL CHECK(role IN ('Chef', 'DEVELOPER', 'TESTER', 'Büro', 'Andere'))
);

-- Seed-Daten (nur wenn noch nicht vorhanden)
INSERT OR IGNORE INTO personen (name, role)
VALUES ('Leonidas', 'Chef');

-- =========================================
-- Tabelle: projekte
-- =========================================
CREATE TABLE IF NOT EXISTS projekte (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    person_id       INTEGER NOT NULL,

    -- Zeiten als ISO-8601 TEXT (z.B. '2026-01-29 09:00:00')
    einstempelzeit  TEXT NOT NULL,
    ausstempelzeit  TEXT,

    -- Optional: verhindert, dass Ausstempelzeit vor Einstempelzeit liegt
    CHECK (
        ausstempelzeit IS NULL
        OR ausstempelzeit >= einstempelzeit
    ),

    FOREIGN KEY (person_id)
        REFERENCES personen(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- Optionaler Index für häufige Abfragen
CREATE INDEX IF NOT EXISTS idx_projekte_person_id ON projekte(person_id);
CREATE INDEX IF NOT EXISTS idx_projekte_einstempelzeit ON projekte(einstempelzeit);
