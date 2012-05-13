from learnX.utils.Log import *

class Morpheme:
    
    STATUS_NONE = 0
    STATUS_LEARNT = 1
    STATUS_KNOWN = 2
    STATUS_MATURE = 3
    
    def __init__(self, noteId, interval, changed, morphLemmeId, score, id = -1):
        self.id = id
        self.noteId = noteId
        self.interval = interval
        self.changed = changed
        self.morphLemmeId = morphLemmeId
        self.score = score
        
    def __ne__(self, o):
        return not self.__eq__(o)
    
    def __eq__(self, o):
        if not isinstance(o, Morpheme): return False
        if self.morphLemmeId != o.morphLemmeId: return False
        return True

    def __hash__(self):
        return self.morphLemmeId
        
    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.interval), str(self.changed), str(self.morphLemmeId), str(self.score)])
    
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
        