
from learnX.morphology.service.ServicesLocator import *

from learnX.morphology.db.dto.Deck import *
from learnX.morphology.db.dto.Card import *

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
        
        log("Determine Modified Facts")
        
        #XXX: Ne pas faire la vérification la 1er fois, prendre tous les facts !
        # Verifier a ne prendre que les facts modifié
        modifiedFacts = []
        for fact in facts:
            if fact.ankiLastModified == fact.lastUpdated:
                continue
            expression = ankiFacts[fact.ankiFactIndex][deck.expressionField]
            if fact.expressionHash != None and int(fact.expressionHash) == hash(expression) :
                continue
            fact.expression = expression
            modifiedFacts.append(fact)
        
        log("Analyze Morphemes on " + str(len(modifiedFacts)) + " facts")
        if len(modifiedFacts) > 0:
            self.morphemesService.analyzeMorphemes(modifiedFacts, deck, deck.language)

        log("computeMorphemesMaturity")
        modifiedCards = self.factsService.getAllCardsChanged(deck, ankiCards)

        # FIXME: uncomment
        if len(modifiedCards) > 0:
            self.morphemesService.computeMorphemesMaturity(modifiedCards)
        
        log("Calculed morpheme Score Start")
        self.morphemesService.computeMorphemesScore(deck.language)
        
        log("decksService.countMorphemes Start")
        self.decksService.countMorphemes(deck)
        
        log("decksService.countMorphemes Start")
        self.languagesService.countMorphemes(deck.language)
        
        log("factsService.computeFactsMaturity Start")
        self.factsService.computeFactsMaturity(deck.language)
        
        log("Saves Decks Start")
        realDeck.save()
        realDeck.close()
        log("Saves Decks Stop")
        
    def processFacts(self, language):
        
        log("self.setupProcessFacts()")
        self.setupProcessFacts(language)

        log("self.markFacts()")     
        self.markFacts(language)
        
        log("self.changeDueCards()")     
        self.changeDueCards(language)
        
        log("self.saveDecks(ankiFactsId)")     
        self.closeDecks(language)
        
        self.factsService.clearAllFactsStatus(language)
        
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
        
        #i = 0
        for modifiedFact in modifiedFacts:
            try:
                ankiFact = self.ankiDeckFacts[modifiedFact.deck.path][modifiedFact.ankiFactId]
            except Exception: continue
            
            deck = self.decks[modifiedFact.deck.path]
            fields = deck.fields
            
            if fields[Deck.LEARNX_SCORE_KEY][1]:
                try: ankiFact[fields[Deck.LEARNX_SCORE_KEY][0]] = u'%d' % int(modifiedFact.score)
                except KeyError: pass
            
            
            morphemes = self.factsService.getMorphemes(modifiedFact)
            matureMorphemes = []
            knownMorphemes = []
            learnMorphemes = []
            unknownMorphemes = []
            morphemesScore = 0
            for morpheme in morphemes:
                morphLemme = morpheme.morphLemme
                if morpheme.status == Morpheme.STATUS_MATURE:
                    matureMorphemes.append(morphLemme.base)
                if morpheme.status == Morpheme.STATUS_KNOWN:
                    knownMorphemes.append(morphLemme.base)
                if morpheme.status == Morpheme.STATUS_LEARNT:
                    learnMorphemes.append(morphLemme.base)
                if morpheme.status == Morpheme.STATUS_NONE:
                    unknownMorphemes.append(morphLemme.base)
                morphemesScore += morpheme.score
            
            if fields[Deck.VOCAB_SCORE_KEY][1]:
                try: ankiFact[fields[Deck.VOCAB_SCORE_KEY][0]] = u'%d' % int(morphemesScore)
                except KeyError: pass
    
            if fields[Deck.UNKNOWNS_KEY][1]:
                try: ankiFact[fields[Deck.UNKNOWNS_KEY][0]] = u','.join(u for u in unknownMorphemes)
                except KeyError: pass
    
            if fields[Deck.LEARNTS_KEY][1]:
                try: ankiFact[fields[Deck.LEARNTS_KEY][0]] = u','.join(u for u in learnMorphemes)
                except KeyError: pass
                
            if fields[Deck.KNOWNS_KEY][1]:
                try: ankiFact[fields[Deck.KNOWNS_KEY][0]] = u','.join(u for u in knownMorphemes)
                except KeyError: pass
                
            if fields[Deck.MATURES_KEY][1]:
                try: ankiFact[fields[Deck.MATURES_KEY][0]] = u','.join(u for u in matureMorphemes)
                except KeyError: pass

            if len(unknownMorphemes) == 1:
                if fields[Deck.COPY_UNKNOWN_1_TO_KEY][1]:
                    try: ankiFact[fields[Deck.COPY_UNKNOWN_1_TO_KEY][0]] = u','.join(u for u in unknownMorphemes)
                    except KeyError: pass
            elif len(unknownMorphemes) == 0:
                if fields[Deck.COPY_MATURE_TO_KEY][1]:
                    try: ankiFact[fields[Deck.COPY_MATURE_TO_KEY][0]] = u'%s' % ankiFact[deck.expressionField]
                    except KeyError: pass
                     
            if fields[Deck.DEFINITION_KEY][1] and fields[Deck.DEFINITION_SCORE_KEY][1]:
                try: ankiFact[fields[Deck.DEFINITION_SCORE_KEY][0]] = u'%d' % int(modifiedFact.definitionScore)
                except KeyError: pass
            
            
            ankiFact.tags = canonifyTags(deleteTags(modifiedFact.getAllStatusTag(), ankiFact.tags))
            ankiFact.tags = canonifyTags(addTags(modifiedFact.getStatusTag(), ankiFact.tags))
            
            #log(ankiFact.tags)
            
            ankiFactsId.append(ankiFact.id)
        
        self.saveDecks(ankiFactsId, language)
                
    def changeDueCards(self, language):
        
        cards = self.factsService.getAllCardsOrderByScore(language = language)
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

        self.saveDecks(None, language)
    
    # Mark Duplicate
    def markDuplicateFacts(self, deck):
        
        ankiDeck = AnkiHelper.getDeck(deck.path)
        
        cards = self.factsService.getAllCardsOrderByScore(deck = deck)
        ankiFactsId = list()
    
        ankiFacts = AnkiHelper.getFacts(ankiDeck)
        ankiFactsDict = dict()
        for ankiFact in ankiFacts:
            ankiFactsDict[ankiFact.id] = ankiFact
    
        uniqueMorphemes = dict()
        #i = 0
        for card in cards:
            fact = self.factsService.getFactById(card.factId)
            morphemes = self.factsService.getMorphemes(fact)
            
            factHasNewMorphemes = False
            for morpheme in morphemes:
                if morpheme.id not in uniqueMorphemes:
                    uniqueMorphemes[morpheme.id] = morpheme.id
                    factHasNewMorphemes = True
            
            try:
                ankiFact = ankiFactsDict[fact.ankiFactId]
            except Exception:continue
            
            ankiFact.tags = canonifyTags(deleteTags(u'LearnX_Duplicate', ankiFact.tags))
            if factHasNewMorphemes == False:
                log(str(fact) + " is Duplicate")
                ankiFact.tags = canonifyTags(addTags(u'LearnX_Duplicate', ankiFact.tags))
                ankiFactsId.append(int(ankiFact.id))

        log(ankiFactsId)
        ankiDeck.updateFactTags(ankiFactsId)
        ankiDeck.save()
        ankiDeck.close()
    
    def saveDecks(self, ankiFactsId, language):
        log("Save Decks !")
        for modifiedDeckPath in self.modifiedDecksPath:
            ankiDeck = self.ankiDecks[modifiedDeckPath]
            
            if ankiFactsId:
                ankiDeck.updateFactTags(ankiFactsId)
            
            ankiDeck.save()
    
    def closeDecks(self, language):
        for modifiedDeckPath in self.modifiedDecksPath:
            ankiDeck = self.ankiDecks[modifiedDeckPath]
            
            ankiDeck.save()
            ankiDeck.close()
    