from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Card import *

from learnX.utils.Log import *
from learnX.utils.Utils import *

class CardDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def persistCards(self, cards):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        toInsert = list()
        for card in cards:
            t = (card.id, )
            c.execute("Select * From Cards Where id = ?", t)
            
            row = c.fetchone()
            if row:
                card.__init__(row[0], row[1], row[2], row[3], row[4], row[5])
            else:
                toInsert.append(card)
        c.close()
        
        c = db.cursor()
        for card in toInsert:
             t = (card.id, card.deckId, card.noteId, card.interval, card.changed, card.lastUpdated)
             c.execute("Insert into Cards(id, deck_id, note_id, interval, changed, last_updated)"
                       "Values (?,?,?,?,?,?)", t)
        db.commit()
        c.close()
        
        return cards

    def updateCards(self, cards):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        for card in cards:            
            t = (card.deckId, card.noteId, card.interval, card.changed, card.lastUpdated, card.id)
            c.execute("Update Cards Set deck_id = ?, note_id = ?, interval = ?, changed = ?, last_updated = ?"
                      "Where id = ?", t)
            
        db.commit()
        c.close()
        
        return cards
