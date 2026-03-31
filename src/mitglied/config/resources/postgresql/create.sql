-- Copyright (C) 2022 - present Juergen Zimmermann, Hochschule Karlsruhe
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <https://www.gnu.org/licenses/>.

-- TEXT statt varchar(n):
-- "There is no performance difference among these three types, apart from a few extra CPU cycles
-- to check the length when storing into a length-constrained column"

SET default_tablespace = mitgliedspace;

CREATE TYPE geschlecht AS ENUM ('MAENNLICH', 'WEIBLICH', 'DIVERS');
CREATE TYPE mitgliedsstatus AS ENUM ('AKTIV', 'INAKTIV');

CREATE TABLE IF NOT EXISTS mitglied (
    id              INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    version         INTEGER NOT NULL DEFAULT 0,
    vorname         TEXT NOT NULL,
    nachname        TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    geburtsdatum    DATE,
    telefonnummer   TEXT UNIQUE,
    geschlecht      geschlecht,
    mitgliedsstatus mitgliedsstatus,
    beitrittsdatum  DATE,
    interessen      JSONB,
    erzeugt         TIMESTAMP NOT NULL,
    aktualisiert    TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS mitglied_nachname_idx ON mitglied(nachname);

CREATE TABLE IF NOT EXISTS ausweis (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    ausstellungsdatum   DATE NOT NULL,
    ablaufdatum         DATE NOT NULL,
    mitglied_id         INTEGER NOT NULL UNIQUE REFERENCES mitglied ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ausweis_mitglied_id_idx ON ausweis(mitglied_id);

CREATE TABLE IF NOT EXISTS ausleihe (
    id              INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    ausleihdatum    DATE NOT NULL,
    rueckgabedatum  DATE NOT NULL,
    mitglied_id     INTEGER NOT NULL REFERENCES mitglied ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ausleihe_mitglied_id_idx ON ausleihe(mitglied_id);
