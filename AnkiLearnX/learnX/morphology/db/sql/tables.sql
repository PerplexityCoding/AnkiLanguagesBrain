
DROP TABLE IF EXISTS Languages;
DROP TABLE IF EXISTS Decks;
DROP TABLE IF EXISTS Notes;
DROP TABLE IF EXISTS Definitions;
DROP TABLE IF EXISTS Cards;
DROP TABLE IF EXISTS Morphemes;
DROP TABLE IF EXISTS MorphemeLemmes;

CREATE TABLE Languages (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name_id INTEGER UNIQUE NOT NULL,
	pos_tagger_id INTEGER NOT NULL,
	pos_tagger_options BLOB,
	total_morphemes INTEGER,
	known_morphemes INTEGER
);

CREATE TABLE Decks (
	id INTEGER PRIMARY KEY,
	enabled INTEGER(1) NOT NULL,
	language_id INTEGER REFERENCES Languages(id),
	expression_field TEXT NOT NULL,
	deck_fields BLOB,
	total_morphemes INTEGER,
	known_morphemes INTEGER,
	pos_options BLOB,
	definition_field TEXT,
	definition_key_field TEXT
);

CREATE TABLE Notes (
	id INTEGER PRIMARY KEY,
	last_updated INTEGER,
	expression_csum TEXT,
	changed INTEGER(1),
	score INTEGER
);

CREATE TABLE Cards (
	id INTEGER PRIMARY KEY,
	deck_id INTEGER REFERENCES Decks(id),
	note_id INTEGER REFERENCES Notes(id),
	interval INTEGER,
	changed INTEGER(1),
	last_updated INTEGER
);

CREATE TABLE Definitions (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	note_id INTEGER REFERENCES Notes(id),
	definition_hash TEXT,
	definition_key_hash TEXT,
	UNIQUE (note_id)
);

CREATE TABLE Morphemes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	note_id INTEGER REFERENCES Note(id),
	interval INTEGER,
	changed INTEGER(1),
	morph_lemme_id NUMERIC NOT NULL,
	UNIQUE (note_id, morph_lemme_id)
);

CREATE TABLE MorphemeLemmes (
	id NUMERIC PRIMARY KEY,
	pos TEXT NOT NULL,
	sub_pos TEXT,
	read TEXT NOT NULL,
	base TEXT NOT NULL,
	rank INTEGER,
	max_interval INTEGER,
	score INTEGER,
	changed INTEGER(1)
);

PRAGMA encoding = "UTF-8";

