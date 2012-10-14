
class Definition:
    
    def __init__(self, noteId, definitionHash, definitionKeyHash, id = -1):
        self.id = id
        self.noteId = noteId
        self.definitionHash = definitionHash
        self.definitionKeyHash = definitionKeyHash
        
    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.noteId), str(self.definitionHash), str(self.definitionKeyHash)])
