
from learnX.morphology.service.DecksService import *
from learnX.morphology.service.LanguagesService import *
from learnX.morphology.service.MorphemesService import *
from learnX.morphology.service.FactsService import *

from learnX.utils.AnkiHelper import *
from learnX.utils.Log import *

class LearnXMainController:
    def __init__(self):
        self.decksService = DecksService()
        self.languagesService = LanguagesService()
        self.morphemesService = MorphemesService()
        self.factsService = FactsService()
        
    def analyze(self, deck):
        
        realDeck = AnkiHelper.getDeck(deck.path)
        log(realDeck)
        log("Get All Facts / Cards")
        ankiFacts = AnkiHelper.getFacts(realDeck)
        ankiCards = AnkiHelper.getCards(realDeck)
        i = 0
        
        log("Store All Facts")
        facts = self.factsService.getAllFacts(deck, ankiFacts)
        cards = self.factsService.getAllCards(deck, ankiCards)
        log("Analyze All")
        
        # Verifier a ne prendre que les facts modifié
        modifiedFacts = []
        for fact in facts:
            if fact.ankiLastModified == fact.lastUpdated:
                continue
            expression = ankiFacts[fact.ankiFactIndex]["Expression"]
            if fact.expressionHash != None and int(fact.expressionHash) == hash(expression) :
                continue
            log("to analyze")
            fact.expression = expression
            modifiedFacts.append(fact)
        
        if len(modifiedFacts) > 0:
            self.morphemesService.analyzeAll(modifiedFacts)
        
        modifiedCards = []

        for card in cards:
            if card.lastUpdated != card.ankiLastModified:
                modifiedCards.append(card)

        if len(modifiedCards) > 0:
            self.morphemesService.computeMorphemesMaturity(modifiedCards)
        
        log("Calculed morpheme Score Start")
        self.morphemesService.computeMorphemesScore()
        log("Calculed morpheme Score End")
        
        self.decksService.countMorphemes(deck)
        self.factsService.computeCardsMaturity()

        log("End")
        
    
        
        
            