from learnX.utils.Log import *

class Morpheme:
    
    STATUS_NONE = 0
    STATUS_LEARNT = 1
    STATUS_KNOWN = 2
    STATUS_MATURE = 3
    
    def __init__(self, status, statusChanged, morphLemmeId, morphLemme, score, id = -1):
        self.id = id
        self.status = status
        self.statusChanged = statusChanged
        self.morphLemmeId = morphLemmeId
        self.morphLemme = morphLemme
        self.score = score
        if self.morphLemme:
            self.morphLemme.parent = self
    
    def __ne__(self, o):
        return not self.__eq__(o)
    
    def __eq__(self, o):
        if not isinstance(o, Morpheme): return False
        if self.morphLemme != o.morphLemme: return False
        return True

    def __hash__(self):
        return hash(self.morphLemme)
        
    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.status), str(self.status), str(self.morphLemmeId), str(self.score)])
    
    def getStatusName(self):
        if self.status == self.STATUS_NONE:
            return "None"
        if self.status == self.STATUS_LEARNT:
            return "Learnt"
        if self.status == self.STATUS_KNOWN:
            return "Known"
        if self.status == self.STATUS_MATURE:
            return "Mature"
        return "None"
        