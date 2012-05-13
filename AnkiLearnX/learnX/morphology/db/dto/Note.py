
class Note:
    
    STATUS_NONE = 0
    
    STATUS_REVIEW_EASY = 10
    STATUS_REVIEW_MEDIUM = 11
    STATUS_REVIEW_HARD = 12
    
    STATUS_LEARN_EASY = 20
    STATUS_LEARN_MEDIUM = 21
    STATUS_LEARN_HARD = 22
    
    STATUS_TOO_DIFFICULT = 30 
    
    def __init__(self, id, lastUpdated = None, expressionCsum = None, morphemesChanged = False, status = 0,
                 statusChanged = False, score = 0):
        self.id = id
        self.lastUpdated = lastUpdated
        self.expressionCsum = expressionCsum
        self.morphemesChanged = morphemesChanged
        self.status = status
        self.statusChanged = statusChanged
        self.score = score

        #self.deck = None
        #self.ankiNote = None
        #self.morphemes = None

    def getStatusTag(self):
        if self.status == self.STATUS_NONE:
            return u'LxNone'
        if self.status == self.STATUS_REVIEW_EASY:
            return u'LxRev,LxRevEasy'
        if self.status == self.STATUS_REVIEW_MEDIUM:
            return u'LxRev,LxRevMedium'
        if self.status == self.STATUS_REVIEW_HARD:
            return u'LxRev,LxRevHard'
        if self.status == self.STATUS_LEARN_EASY:
            return u'LxLearn,LxLearnEasy'
        if self.status == self.STATUS_LEARN_MEDIUM:
            return u'LxLearn,LxLearnMedium'
        if self.status == self.STATUS_LEARN_HARD:
            return u'LxLearn,LxLearnHard'
        if self.status == self.STATUS_TOO_DIFFICULT:
            return u'LxTooDifficult'   
        return u'LxNone'
    
    def getAllStatusTag(self):
        return u'LxNone LxRev LxRevEasy LxRevMedium LxRevHard LxLearn LxLearnEasy LxLearnMedium LxLearnHard LxTooDifficult'

    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.deckId), str(self.ankiNoteId),str(self.lastUpdated),
                           str(self.expressionCsum), str(self.morphemesChanged), str(self.status),
                           str(self.score), str(self.statusChanged)])
