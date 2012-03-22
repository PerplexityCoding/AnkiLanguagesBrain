
class Fact:
    
    STATUS_NONE = 0
    
    STATUS_REVIEW_EASY = 10
    STATUS_REVIEW_MEDIUM = 11
    STATUS_REVIEW_HARD = 12
    
    STATUS_LEARN_EASY = 20
    STATUS_LEARN_MEDIUM = 21
    STATUS_LEARN_HARD = 22
    
    STATUS_TOO_DIFFICULT = 30 
    
    def __init__(self, deckId, ankiFactId, lastUpdated, expressionHash, morphemesChanged, status, statusChanged, score, id = -1):
        self.id = id
        self.deckId = deckId
        self.ankiFactId = ankiFactId
        self.lastUpdated = lastUpdated
        self.expressionHash = expressionHash
        self.morphemesChanged = morphemesChanged
        self.status = status
        self.statusChanged = statusChanged
        self.score = score
        self.deck = None
        self.ankiFact = None
        self.morphemes = None

    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.deckId), str(self.ankiFactId),str(self.lastUpdated),
                           str(self.expressionHash), str(self.morphemesChanged), str(self.status),
                           str(self.score), str(self.statusChanged)])
