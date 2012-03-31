from learnX.utils.Log import *

class MorphemeLemme:
    def __init__(self, base, inflected, pos, subPos, read, id = -1):
        self.id = id
        self.pos = pos
        self.subPos = subPos
        self.read = read
        self.base = base
        
    def __ne__(self, o):
        return not self.__eq__(o)
        
    def __eq__(self, o):
        if not isinstance(o, MorphemeLemme): return False
        if self.pos != o.pos: return False
        if self.subPos != o.subPos: return False
        if self.read != o.read: return False
        if self.base != o.base: return False
        return True

    def __hash__(self):
        return hash((self.pos, self.subPos, self.read, self.base))
        
    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.pos), str(self.subPos), str(self.read), str(self.base)])
