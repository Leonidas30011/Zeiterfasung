	-- =========================================
-- SQLite 3: Zeiterfassung
-- =========================================
-- Hinweis: In SQLite müssen Foreign Keys explizit aktiviert werden.
PRAGMA foreign_keys = ON;

-- =========================================
-- Tabelle: personen
-- =========================================
create TABLE if not exists personen(
    id integer primary key autoincrement ,
    name text not null unique,
    role TEXT NOT NULL CHECK(role IN ('Chef', 'DEVELOPER', 'TESTER', 'Büro', 'Andere')),
    art TEXT NOT NULL CHECK(art IN ('Ja', 'Vollzeit', 'Teilzeit', 'Mini-Job', 'Extern'))

);


CREATE TABLE IF NOT EXISTS projekte (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL

);


CREATE TABLE if not exists buchungen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projekt_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    einstempelzeit TEXT NOT NULL,
    ausstempelzeit TEXT,

    FOREIGN KEY (projekt_id) REFERENCES projekte(id)
        ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES personen(id)
        ON DELETE RESTRICT ,

    CHECK (
        ausstempelzeit IS NULL
        OR ausstempelzeit >= einstempelzeit
    )
);
