
from learnX.morphology.service.DecksService import *
from learnX.morphology.service.LanguagesService import *
from learnX.morphology.service.MorphemesService import *
from learnX.morphology.service.FactsService import *

from learnX.morphology.db.dto.Deck import *

from learnX.utils.AnkiHelper import *
from learnX.utils.Log import *

from anki.utils import deleteTags, addTags, canonifyTags, stripHTML

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
        
        realDeck.save()
        realDeck.close()
        
        self.processFacts()
        
        log("End")
        
    def processFacts(self):
        
        self.setupProcessFacts()
        ankiFactsId = self.markFacts()
        self.changeDueCards()
        self.saveDecks(ankiFactsId)
        
    def setupProcessFacts(self):
        self.decks = decks = dict()
        self.ankiDecks = ankiDecks = dict()
        self.ankiDeckFacts = ankiDeckFacts = dict()
        self.ankiDeckCards = ankiDeckCards = dict()
        self.modifiedDecksPath = modifiedDecksPath = self.decksService.getDecksPathChanged()
        
        # Init Mapping AnkiCards -> Cards and AnkiFacts -> Fact
        
        for modifiedDeckPath in modifiedDecksPath:
            ankiDecks[modifiedDeckPath] = realDeck = AnkiHelper.getDeck(modifiedDeckPath)
            decks[modifiedDeckPath] = self.decksService.getDeckByPath(modifiedDeckPath)
            
            ankiFacts = AnkiHelper.getFacts(realDeck)
            ankiFactsDict = dict()
            for ankiFact in ankiFacts:
                ankiFactsDict[ankiFact.id] = ankiFact
            ankiDeckFacts[modifiedDeckPath] = ankiFactsDict
                
            ankiCards = AnkiHelper.getCards(realDeck)
            ankiCardsDict = dict()
            for ankiCard in ankiCards:
                ankiCardsDict[ankiCard.id] = ankiCard    
            ankiDeckCards[modifiedDeckPath] = ankiCardsDict
    
    def markFacts(self):
        modifiedFacts = self.factsService.getAllChanged()
        ankiFactsId = list()
        
        for modifiedFact in modifiedFacts:
            ankiFact = self.ankiDeckFacts[modifiedFact.deck.path][modifiedFact.ankiFactId]
            deck = self.decks[modifiedFact.deck.path]
            fields = deck.fields
            
            if fields[Deck.LEARNX_SCORE_KEY][1]:
                try: ankiFact[fields[Deck.LEARNX_SCORE_KEY][0]] = u'%d' % int(modifiedFact.score)
                except KeyError: pass
            
            #if fields[Deck.VOCAB_RANK_KEY][1]:
            #    try: ankiFact[fields[Deck.VOCAB_RANK_KEY][0]] = u'%d' % int(modifiedFact.score)
            #    except KeyError: pass
    
            #LEARNT_NB_KEY = "Learnt Count"
            #KNOWN_NB_KEY = "Known Count"
            #MATURE_NB_KEY = "Mature Count"
            
            #UNKNOWNS_KEY = "Unknown"
            #UNMATUES_KEY = "Unmature"
            ankiFact.tags = canonifyTags(deleteTags(modifiedFact.getAllStatusTag(), ankiFact.tags))
            
            ankiFact.tags = canonifyTags(addTags(modifiedFact.getStatusTag(), ankiFact.tags))
            
            ankiFactsId.append(ankiFact.id)
        
        return ankiFactsId
        
    def changeDueCards(self):
        
        cards = self.factsService.getAllCardsOrderByScore()
        newtime = 472777200.0 # 25 Decembre 1984 :)
        
        for card in cards:
            ankiCard = self.ankiDeckCards[card.deckPath][card.ankiCardId]
            deck = self.ankiDecks[card.deckPath]
            
            try:
                if deck.cardIsNew(ankiCard):
                    ankiCard.due = newtime
                    ankiCard.combinedDue = newtime
                    newtime += 3600
            except KeyError:
                log('Error during sorting')
            
    def saveDecks(self, ankiFactsId):
        for modifiedDeckPath in self.modifiedDecksPath:
            ankiDeck = self.ankiDecks[modifiedDeckPath]
            
            ankiDeck.updateFactTags(ankiFactsId)
            
            ankiDeck.save()
            ankiDeck.close()
            
        #self.factsService.clearAllFactsStatus()
    