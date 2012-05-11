
class Card:
    
    STATUS_NONE = 0
    STATUS_LEARNT = 1
    STATUS_KNOWN = 2
    STATUS_MATURE = 3
    
    def __init__(self, deckId, factId, ankiCardId, status, statusChanged, lastUpdated = None, id = -1):
        self.id = id
        self.deckId = deckId
        self.factId = factId
        self.ankiCardId = ankiCardId
        self.status = status
        self.statusChanged = statusChanged
        self.lastUpdated = lastUpdated
        self.fact = None
        self.deck = None
        self.ankiCard = None
        self.morphemes = None
        self.score = 0

    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.deckId), str(self.factId), str(self.ankiCardId),
                           str(self.status), str(self.statusChanged)])
