
class Deck:
    
    LEARNX_SCORE_KEY = "LearnX Score"
    VOCAB_RANK_KEY = "Vocab Score"
    
    LEARNT_NB_KEY = "Learnt Count"
    KNOWN_NB_KEY = "Known Count"
    MATURE_NB_KEY = "Mature Count"
    
    UNKNOWNS_KEY = "Unknown"
    UNMATUES_KEY = "Unmature"
    
    COPY_UNKNOWN_1_TO_KEY = "Copy Unknown"
    COPY_MATURE_TO_KEY = "Copy Mature"
    
    def __init__(self, name, path, enabled, languageId, expressionField,
                 fields, id = -1, matureTreshold = 21, knownTreshold = 7, learnTreshold = 3, 
                 total = 0, learnt = 0, known = 0, mature = 0):
        self.id = id
        self.name = str(name)
        self.path = str(path)
        self.enabled = enabled
        self.languageId = languageId
        self.language = None
        if expressionField != None:
            self.expressionField = expressionField
        else:
            self.expressionField = "Expression"
        self.matureTreshold = matureTreshold
        self.knownTreshold = knownTreshold
        self.learnTreshold = learnTreshold
        if fields:
            self.fields = fields
        else:
            self.fields = {
                self.LEARNX_SCORE_KEY : ("LearnXScore", False, True),
                self.LEARNT_NB_KEY : ("LearntCount", False, True),
                self.KNOWN_NB_KEY : ("KnownCount", False, True),
                self.MATURE_NB_KEY : ("MatureCount", False, True),
                self.VOCAB_RANK_KEY : ("VocabScore", False, True),
                self.UNKNOWNS_KEY : ("UnknownMorphemes", False, False),
                self.UNMATUES_KEY : ("UnmatureMorphemes", False, False),
                self.COPY_UNKNOWN_1_TO_KEY : ("VocabExpression", False, False),
                self.COPY_MATURE_TO_KEY : ("SentenceExpression", False, False)
            }
        self.fieldsList = [self.LEARNX_SCORE_KEY, self.LEARNT_NB_KEY, self.KNOWN_NB_KEY, self.MATURE_NB_KEY,
                self.VOCAB_RANK_KEY, self.UNKNOWNS_KEY, self.UNMATUES_KEY, self.COPY_UNKNOWN_1_TO_KEY,
                self.COPY_MATURE_TO_KEY
        ]
        self.totalMorphemes = total
        self.learntMorphemes = learnt
        self.knownMorphemes = known
        self.matureMorphemes = mature

    def __ne__(self, o):
        return not self.__eq__(o)
        
    def __eq__(self, o):
        if not isinstance(o, Deck): return False
        if self.id != o.id: return False
        if self.name != o.name: return False
        if self.path != o.path: return False
        return True

    def __hash__(self):
        return hash((self.id, self.name, self.path))

    def __repr__(self):
        return u'\t'.join([self.name, self.path, str(self.enabled), str(self.languageId), self.expressionField,
                           str(self.fields), str(self.totalMorphemes), str(self.knownMorphemes), str(self.matureMorphemes)])