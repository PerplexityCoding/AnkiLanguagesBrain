from languagesBrain.morphology.db.LanguagesBrainDB import *
from languagesBrain.morphology.db.dto.Deck import *

from languagesBrain.morphology.db.dto.Morpheme import *

from languagesBrain.utils.Log import *

import pickle

class DeckDao:
    def __init__(self):
        self.LanguagesBrainDB = LanguagesBrainDB.getInstance()

    def listDecksByLanguage(self, languageId):
        
        db = self.LanguagesBrainDB.openDataBase()
        
        c = db.cursor()
        t = (languageId,)
        c.execute("select * from Decks Where language_id = ?", t)
        
        decks = []
        for row in c:
            deck = Deck(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
            if deck.fields:
                deck.fields = pickle.loads(str(deck.fields))
            if deck.posOptions:
                deck.posOptions = pickle.loads(str(deck.posOptions))
            decks.append(deck)
        
        c.close()
        
        return decks
        
    def insertDeck(self, deck):
        db = self.LanguagesBrainDB.openDataBase()
        c = db.cursor()
        
        deckFields = deck.fields
        posOptions = deck.posOptions
        if deckFields:
            deckFields = sqlite3.Binary(pickle.dumps(deckFields, 2))
        if posOptions:
            posOptions = sqlite3.Binary(pickle.dumps(posOptions, 2))
            
        t = (deck.id, deck.enabled, deck.firstTime, deck.languageId, deck.expressionField, deckFields,
             deck.totalMorphemes, deck.knownMorphemes, posOptions, deck.definitionField, deck.definitionKeyField)
        c.execute("Insert into Decks(id, enabled, first_time, language_id, expression_field, "
                  "deck_fields, total_morphemes, known_morphemes, pos_options, definition_field, definition_key_field) "
                  "Values (?,?,?,?,?,?,?,?,?,?,?)", t)
        db.commit()
        c.close()
        
        return deck
        
    def updateDeck(self, deck):
        
        db = self.LanguagesBrainDB.openDataBase()
        c = db.cursor()
        
        if deck.language:
            deck.languageId = deck.language.id
        deckFields = deck.fields
        posOptions = deck.posOptions
        if deckFields:
            deckFields = sqlite3.Binary(pickle.dumps(deckFields, 2))
        if posOptions:
            posOptions = sqlite3.Binary(pickle.dumps(posOptions, 2))
        
        t = (deck.enabled, deck.firstTime, deck.languageId, deck.expressionField, deckFields,
             deck.totalMorphemes, deck.knownMorphemes, posOptions, deck.definitionField, deck.definitionKeyField, deck.id)
        c.execute("Update Decks Set enabled = ?, first_time = ?, language_id = ?, expression_field = ?, deck_fields = ?, "
                  "total_morphemes = ?, known_morphemes = ?, pos_options = ?, definition_field = ?, definition_key_field = ? "
                  "Where id = ?", t)
        db.commit()
        c.close()
        
        return deck
        
    def resetFirstTime(self, deck):
        
        db = self.LanguagesBrainDB.openDataBase()
        c = db.cursor()
        
        t = (deck.id,)
        c.execute("Update Decks Set first_time = 0 Where id = ?", t)
        
        db.commit()
        c.close()
        
    def findDeckById(self, id):
        db = self.LanguagesBrainDB.openDataBase()
        c = db.cursor()
        
        t = (id,)
        c.execute("Select * From Decks Where id = ?", t)
        
        deck = None
        for row in c:
            deck = Deck(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
            if deck.fields:
                deck.fields = pickle.loads(str(deck.fields))
            if deck.posOptions:
                deck.posOptions = pickle.loads(str(deck.posOptions))
            
        db.commit()
        c.close()

        return deck
