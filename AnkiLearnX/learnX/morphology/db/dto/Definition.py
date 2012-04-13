
class Definition:
    
    def __init__(self, factId, definitionHash, definitionKeyHash, id = -1):
        self.id = id
        self.factId = factId
        self.definitionHash = definitionHash
        self.definitionKeyHash = definitionKeyHash
        
    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.factId), str(self.definitionHash), str(self.definitionKeyHash)])
