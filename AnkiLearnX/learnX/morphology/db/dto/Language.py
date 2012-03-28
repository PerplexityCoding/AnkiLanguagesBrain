
class Language:
    def __init__(self, nameId, posType, id = -1, total = 0, learnt = 0, known = 0, mature = 0):
        self.id = id
        self.nameId = nameId
        self.posType = posType
        self.totalMorphemes = total
        self.learntMorphemes = learnt
        self.knownMorphemes = known
        self.matureMorphemes = mature

    def __ne__(self, o):
        return not self.__eq__(o)
    
    def __eq__(self, o):
        if not isinstance(o, Language): return False
        if self.id != o.id: return False
        return True

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.nameId), str(self.posType)])
