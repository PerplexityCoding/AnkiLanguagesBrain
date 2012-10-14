from languagesBrain.morphology.db.LearnXdB import *
from languagesBrain.morphology.db.dto.Card import *

from languagesBrain.utils.Log import *
from languagesBrain.utils.Utils import *

class CardDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def persistCards(self, cards):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        cardsHash = dict()
        for card in cards:
            cardsHash[card.id] = card
        
        c.execute("Select * From Cards Where id in (%s)" % ",".join(str(n.id) for n in cards))
        for row in c:
            cardsHash.pop(row[0]).__init__(row[0], row[1], row[2], row[3], row[4])
        c.close()
        
        if len(cardsHash) > 0:
            c = db.cursor()
            for card in cardsHash.values():
                 t = (card.id, card.deckId, card.noteId, card.interval, card.lastUpdated)
                 c.execute("Insert into Cards(id, deck_id, note_id, interval, last_updated)"
                           "Values (?,?,?,?,?)", t)
            db.commit()
            c.close()
        
        return cards

    def updateCards(self, cards):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        for card in cards:            
            t = (card.deckId, card.noteId, card.interval, card.lastUpdated, card.id)
            c.execute("Update Cards Set deck_id = ?, note_id = ?, interval = ?, last_updated = ? "
                      "Where id = ?", t)
            
        db.commit()
        c.close()
        
        return cards
    
    def selectAllCards(self):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        c.execute("Select c.id, n.score From Cards c, Notes n Where c.note_id = n.id")
        
        cards = list()
        for row in c:
            cards.append((row[0], row[1]))
        c.close()
        
        return cards
