from learnX.utils.Log import *

class MorphemeLemme:
    def __init__(self, base, inflected, pos, subPos, read, rank = 0, maxInterval = 0, score = 0, id = -1):
        if id == -1:
            id = hash((pos, subPos, read, base))
        self.id = id
        self.pos = pos
        self.subPos = subPos
        self.read = read
        self.base = base
        self.rank = rank
        self.maxInterval = maxInterval
        self.score = score

    def __ne__(self, o):
        return not self.__eq__(o)
        
    def __eq__(self, o):
        if not isinstance(o, MorphemeLemme): return False
        if self.id != o.id: return False
        return True

    def __hash__(self):
        return self.id
        
    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.pos), str(self.subPos), str(self.read), str(self.base),
                           str(self.rank), str(self.maxInterval), str(self.score)])
