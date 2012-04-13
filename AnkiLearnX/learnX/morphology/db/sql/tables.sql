
DROP TABLE IF EXISTS Languages;
DROP TABLE IF EXISTS Decks;
DROP TABLE IF EXISTS Facts;
DROP TABLE IF EXISTS Definitions;
DROP TABLE IF EXISTS Cards;
DROP TABLE IF EXISTS Morphemes;
DROP TABLE IF EXISTS FactsMorphemes;
DROP TABLE IF EXISTS DefinitionsMorphemes;
DROP TABLE IF EXISTS DefinitionsKeysMorphemes;
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
	deck_name TEXT UNIQUE NOT NULL,
	deck_path TEXT NOT NULL,
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

CREATE TABLE Facts (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	deck_id INTEGER REFERENCES Deck(id),
	anki_fact_id INTEGER NOT NULL,
	last_updated INTEGER,
	expression_hash TEXT,
	morphemes_changed INTEGER(1),
	status INTEGER(4),
	status_changed INTEGER(1),
	score INTEGER,
	UNIQUE (deck_id, anki_fact_id)
);

CREATE TABLE Definitions (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	fact_id INTEGER REFERENCES Facts(id),
	definition_hash TEXT,
	definition_key_hash TEXT,
	UNIQUE (fact_id)
);

CREATE TABLE Cards (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	deck_id INTEGER REFERENCES Deck(id),
	fact_id INTEGER REFERENCES Facts(id),
	anki_card_id INTEGER NOT NULL,
	status INTEGER(4),
	status_changed INTEGER(1),
	last_updated INTEGER,
	UNIQUE (deck_id, anki_card_id, fact_id)
);

CREATE TABLE Morphemes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	status INTEGER(4) NOT NULL,
	status_changed INTEGER(1),
	morph_lemme_id INTEGER NOT NULL,
	score INTEGER
);

CREATE TABLE FactsMorphemes (
	fact_id INTEGER REFERENCES Fact(id),
	morpheme_id INTEGER REFERENCES Morphemes(id),
	UNIQUE (fact_id, morpheme_id)
);

CREATE TABLE DefinitionsMorphemes (
	definition_id INTEGER REFERENCES Definitions(id),
	morpheme_id INTEGER REFERENCES Morphemes(id),
	UNIQUE (definition_id, morpheme_id)
);

CREATE TABLE DefinitionsKeysMorphemes (
	definition_id INTEGER REFERENCES Definitions(id),
	morpheme_id INTEGER REFERENCES Morphemes(id),
	UNIQUE (definition_id, morpheme_id)
);

CREATE TABLE MorphemeLemmes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	pos TEXT NOT NULL,
	sub_pos TEXT,
	read TEXT NOT NULL,
	base TEXT NOT NULL
);

PRAGMA encoding = "UTF-8";

