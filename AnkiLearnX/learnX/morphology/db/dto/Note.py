
class Note:
    
    STATUS_NONE = 0
    STATUS_REVIEW = 10
    STATUS_LEARN = 20    
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

    def getStatusTag(self):
        if self.status == self.STATUS_NONE:
            return u'LxNone'
        if self.status == self.STATUS_REVIEW:
            return u'LxRev'
        if self.status == self.STATUS_LEARN:
            return u'LxLearn'
        if self.status == self.STATUS_TOO_DIFFICULT:
            return u'LxTooDifficult'   
        return u'LxNone'
    
    def getAllStatusTag(self):
        return u'LxNone LxRev LxLearn LxTooDifficult'

    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.deckId), str(self.ankiNoteId),str(self.lastUpdated),
                           str(self.expressionCsum), str(self.morphemesChanged), str(self.status),
                           str(self.score), str(self.statusChanged)])
