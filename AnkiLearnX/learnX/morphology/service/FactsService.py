#-*- coding: utf-8 -*-

from learnX.morphology.db.dao.FactDao import *
from learnX.morphology.db.dao.CardDao import *
from learnX.morphology.db.dao.MorphemeDao import *
from learnX.morphology.db.dao.DeckDao import *
from learnX.morphology.db.dao.DefinitionDao import *

from learnX.morphology.db.dto.Morpheme import *
from learnX.morphology.db.dto.Fact import *

class FactsService:
    def __init__(self, serviceLocator):
        self.serviceLocator = serviceLocator
        self.fact_dao = FactDao()
        self.card_dao = CardDao()
        self.morpheme_dao = MorphemeDao()
        self.deck_dao = DeckDao()
        self.definitionDao = DefinitionDao()
        
    def setupServices(self):
        self.decksService = self.serviceLocator.getDecksService()
        
    def getFact(self, deck, ankiFactId):
        fact = self.fact_dao.findByAnkiFactId(deck, ankiFactId)
        if fact == None:
            fact = Fact(deck.id, ankiFactId, None, None, False, Fact.STATUS_NONE, False, 0)
            fact.deck = deck
            fact = self.fact_dao.insert(fact)

        return fact
    
    def getDefinition(self, fact):
        return self.definitionDao.getDefinition(fact.id)

    def getFactById(self, ankiFactId):
        fact = self.fact_dao.findById(ankiFactId)
        fact.deck = self.deck_dao.findById(fact.deckId)
        
        return fact
    
    def getAllFacts(self, col, deck, ankiCards):
        
        facts = []
        factsToInsert = []
        for ankiCard in ankiCards:
            ankiCard = col.getCard(ankiCard)
            ankiFact = ankiCard.note()
            fact = self.fact_dao.findByAnkiFactId(deck, ankiFact.id)
            if fact == None:
                fact = Fact(deck.id, ankiFact.id, None, None, False, Fact.STATUS_NONE, False, 0)
                fact.deck = deck
                factsToInsert.append(fact)
            fact.ankiFact = ankiFact
            facts.append(fact)

        if len(factsToInsert) > 0:
            self.fact_dao.insertAll(factsToInsert)
        
        return facts
    
    def getAllCardsOrderByScore(self, deck = None, language = None):
        if language:
            decksId = self.decksService.listDecksIdByLanguage(language)
        else:
            decksId = [deck.id]
        log(decksId)
        return self.card_dao.getCardsOrderByScore(decksId)
    
    def calcCardStatus(self, deck, ankiCard):
        if ankiCard.ivl == 0:
            return Card.STATUS_NONE
        if ankiCard.ivl < deck.knownTreshold:
            return Card.STATUS_LEARNT
        if ankiCard.ivl < deck.matureTreshold:
            return Card.STATUS_KNOWN
        return Card.STATUS_MATURE
        
    def getAllCardsChanged(self, col, deck, ankiCards):
        
        changedCards = []
        cardsToInsert = []
        cardsToUpdate = []
        for ankiCard in ankiCards:
            ankiCard = col.getCard(ankiCard)
            card = self.card_dao.findById(deck, ankiCard.id)
            status = self.calcCardStatus(deck, ankiCard)
            if card == None:
                fact = self.getFact(deck, ankiCard.note().id)
                card = Card(deck.id, fact.id, ankiCard.id, status, True)
                card.deck = deck
                card.fact = fact
                cardsToInsert.append(card)
                changedCards.append(card)
            else:
                if status != card.status:
                    card.statusChanged = True
                    changedCards.append(card)
                card.status = status               
                cardsToUpdate.append(card)  
            card.ankiLastModified = ankiCard.mod
            
        if len(cardsToInsert) > 0:
            self.card_dao.insertAll(cardsToInsert)
        
        if len(cardsToUpdate) > 0:
            self.card_dao.updateAll(cardsToUpdate)
        
        return changedCards
    
    def getAllFactsChanged(self, language):
        return self.getAllFactsByLanguage(language, 1)
    
    def getAllFactsByLanguage(self, language, statusChanged = None):
        
        decksId = self.decksService.listDecksIdByLanguage(language)
        facts = self.fact_dao.selectAll(decksId, statusChanged) 
        decks = dict()
        for fact in facts:
            deck = None
            try:
                deck = decks[fact.deckId]
            except KeyError as e:
                deck = self.deck_dao.findById(fact.deckId)
                decks[fact.deckId] = deck
            fact.deck = deck
        return facts
    
    def computeFactsMaturity(self, language):
        
        decksId = self.decksService.listDecksIdByLanguage(language)
        facts = self.fact_dao.selectAll(decksId, None) #FIXME: Buggggg with other decks !! replace with all facts for now ?
        for fact in facts:
            morphemes = self.morpheme_dao.getMorphemesFromFact(fact)
        
            matureMorphemes = []
            knownMorphemes = []
            learnMorphemes = []
            unknownMorphemes = []
            morphemesScore = 0
            for morpheme in morphemes:
                if morpheme.status == Morpheme.STATUS_MATURE:
                    matureMorphemes.append(morpheme)
                if morpheme.status == Morpheme.STATUS_KNOWN:
                    knownMorphemes.append(morpheme)
                if morpheme.status == Morpheme.STATUS_LEARNT:
                    learnMorphemes.append(morpheme)
                if morpheme.status == Morpheme.STATUS_NONE:
                    unknownMorphemes.append(morpheme)
                morphemesScore += morpheme.score
            total = len(morphemes)
            mature = len(matureMorphemes)
            known = len(knownMorphemes)
            learnt = len(learnMorphemes)
            unknown = len(unknownMorphemes)
            
            status = fact.status
            if unknown == 0:
                if learnt == 0 and known == 0:
                    status = Fact.STATUS_REVIEW_EASY
                elif learnt > 0:
                    status = Fact.STATUS_REVIEW_HARD
                else :
                    status = Fact.STATUS_REVIEW_MEDIUM
            elif unknown == 1:
                if learnt == 0 and known == 0:
                    status = Fact.STATUS_LEARN_EASY
                elif learnt > 0:
                    status = Fact.STATUS_LEARN_HARD
                else :
                    status = Fact.STATUS_LEARN_MEDIUM
            else:
                status = Fact.STATUS_TOO_DIFFICULT

            if status != fact.status:
                fact.status = status
                fact.statusChanged = True
            
            score = (mature * 1 + known * 2 + learnt * 6 + unknown * 30) * 300 + morphemesScore
            if score != fact.score:
                fact.score = score
                fact.statusChanged = True
            
        self.fact_dao.updateAll(facts) 

        #self.morpheme_dao.clearMorphemesStatus()

        return facts

    def changeMorphemes(self, fact, morphemes):
        self.fact_dao.insertFactMorphemes(fact, morphemes)
        
        fact.morphemes = morphemes
        return fact
    
    def getMorphemes(self, fact):
        return self.morpheme_dao.getMorphemesFromFact(fact, True)

    def getAllNewCards(self, language):
        decksId = self.decksService.listDecksIdByLanguage(language)
        return self.card_dao.getAllNewCards(decksId)

    def clearAllFactsStatus(self, language):
        decksId = self.decksService.listDecksIdByLanguage(language)
        self.fact_dao.clearAllFactsStatus(decksId)