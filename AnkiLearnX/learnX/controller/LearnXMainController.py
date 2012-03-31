
from learnX.morphology.service.ServicesLocator import *

from learnX.morphology.db.dto.Deck import *

from learnX.utils.AnkiHelper import *
from learnX.utils.Log import *

from anki.utils import deleteTags, addTags, canonifyTags, stripHTML

class LearnXMainController:
    def __init__(self, interface):
        self.interface = interface
        
        self.servicesLocator = ServicesLocator.getInstance()
        self.decksService = self.servicesLocator.getDecksService()
        self.languagesService = self.servicesLocator.getLanguagesService()
        self.factsService = self.servicesLocator.getFactsService()
        
    def analyze(self, deck):
        self.analyzeDeck(deck)
        
        log("Process Facts Start")
        self.processFacts(deck.language)
        log("Process Facts Stop")
        
        self.interface.refreshAll()
        
        log("End")
    
    def analyzeLanguage(self, language):
        
        log(language)
        decks = self.decksService.listDecksByLanguage(language)
        for deck in decks:
            self.analyzeDeck(deck)
        
        log("Process Facts Start")
        self.processFacts(deck.language)
        log("Process Facts Stop")
        
        self.interface.refreshAll()
        
        log("End")
        
    def analyzeDeck(self, deck):
        
        self.morphemesService = self.servicesLocator.getMorphemesService(deck.language)
        
        realDeck = AnkiHelper.getDeck(deck.path)
        log(realDeck)
        log("Get All Facts / Cards")
        ankiFacts = AnkiHelper.getFacts(realDeck)
        ankiCards = AnkiHelper.getCards(realDeck)
        i = 0
        
        log("Store All Facts")
        facts = self.factsService.getAllFacts(deck, ankiFacts)
        log("Analyze All")
        
        # Verifier a ne prendre que les facts modifié
        modifiedFacts = []
        for fact in facts:
            if fact.ankiLastModified == fact.lastUpdated:
                continue
            expression = ankiFacts[fact.ankiFactIndex][deck.expressionField]
            if fact.expressionHash != None and int(fact.expressionHash) == hash(expression) :
                continue
            log("to analyze")
            fact.expression = expression
            modifiedFacts.append(fact)
        
        log("Analyze Morphemes")
        if len(modifiedFacts) > 0:
            self.morphemesService.analyzeMorphemes(modifiedFacts, deck.language)


        log("computeMorphemesMaturity")
        modifiedCards = self.factsService.getAllCardsChanged(deck, ankiCards)

        if len(modifiedCards) > 0:
            self.morphemesService.computeMorphemesMaturity(modifiedCards)
        
        log("Calculed morpheme Score Start")
        self.morphemesService.computeMorphemesScore(deck.language)
        log("Calculed morpheme Score End")
        
        log("decksService.countMorphemes Start")
        self.decksService.countMorphemes(deck)
        log("decksService.countMorphemes End")
        
        log("decksService.countMorphemes Start")
        self.languagesService.countMorphemes(deck.language)
        log("decksService.countMorphemes End")
        
        log("factsService.computeFactsMaturity Start")
        self.factsService.computeFactsMaturity(deck.language)
        log("factsService.computeFactsMaturity End")
        
        log("Saves Decks Start")
        realDeck.save()
        realDeck.close()
        log("Saves Decks Stop")
        
    def processFacts(self, language):
        
        log("self.setupProcessFacts()")
        self.setupProcessFacts(language)

        log("self.markFacts()")     
        ankiFactsId = self.markFacts(language)
        
        log("self.changeDueCards()")     
        self.changeDueCards(language)
        
        log("self.saveDecks(ankiFactsId)")     
        self.saveDecks(ankiFactsId, language)
        
    def setupProcessFacts(self, language):
        self.decks = decks = dict()
        self.ankiDecks = ankiDecks = dict()
        self.ankiDeckFacts = ankiDeckFacts = dict()
        self.ankiDeckCards = ankiDeckCards = dict()
        #self.modifiedDecksPath = modifiedDecksPath = self.decksService.getDecksPathChanged()
        decksList = self.decksService.listDecks()
        modifiedDecksPath = []
        for deck in decksList:
            log(deck.language)
            if deck.enabled and deck.language == language:
                modifiedDecksPath.append(deck.path)
        self.modifiedDecksPath = modifiedDecksPath
        
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
    
    def markFacts(self, language):
        modifiedFacts = self.factsService.getAllFactsChanged(language)
        ankiFactsId = list()
        
        for modifiedFact in modifiedFacts:
            try:
                ankiFact = self.ankiDeckFacts[modifiedFact.deck.path][modifiedFact.ankiFactId]
            except Exception: continue
            
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
        
    def changeDueCards(self, language):
        
        cards = self.factsService.getAllCardsOrderByScore(language)
        newtime = 472777200.0 # 25 Decembre 1984 :)
        
        for card in cards:
            try:
                ankiCard = self.ankiDeckCards[card.deckPath][card.ankiCardId]
            except Exception: continue
            deck = self.ankiDecks[card.deckPath]
            
            try:
                if deck.cardIsNew(ankiCard):
                    ankiCard.due = newtime
                    ankiCard.combinedDue = newtime
                    newtime += 3600
            except KeyError:
                log('Error during sorting')
            
    def saveDecks(self, ankiFactsId, language):
        for modifiedDeckPath in self.modifiedDecksPath:
            ankiDeck = self.ankiDecks[modifiedDeckPath]
            
            ankiDeck.updateFactTags(ankiFactsId)
            
            ankiDeck.save()
            ankiDeck.close()
            
        self.factsService.clearAllFactsStatus(language)
    