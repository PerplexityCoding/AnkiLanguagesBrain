from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Deck import *

from learnX.morphology.db.dto.Morpheme import *

from learnX.utils.Log import *

import pickle

class DeckDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    # Unused
    def list(self):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        c.execute("select * from Decks")
        
        decks = []
        for row in c:
            deck = Deck(row[1], row[2], row[3], row[4], row[5], row[6], row[0], row[7], row[8], row[9], row[10], row[11], row[12], row[13])
            if deck.fields:
                deck.fields = pickle.loads(str(deck.fields))
            decks.append(deck)
        
        c.close()
        
        return decks
    
    def insert(self, deck):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        deckFields = deck.fields
        if deckFields:
            deckFields = sqlite3.Binary(pickle.dumps(deckFields, 2))
            
        t = (deck.name, deck.path, deck.enabled, deck.languageId, deck.expressionField, deckFields,
             deck.matureTreshold, deck.knownTreshold, deck.learnTreshold, deck.totalMorphemes, deck.learntMorphemes, deck.knownMorphemes,
             deck.matureMorphemes)
        c.execute("Insert into Decks(deck_name, deck_path, enabled, language_id, expression_field,"
                  "deck_fields, mature_treshold, known_treshold, learn_treshold,"
                  "total_morphemes, learnt_morphemes, known_morphemes, mature_morphemes) "
                  "Values (?,?,?,?,?,?,?,?,?,?,?,?,?)", t)
        db.commit()
        c.close()
        
        c = db.cursor()
        
        u = (deck.name, deck.path)
        c.execute("Select id From Decks Where deck_name = ? and deck_path = ?", u)
        for row in c:
            deck.id = row[0]
        c.close()
        
        return deck
        
    def update(self, deck):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        if deck.language:
            deck.languageId = deck.language.id
        deckFields = deck.fields
        if deckFields:
            deckFields = sqlite3.Binary(pickle.dumps(deckFields, 2))
        
        t = (deck.name, deck.path, deck.enabled, deck.languageId, deck.expressionField, deckFields,
             deck.matureTreshold, deck.knownTreshold, deck.learnTreshold,
             deck.totalMorphemes, deck.learntMorphemes, deck.knownMorphemes, deck.matureMorphemes, deck.id)
        c.execute("Update Decks Set deck_name = ?, deck_path = ?, enabled = ?, language_id = ?, "
                  "expression_field = ?, deck_fields = ?, mature_treshold = ?, known_treshold = ?, learn_treshold = ?, "
                  "total_morphemes = ?, learnt_morphemes = ?, known_morphemes = ?, mature_morphemes = ? "
                  "Where id = ?", t)
        
        db.commit()
        c.close()
        
        return self.findByName(deck.name, deck.path)
        
    def findByName(self, name, path):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (name, path)
        c.execute("Select * From Decks Where deck_name = ? and deck_path = ?", t)
        
        deck = None
        for row in c:
            deck = Deck(row[1], row[2], row[3], row[4], row[5], row[6], row[0], row[7], row[8], row[9], row[10], row[11], row[12], row[13])
            if deck.fields:
                deck.fields = pickle.loads(str(deck.fields))
            
        db.commit()
        c.close()

        return deck
    
    def countMorphemes(self, deck):
        db = self.learnXdB.openDataBase()
        
        sql = "Select count (distinct fm.morpheme_id) From FactsMorphemes fm, Facts f "
        sql += "Where f.id = fm.fact_id and f.deck_id = ?"
        
        c = db.cursor()
        t = (deck.id,)
        c.execute(sql, t)
        row = c.fetchone()
        deck.totalMorphemes = 0
        if row:
            deck.totalMorphemes = row[0]
        c.close
        
        sql = "Select count (distinct fm.morpheme_id) From FactsMorphemes fm, Facts f, Morphemes m "
        sql += "Where f.id = fm.fact_id and f.deck_id = ? and fm.morpheme_id = m.id and m.status = ?"
        
        c = db.cursor()
        t = (deck.id, Morpheme.STATUS_LEARNT)
        c.execute(sql, t)
        row = c.fetchone()
        deck.learntMorphemes = 0
        if row:
            deck.learntMorphemes = row[0]
        c.close
        
        c = db.cursor()
        t = (deck.id, Morpheme.STATUS_KNOWN)
        c.execute(sql, t)
        row = c.fetchone()
        deck.knownMorphemes = 0
        if row:
            deck.knownMorphemes = row[0]
        c.close
        
        c = db.cursor()
        t = (deck.id, Morpheme.STATUS_MATURE)
        c.execute(sql, t)
        row = c.fetchone()
        deck.matureMorphemes = 0
        if row:
            deck.matureMorphemes = row[0]
        c.close
    