
from learnX.morphology.db.dao.MorphemeLemmeDao import *
from learnX.morphology.db.dao.MorphemeDao import *
from learnX.morphology.db.dao.FactDao import *
from learnX.morphology.db.dao.CardDao import *
from learnX.morphology.db.dao.DeckDao import *

from learnX.morphology.db.dto.Card import *
from learnX.morphology.db.dto.Morpheme import *

from learnX.utils.Log import *
from learnX.utils.KanjiHelper import *

from learnX.morphology.lemmatizer.cst.CstLemmatizer import *

class MorphemesService:
    
    def __init__(self, serviceLocator):
        self.serviceLocator = serviceLocator
        
        self.lemmeDao = MorphemeLemmeDao()
        self.morphemeDao = MorphemeDao()
        self.factDao = FactDao()
        self.cardDao = CardDao()
        self.deckDao = DeckDao()
    
    def setupServices(self):
        self.decksService = self.serviceLocator.getDecksService()
        self.factsService = self.serviceLocator.getFactsService()

    def extractMorphemes(self, expression, language):
        
        morphemes = language.posTagger.posMorphemes(expression)
        #language.lemmatizer = CstLemmatizer()
        #if language.lemmatizer:
        #    morphemes = language.lemmatizer.lemmatizeMorphemes(morphemes)
        
        # Unique morphemes
        
        return morphemes
    
    def analyze(self, expression, language):
        morphemes = self.extractMorphemes(expression)
        return morphemes
    
    def analyzeMorphemes(self, facts, language):
        
        # Unique Morphemes
        allMorphLemmes = list()
        for fact in facts:
            morphLemmes = self.extractMorphemes(fact.expression, language)
            for morphLemme in morphLemmes:
                allMorphLemmes.append(morphLemme)
            fact.morphLemmes = morphLemmes
        
        if language.lemmatizer:
            language.lemmatizer.lemmatizeMorphemes(allMorphLemmes)
        
        allMorphemes = list()
        for fact in facts:
            factUniqueMorphemes = []
            for morphLemme in fact.morphLemmes:
                morpheme = Morpheme(Morpheme.STATUS_NONE, False, morphLemme.id, morphLemme, 0)
                
                uniqueMorpheme = None
                if morpheme not in allMorphemes:    
                    allMorphemes.append(morpheme)
                    uniqueMorpheme = morpheme
                else:
                    uniqueMorpheme = allMorphemes[allMorphemes.index(morpheme)]
                if uniqueMorpheme not in factUniqueMorphemes:
                    factUniqueMorphemes.append(uniqueMorpheme)
            fact.morphemes = factUniqueMorphemes
            fact.expressionHash = hash(fact.expression)
            fact.lastUpdated = fact.ankiLastModified
            fact.expression = None
        
        log("persistAll")
        self.lemmeDao.persistAll(allMorphemes)
        self.morphemeDao.persistAll(allMorphemes)
        
        log("insertAllFactMorphemes")
        self.factDao.insertAllFactMorphemes(facts)
        
        log("updateAll")
        self.factDao.updateAll(facts)
        
        for fact in facts:
            fact.morphLemmes = None
            fact.morphemes = None
    
    def computeMorphemesMaturity(self, cards):
        
        log("computeMorphemesMaturity")
        modifiedMorphemes = list()
        for card in cards:
            morphemes = self.morphemeDao.getMorphemesFromCard(card)
            #log("Morphemes: " + str(len(morphemes)))
            for morpheme in morphemes:
                if morpheme is not modifiedMorphemes:
                    status = self.morphemeDao.getNewStatus(morpheme)
                    #log("status: " + str(status))
                    if morpheme.status != status:
                        #log("status modified")
                        morpheme.status = status
                        morpheme.statusChanged = True
                        modifiedMorphemes.append(morpheme)
            card.lastUpdated = card.ankiLastModified

        self.morphemeDao.updateAll(modifiedMorphemes)
        self.cardDao.updateAll(cards)
    
    def analyze(self, fact):
        
        morphemes = self.extractMorphemes(fact.expression)
        
        attachedMorphemes = []
        for morpheme in morphemes:
            morpheme.morphLemme = self.lemmeDao.persist(morpheme.morphLemme)
            morpheme = self.morphemeDao.persist(morpheme)
            attachedMorphemes.append(morpheme)
        
        self.factsService.changeMorphemes(fact, attachedMorphemes)
        
        return morphemes
        
    def getAllPOS(self, language):
        try:
            return language.posOptions["activatedPos"]
        except Exception: pass
  
    def getAllSubPOS(self, language):
        try:
            return language.posOptions["activatedSubPos"]
        except Exception: pass
    
    def getMorphemes(self, searchText = None, decksId = None):
        
        if searchText == None or searchText == "":
            return self.lemmeDao.getMorphemes(decksId)
        else:
            searchExpressions = searchText.split(" ")
            status_changed = None
            status = None
            pos = None
            subPos = None
            expressions = []
            
            for searchExpression in searchExpressions:
                uni = unicode(searchExpression)
                if searchExpression == "is:changed":
                    status_changed = True
                elif searchExpression == "-is:changed":
                    status_changed = False
                elif searchExpression == "status:None":
                    status = Morpheme.STATUS_NONE
                elif searchExpression == "status:Learnt":
                    status = Morpheme.STATUS_LEARNT
                elif searchExpression == "status:Known":
                    status = Morpheme.STATUS_KNOWN
                elif searchExpression == "status:Mature":
                    status = Morpheme.STATUS_MATURE
                elif uni.startswith("pos:"):
                    pos = uni.split(":")[1]                    
                elif uni.startswith("sub_pos:"):
                    subPos = uni.split(":")[1]
                else:
                    expressions.append(uni)
            return self.lemmeDao.getMorphemes(decksId, expressions, status, status_changed, pos, subPos)