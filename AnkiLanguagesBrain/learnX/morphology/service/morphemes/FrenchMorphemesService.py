
from learnX.morphology.service.MorphemesService import *


class FrenchMorphemesService(MorphemesService):
    
    def __init__(self, serviceLocator):
        MorphemesService.__init__(self, serviceLocator)
    
    def rankMorpheme(self, knownDb, expression):
        score = len(expression) * 30
        if expression <= 4:
            return score
        for knownExpression in knownDb:
            if knownExpression == expression:
                return 0
        for knownExpression in knownDb:
            i = len(knownExpression)
            j = len(expression)
            if i == j:
                return score
            if i > j:
                if knownExpression.find(expression) >= 0:
                    return score * 0.5
            else:
                if expression.find(knownExpression) >= 0:
                    return score * 0.5
        return score
    
    def filterMorphLemmes(self, morphLemmesList):
        for morphLemme in morphLemmesList:
            morphLemme.pos = ""
        return morphLemmesList