from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Card import *

from learnX.utils.Log import *

class CardDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def insertAll(self, cards):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        for card in cards:
            if card.deck:
                card.deckId = card.deck.id
            if card.fact:
                card.factId = card.fact.id
            
            t = (card.deckId, card.factId, card.ankiCardId, card.status, card.statusChanged, card.lastUpdated)
            c.execute("Insert into Cards(deck_id, fact_id, anki_card_id, status, status_changed, last_updated)"
                      "Values (?,?,?,?,?,?)", t)
        db.commit()
        c.close()
        
        c = db.cursor()
        
        for card in cards:
            t = (card.deckId, card.ankiCardId)
            c.execute("Select id From Cards Where deck_id = ? and anki_card_id = ?", t)
            
            for row in c:
                card.id = row[0]
        
        c.close()

    def findById(self, deck, ankiCardId):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        t = (deck.id, ankiCardId)
        c.execute("Select * From Cards Where deck_id = ? and anki_card_id = ?", t)
        
        card = None
        for row in c:
            card = Card(row[1], row[2], row[3], row[4], row[5], row[6], row[0])
            card.deck = deck

        c.close()
        
        return card
    
    def getCardsByMorphemeId(self, morphemeId):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        t = (morphemeId)
        c.execute("select c.id, c.deck_id,  c.fact_id, c.anki_card_id, c.status, c.status_changed, c.last_updated "
                  "From Cards c, Facts f, FactsMorphemes fm where c.fact_id = f.id and f.id = fm.fact_id and fm.morpheme_id = 1", t)
        
        card = None
        for row in c:
            card = Card(row[1], row[2], row[3], row[4], row[5], row[6], row[0])

        c.close()
        
        return card
        
    def updateAll(self, cards):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        for card in cards:
            if card.deck:
                card.deckId = card.deck.id
            if card.fact:
                card.factId = card.fact.id
            
            t = (card.deckId, card.factId, card.ankiCardId, card.status, card.statusChanged, card.lastUpdated, card.id)
            c.execute("Update Cards Set deck_id = ?, fact_id = ?, anki_card_id = ?, status = ?, status_changed = ?, last_updated = ?"
                      "Where id = ?", t)
            
        db.commit()
        c.close()
        
        return cards
