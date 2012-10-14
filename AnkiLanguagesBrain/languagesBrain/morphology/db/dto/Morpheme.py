from languagesBrain.utils.Log import *

class Morpheme:
    
    def __init__(self, noteId, interval, morphLemmeId, id = -1):
        self.id = id
        self.noteId = noteId
        self.interval = interval
        self.morphLemmeId = morphLemmeId
        
    def __ne__(self, o):
        return not self.__eq__(o)
    
    def __eq__(self, o):
        if not isinstance(o, Morpheme): return False
        if self.morphLemmeId != o.morphLemmeId: return False
        return True

    def __hash__(self):
        return self.morphLemmeId
        
    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.noteId), str(self.interval), str(self.morphLemmeId)])

        