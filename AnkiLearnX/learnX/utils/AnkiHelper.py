
from learnX.utils.Log import *

#from anki.deck import DeckStorage
#from anki.notes import Note
#from anki.cards import Card

class AnkiHelper:
    
    @staticmethod
    def getNotes(deck): # m LazyList Note
        return deck.s.query(Note).all()

    @staticmethod
    def getCards(deck):
        return deck.s.query(Card).all()

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

