from learnX.morphology.service.Mecab import *
from learnX.morphology.service.FactsService import *

from learnX.morphology.db.dto.Morpheme import *
from learnX.morphology.db.dao.MecabMorphemeDao import *
from learnX.morphology.db.dao.MorphemeDao import *
from learnX.morphology.db.dao.FactDao import *
from learnX.morphology.db.dao.CardDao import *

from learnX.morphology.db.dto.Card import *

from learnX.utils.Log import *

class MorphemesService:
    
    def __init__(self):
        self.mecab = Mecab()
        self.mecabDao = MecabMorphemeDao()
        self.morphemeDao = MorphemeDao()
        self.factDao = FactDao()
        self.cardDao = CardDao()
        self.factService = FactsService()

    def extractMorphemes(self, expression):
        
        # if mecab:
        mecabMorphemes = self.mecab.getMorphemes(expression)
        morphemes = set()
        for mecabMorpheme in mecabMorphemes:
            morphemes.add(Morpheme(Morpheme.STATUS_NONE, False, Morpheme.TYPE_MECAB, mecabMorpheme.id, mecabMorpheme))
        
        return morphemes
    
    def analyze(self, expression):
        morphemes = self.extractMorphemes(expression)
        return morphemes
    
    def analyzeAll(self, facts):
        
        allMorphemes = list()
        # Unique Morphemes
        for fact in facts:
            fact.morphemes = self.extractMorphemes(fact.expression)
            factUniqueMorphemes = []
            for morpheme in fact.morphemes:
                uniqueMorpheme = None
                if morpheme not in allMorphemes:    
                    allMorphemes.append(morpheme)
                    uniqueMorpheme = morpheme
                else:
                    uniqueMorpheme = allMorphemes[allMorphemes.index(morpheme)]
                uniqueMorpheme.fact = fact
                factUniqueMorphemes.append(uniqueMorpheme)
            fact.morphemes = factUniqueMorphemes
            fact.expressionHash = hash(fact.expression)
            fact.lastUpdated = fact.ankiLastModified
            fact.expression = None
        
        self.mecabDao.persistAll(allMorphemes)
        self.morphemeDao.persistAll(allMorphemes)
        
        self.factDao.insertAllFactMorphemes(facts)
        
        self.factDao.updateAll(facts)
        
        for fact in facts:
            fact.morphemes = None
    
    def computeMorphemesMaturity(self, cards):
        
        log("computeMorphemesMaturity")
        morphemes_modified = list()
        for card in cards:
            morphemes = self.morphemeDao.getMorphemesFromCard(card)
            for morpheme in morphemes:
                if morpheme is not morphemes_modified:
                    status = self.morphemeDao.getNewStatus(morpheme)
                    if morpheme.status != status:
                        log("status modified")
                        morpheme.status = status
                        morpheme.statusChanged = True
                        morphemes_modified.append(morpheme)
            card.lastUpdated = card.ankiLastModified

        self.morphemeDao.updateAll(morphemes_modified)
        self.cardDao.updateAll(cards)
    
    def analyze(self, fact):
        
        morphemes = self.extractMorphemes(fact.expression)
        
        attachedMorphemes = []
        for morpheme in morphemes:
            # if mecab:
            morpheme.morph = self.mecabDao.persist(morpheme.morph)
            morpheme = self.morphemeDao.persist(morpheme)
            attachedMorphemes.append(morpheme)
        
        self.factService.changeMorphemes(fact, attachedMorphemes)
        
        return morphemes
        
    def getAllPOS(self):
        return self.mecabDao.getAllPOS()
  
    def getAllSubPOS(self):
        return self.mecabDao.getAllSubPOS()
    
    def getMorphemes(self, searchText = None):
        
        if searchText == None or searchText == "":
            return self.mecabDao.getMorphemes()
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
            return self.mecabDao.getMorphemes(expressions, status, status_changed, pos, subPos)