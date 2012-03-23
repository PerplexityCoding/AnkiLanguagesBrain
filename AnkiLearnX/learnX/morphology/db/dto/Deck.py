
class Deck:
    
    def __init__(self, name, path, enabled, languageId, expressionField,
                 fields, id = -1, matureTreshold = 21, knownTreshold = 7, learnTreshold = 3, 
                 total = 0, learnt = 0, known = 0, mature = 0):
        self.id = id
        self.name = str(name)
        self.path = str(path)
        self.enabled = enabled
        self.languageId = languageId
        self.language = None
        self.expressionField = expressionField
        self.matureTreshold = matureTreshold
        self.knownTreshold = knownTreshold
        self.learnTreshold = learnTreshold
        if fields:
            self.fields = fields
        else:
            self.fields = {
                ("LearnX Score", "morphManIndex", False),
                ("i+N Known", "iPlusN", False),
                ("i+N Mature", "iPlusNmature", False),
                ("Vocab Rank", "vocabRank", False),
                ("Unkowns", "unknowns", False),
                ("Unmatures", "unmatures", False),
                ("Copy i+1 Known", "vocabExpression", False),
                ("Copy i+0 Mature", "sentenceExpression", False)
            }
        self.totalMorphemes = total
        self.learntMorphemes = learnt
        self.knownMorphemes = known
        self.matureMorphemes = mature

    def __repr__(self):
        return u'\t'.join([self.name, self.path, str(self.enabled), str(self.languageId), self.expressionField,
                           str(self.fields), str(self.totalMorphemes), str(self.knownMorphemes), str(self.matureMorphemes)])