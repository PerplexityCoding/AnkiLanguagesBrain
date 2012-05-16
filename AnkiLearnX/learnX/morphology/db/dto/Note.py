
class Note:
    
    def __init__(self, id, lastUpdated = None, expressionCsum = None, score = 0):
        self.id = id
        self.lastUpdated = lastUpdated
        self.expressionCsum = expressionCsum
        self.score = score

    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.lastUpdated), str(self.expressionCsum), str(self.score)])
