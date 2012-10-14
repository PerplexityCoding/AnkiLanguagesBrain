
class Language:
    
    ENGLISH = 1
    FRENCH = 2
    JAPANESE = 500
    
    def __init__(self, nameId, posTaggerId, id = -1, total = 0, known = 0, posOptions = None):
        self.id = id
        self.nameId = nameId
        self.posTaggerId = posTaggerId
        self.posOptions = posOptions
        self.totalMorphemes = total
        self.knownMorphemes = known
        self.lemmatizer = None

    def __ne__(self, o):
        return not self.__eq__(o)
    
    def __eq__(self, o):
        if not isinstance(o, Language): return False
        if self.id != o.id: return False
        return True

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.nameId), str(self.posTaggerId)])

