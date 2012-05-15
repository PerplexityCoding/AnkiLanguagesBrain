
class Card:
    
    def __init__(self, id, deckId, noteId, interval = -1, changed = False, lastUpdated = None):
        self.id = id
        self.deckId = deckId
        self.noteId = noteId
        self.interval = interval
        self.changed = changed
        self.lastUpdated = lastUpdated
        
    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.deckId), str(self.noteId), str(self.changed)])
