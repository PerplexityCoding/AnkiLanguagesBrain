
from learnX.utils.Log import *

from anki.deck import DeckStorage
from anki.facts import Fact
from anki.cards import Card

class AnkiHelper:
    
    @staticmethod
    def getFacts(deck): # m LazyList Fact
        return deck.s.query(Fact).all()

    @staticmethod
    def getCards(deck):
        return deck.s.query(Card).all()

    @staticmethod
    def getFactIdToCardsDb(deck): # m Map FactId {Card}
        d = {}
        for c in deck.s.query(Card).all():
            try:
                d[c.factId].append(c)
            except KeyError:
                d[c.factId] = [c]
        return d

    @staticmethod
    def closeDeck(deck): # Deck -> IO ()
        if deck.s:
            deck.s.rollback()
            deck.s.clear()
            deck.s.close()
        deck.engine.dispose()
        
    @staticmethod
    def getDeck(dpath): # AnkiDeckPath -> Maybe Deck
        if not os.path.exists( dpath ):
            return log('! deck file not found @ %s' % dpath)
        try:
            return DeckStorage.Deck(dpath)
        except Exception, e:
            if hasattr(e, 'data') and e.data.get('type') == 'inuse':
                log( '! deck already open @ %s. skipping' % dpath )
            else:
                log( '!!! deck is corrupted: %s\nException was: %s' % (dpath, e) )
