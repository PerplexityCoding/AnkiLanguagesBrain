
class Language:
    def __init__(self, nameId, posType, id = -1):
        self.id = id
        self.nameId = nameId
        self.posType = posType

    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.nameId), str(self.posType)])
