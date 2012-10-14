
class Deck:
    
    LEARNX_SCORE_KEY = "LearnXScore"
    VOCAB_SCORE_KEY = "VocabScore"
    UNKNOWNS_KEY = "Unknown"
    KNOWNS_KEY = "Knowns"
    COPY_UNKNOWN_1_TO_KEY = "Copy1Unknown"
    DEFINITION_SCORE_KEY = "DefinitionScore"
    
    def __init__(self, id, enabled, firstTime, languageId, expressionField,
                 fields, total = 0, known = 0, posOptions = None, definitionField = None,
                 definitionKeyField = None):
        self.id = id
        self.enabled = enabled
        self.firstTime = firstTime
        self.languageId = languageId
        self.language = None
        if expressionField != None:
            self.expressionField = expressionField
        else:
            self.expressionField = "Expression"
        if fields:
            self.fields = fields
        else:
            self.fields = {
                self.LEARNX_SCORE_KEY : ("LearnXScore", False, True),
                self.VOCAB_SCORE_KEY : ("VocabScore", False, True),
                self.UNKNOWNS_KEY : ("UnknownMorphemes", False, False),
                self.KNOWNS_KEY : ("KnownMorphemes", False, False),
                self.COPY_UNKNOWN_1_TO_KEY : ("VocabExpression", False, False),
                self.DEFINITION_SCORE_KEY : ("DefinitionScore", False, False)
            }
        self.fieldsList = [self.LEARNX_SCORE_KEY, self.VOCAB_SCORE_KEY, self.UNKNOWNS_KEY,
                           self.KNOWNS_KEY, self.COPY_UNKNOWN_1_TO_KEY, self.DEFINITION_SCORE_KEY]
        self.totalMorphemes = total
        self.knownMorphemes = known
        if posOptions == None:
            self.posOptions = {"disabledPos" : list()}
        else:
            self.posOptions = posOptions
        self.definitionField = definitionField
        self.definitionKeyField = definitionKeyField

    def __ne__(self, o):
        return not self.__eq__(o)
        
    def __eq__(self, o):
        if not isinstance(o, Deck): return False
        if self.id != o.id: return False
        return True

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return u'\t'.join([str(self.id), str(self.enabled), str(self.firstTime), str(self.languageId), self.expressionField,
                           str(self.fields), str(self.totalMorphemes), str(self.knownMorphemes)])