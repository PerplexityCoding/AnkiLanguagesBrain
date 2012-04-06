
class Deck:
    
    LEARNX_SCORE_KEY = "LearnXScore"
    VOCAB_SCORE_KEY = "VocabScore"
    
    UNKNOWNS_KEY = "Unknown"
    LEARNTS_KEY = "Learnts"
    KNOWNS_KEY = "Knowns"
    MATURES_KEY = "Matures"
    
    COPY_UNKNOWN_1_TO_KEY = "CopyUnknown"
    COPY_MATURE_TO_KEY = "CopyMature"

    DEFINITION_KEY = "Definition"
    DEFINITION_SCORE_KEY = "DefinitionScore"
    
    def __init__(self, name, path, enabled, languageId, expressionField,
                 fields, id = -1, matureTreshold = 21, knownTreshold = 7, learnTreshold = 3, 
                 total = 0, learnt = 0, known = 0, mature = 0, posOptions = None):
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
                self.VOCAB_SCORE_KEY : ("VocabScore", False, True),
                self.UNKNOWNS_KEY : ("UnknownMorphemes", False, False),
                self.LEARNTS_KEY : ("LearntMorphemes", False, False),
                self.KNOWNS_KEY : ("KnownMorphemes", False, False),
                self.MATURES_KEY : ("MatureMorphemes", False, False),
                self.COPY_UNKNOWN_1_TO_KEY : ("VocabExpression", False, False),
                self.COPY_MATURE_TO_KEY : ("SentenceExpression", False, False),
                self.DEFINITION_KEY : ("DefinitionExpression", False, False),
                self.DEFINITION_SCORE_KEY : ("DefinitionScore", False, False)
            }
        self.fieldsList = [self.LEARNX_SCORE_KEY, self.VOCAB_SCORE_KEY, self.UNKNOWNS_KEY, self.LEARNTS_KEY,
                           self.KNOWNS_KEY, self.MATURES_KEY, self.COPY_UNKNOWN_1_TO_KEY, self.COPY_MATURE_TO_KEY,
                           self.DEFINITION_KEY, self.DEFINITION_SCORE_KEY
        ]
        self.totalMorphemes = total
        self.learntMorphemes = learnt
        self.knownMorphemes = known
        self.matureMorphemes = mature
        if posOptions == None:
            self.posOptions = {"disabledPos" : list()}
        else :
            self.posOptions = posOptions

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