
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
    
    def computeMorphemesScore(self, language):
        
        decksId = self.decksService.listDecksIdByLanguage(language)
        
        log("lemmeDao.getMorphemes() Start")
        allMorphemes = self.lemmeDao.getMorphemes(decksId)
        log("lemmeDao.getMorphemes() Stop")
        
        log("Rank Morphemes Start")
        rankDb = self.morphemeDao.getAllKnownBaseMorphemes()
        modifiedMorphemes = list()
        for morpheme in allMorphemes:
            score = self.rankMorpheme(rankDb, morpheme.morphLemme.base)
            if morpheme.score != score:
                morpheme.score = score
                morpheme.statusChanged = True #FIXME
                modifiedMorphemes.append(morpheme)
        log("Rank Morphemes Stop")
        
        self.morphemeDao.updateAll(modifiedMorphemes)
        
        return modifiedMorphemes
    
    def filterMorphLemmes(self, morphLemmesList):
        for morphLemme in morphLemmesList:
            morphLemme.pos = ""
        return morphLemmesList