
class Card:
    
    STATUS_NONE = 0
    STATUS_LEARNT = 1
    STATUS_KNOWN = 2
    STATUS_MATURE = 3
    
    def __init__(self, id, deckId, noteId, interval = 0, status = 0, statusChanged = False, lastUpdated = None):
        self.id = id
        self.deckId = deckId
        self.noteId = noteId
        self.interval = interval
        self.status = status
        self.statusChanged = statusChanged
        self.lastUpdated = lastUpdated
        
        #self.note = None
        #self.deck = None
        #self.ankiCard = None
        #self.morphemes = None
        #self.score = 0

    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.deckId), str(self.noteId), str(self.status), str(self.statusChanged)])
