
from learnX.utils.Log import *

from aqt import mw

#from anki.deck import DeckStorage
#from anki.notes import Note
#from anki.cards import Card

class AnkiHelper:
    
    @staticmethod
    def getCards(deckid):
        #deckname = mw.col.decks.get(deckid)["id"]
        cids = mw.col.decks.cids(deckid)
        
        ankiCards = list()
        for cid in cids:
            ankiCards.append(mw.col.getCard(cid))

        return ankiCards

    @staticmethod
    def getNoteIdToCardsDb(deck): # m Map NoteId {Card}
        d = {}
        for c in deck.s.query(Card).all():
            try:
                d[c.noteId].append(c)
            except KeyError:
                d[c.noteId] = [c]
        return d

    @staticmethod
    def closeDeck(deck): # Deck -> IO ()
        if deck.s:
            deck.s.rollback()
            deck.s.clear()
            deck.s.close()
        deck.engine.dispose()

