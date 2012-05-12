
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
	learnt_morphemes INTEGER,
	known_morphemes INTEGER,
	mature_morphemes INTEGER
);

CREATE TABLE Decks (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	anki_deck_id INTEGER NOT NULL,
	enabled INTEGER(1) NOT NULL,
	language_id INTEGER REFERENCES Languages(id),
	expression_field TEXT NOT NULL,
	deck_fields BLOB,
	mature_treshold INTEGER,
	known_treshold INTEGER,
	learn_treshold INTEGER,
	total_morphemes INTEGER,
	learnt_morphemes INTEGER,
	known_morphemes INTEGER,
	mature_morphemes INTEGER,
	pos_options BLOB,
	definition_field TEXT,
	definition_key_field TEXT
);

CREATE TABLE Notes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	deck_id INTEGER REFERENCES Decks(id),
	anki_note_id INTEGER NOT NULL,
	last_updated INTEGER,
	expression_hash TEXT,
	morphemes_changed INTEGER(1),
	status INTEGER(4),
	status_changed INTEGER(1),
	score INTEGER,
	UNIQUE (deck_id, anki_note_id)
);

CREATE TABLE Definitions (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	note_id INTEGER REFERENCES Notes(id),
	definition_hash TEXT,
	definition_key_hash TEXT,
	UNIQUE (note_id)
);

CREATE TABLE Cards (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	deck_id INTEGER REFERENCES Decks(id),
	note_id INTEGER REFERENCES Notes(id),
	anki_card_id INTEGER NOT NULL,
	interval INTEGER,
	status INTEGER(4),
	status_changed INTEGER(1),
	last_updated INTEGER,
	UNIQUE (deck_id, anki_card_id, note_id)
);

CREATE TABLE Morphemes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	note_id INTEGER REFERENCES Note(id),
	max_interval INTEGER,
	score INTEGER,
	changed INTEGER(1),
	morph_lemme_id NUMERIC NOT NULL
);

CREATE TABLE MorphemeLemmes (
	id NUMERIC PRIMARY KEY,
	pos TEXT NOT NULL,
	sub_pos TEXT,
	read TEXT NOT NULL,
	base TEXT NOT NULL,
	score INTEGER
);

PRAGMA encoding = "UTF-8";

