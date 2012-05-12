from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Card import *

from learnX.utils.Log import *
from learnX.utils.Utils import *

class CardDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def insertAll(self, cards):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        for card in cards:
            if card.deck:
                card.deckId = card.deck.id
            if card.note:
                card.noteId = card.note.id
            
            t = (card.deckId, card.noteId, card.ankiCardId, card.interval, card.status, card.statusChanged, card.lastUpdated)
            c.execute("Insert into Cards(deck_id, note_id, anki_card_id, interval, status, status_changed, last_updated)"
                      "Values (?,?,?,?,?,?,?)", t)
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
            card = Card(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[0])
            card.deck = deck

        c.close()
        
        return card
    
    def getCardsOrderByScore(self, decksId):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        sql = "Select c.id, c.deck_id, c.note_id, c.anki_card_id, c.interval, c.status, c.status_changed, c.last_updated, d.anki_deck_id, f.score "
        sql += "From Decks d, Cards c, Notes f "
        sql += "Where c.note_id = f.id and c.deck_id = d.id and c.status = 0 and d.id in %s" % Utils.ids2str(decksId)
        sql += " order by f.score asc"
        
        c.execute(sql)
        
        cards = []
        for row in c:
            card = Card(row[1],row[2],row[3],row[5],row[6],row[7],row[0])
            card.ankiDeckId = row[8]
            card.score = int(row[9])
            cards.append(card)

        c.close()
        
        return cards
    
    def getCardsByMorphemeId(self, morphemeId):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        t = (morphemeId)
        c.execute("select c.id, c.deck_id,  c.note_id, c.anki_card_id, c.interval, c.status, c.status_changed, c.last_updated "
                  "From Cards c, Notes f, NotesMorphemes fm where c.note_id = f.id and f.id = fm.note_id and fm.morpheme_id = 1", t)
        
        card = None
        for row in c:
            card = Card(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[0])

        c.close()
        
        return card

    def getAllNewCards(self, decksId):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        sql = "select c.id, c.deck_id,  c.note_id, c.anki_card_id, c.interval, c.status, c.status_changed, c.last_updated, d.anki_deck_id "
        sql += "from Cards c, Decks d where c.status = 0 and c.deck_id = d.id "
        
        t = []
        if decksId != None and len(decksId) > 0:
            sql += "and ("
            i = 1
            for deckId in decksId:
                t.append(deckId)
                sql += "d.id = ?"
                if i < len(decksId):
                    sql += " or "
                i += 1
            sql += ")"
        
        if len(t) > 0:
            c.execute(sql, t)
        else:
            c.execute(sql)
        
        cards = []
        for row in c:
            card = Card(row[1],row[2],row[3],row[5],row[6],row[7],row[0])
            card.ankiDeckId = row[8]
            cards.append(card)
        
        return cards

    def updateAll(self, cards):
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        
        for card in cards:
            if card.deck:
                card.deckId = card.deck.id
            if card.note:
                card.noteId = card.note.id
            
            t = (card.deckId, card.noteId, card.ankiCardId, card.interval, card.status, card.statusChanged, card.lastUpdated, card.id)
            c.execute("Update Cards Set deck_id = ?, note_id = ?, anki_card_id = ?, interval = ?, status = ?, status_changed = ?, last_updated = ?"
                      "Where id = ?", t)
            
        db.commit()
        c.close()
        
        return cards
