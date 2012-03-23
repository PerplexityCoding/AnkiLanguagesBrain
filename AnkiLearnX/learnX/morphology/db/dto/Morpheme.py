from learnX.utils.Log import *

class Morpheme:
    
    STATUS_NONE = 0
    STATUS_LEARNT = 1
    STATUS_KNOWN = 2
    STATUS_MATURE = 3
    
    TYPE_MECAB = 1
    
    def __init__(self, status, statusChanged, type, morphId, morph, id = -1):
        self.id = id
        self.status = status
        self.statusChanged = statusChanged
        self.type = type
        self.morphId = morphId
        self.morph = morph
        if self.morph:
            self.morph.parent = self
    
    def __ne__(self, o):
        return not self.__eq__(o)
    
    def __eq__(self, o):
        if not isinstance(o, Morpheme): return False
        if self.morph != o.morph: return False
        return True

    def __hash__(self):
        return hash(self.morph)
        
    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.status), str(self.status), str(self.type), str(self.morph)])
    
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
        