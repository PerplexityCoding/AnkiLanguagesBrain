
from learnX.morphology.service.ServicesLocator import *

from learnX.morphology.db.dto.Deck import *
from learnX.morphology.db.dto.Card import *

from learnX.utils.AnkiHelper import *
from learnX.utils.Log import *

#from anki.utils import deleteTags, addTags, canonifyTags, stripHTML

class LearnXMainController:
    def __init__(self, interface):
        self.interface = interface
        
        self.col = interface.col
        self.deckManager = interface.deckManager
        
        
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
        
        realDeck = self.deckManager.get(deck.ankiDeckId)
        log(realDeck)
        log("Get All Facts / Cards")
        self.ankiCards = ankiCards = self.deckManager.cids(realDeck["id"])
        i = 0
        
        log("Store All Facts : " + str(len(ankiCards)) + " cards")
        facts = self.factsService.getAllFacts(self.col, deck, ankiCards)
        
        log("Determine Modified Facts : " + str(len(facts)))
        
        #XXX: Ne pas faire la vérification la 1er fois, prendre tous les facts !
        # Verifier a ne prendre que les facts modifié
        # Pas besoin pour anki 2 ?
        modifiedFacts = []
        for fact in facts:
            if fact.ankiFact.mod == fact.lastUpdated:
                continue
            if fact.expressionHash != None and Utils.fieldChecksum(fact.ankiFact.__getitem__(deck.expressionField)) == fact.expressionHash:
                continue
            modifiedFacts.append(fact)
        
        log("Analyze Morphemes on " + str(len(modifiedFacts)) + " facts")
        if len(modifiedFacts) > 0:
            self.morphemesService.analyzeMorphemes(modifiedFacts, deck, deck.language)

        log("getAllCardsChanged")
        modifiedCards = self.factsService.getAllCardsChanged(self.col, deck, ankiCards)
        
        log("computeMorphemesMaturity: " + str(len(modifiedCards)) + " cards")
        if len(modifiedCards) > 0:
            self.morphemesService.computeMorphemesMaturity(modifiedCards)
        
        log("Calculed morpheme Score Start")
        self.morphemesService.computeMorphemesScore(deck.language)
        
        log("Analyze Definitions")
        #if deck.definitionField:
        #    self.morphemesService.analyseDefinition(deck, deck.language, facts, ankiFacts)
        
        log("decksService.countMorphemes Start")
        self.decksService.countMorphemes(deck)
        
        log("decksService.countMorphemes Start")
        self.languagesService.countMorphemes(deck.language)
        
        log("factsService.computeFactsMaturity Start")
        self.factsService.computeFactsMaturity(deck.language)
        
        log("Saves Decks Start")
        self.col.save()
        log("Saves Decks Stop")
        
    def processFacts(self, language):
        
        #log("self.setupProcessFacts()")
        #self.setupProcessFacts(language)

        log("self.markFacts()")     
        self.markFacts(language)
        
        #log("self.changeDueCards()")     
        #self.changeDueCards(language)
        
        self.factsService.clearAllFactsStatus(language)
        
        self.col.save()

    
    def getMorphemesScore(self, morphemes):
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
        return morphemesScore, matureMorphemes, knownMorphemes, learnMorphemes, unknownMorphemes
    
    def markFacts(self, language):
        facts = self.factsService.getAllFactsByLanguage(language)
        ankiFactsId = list()
        
        #i = 0
        for fact in facts:
            try:
                ankiFact = self.col.getNote(fact.ankiFactId)
            except Exception: continue
            
            deck = fact.deck
            fields = deck.fields
            
            morphemes = self.factsService.getMorphemes(fact)
            morphemesScore, matureMorphemes, knownMorphemes, learnMorphemes, unknownMorphemes = self.getMorphemesScore(morphemes)
            
            if fact.statusChanged == True: # FIXME: sure ?
                if fields[Deck.LEARNX_SCORE_KEY][1]:
                    try: ankiFact[fields[Deck.LEARNX_SCORE_KEY][0]] = u'%d' % int(fact.score)
                    except KeyError: pass
                
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
                
                self.col.tags.remFromStr(fact.getAllStatusTag(), self.col.tags.join(ankiFact.tags))
                self.col.tags.addToStr(fact.getAllStatusTag(), self.col.tags.join(ankiFact.tags))
                                                       
            if deck.definitionField:
                try:
                    ankiFact.tags = canonifyTags(deleteTags(u'LxDefKnown,LxDefMatch', ankiFact.tags))
                    definition = self.factsService.getDefinition(fact)
                    
                    if definition and definition.definitionHash and int(definition.definitionHash) != 0:
                    
                        defMorphemes = self.morphemesService.getMorphemesDefinition(definition)
                        dictMorphemesScore, defMatureMorphemes, defKnownMorphemes, defLearnMorphemes, defUnknownMorphemes = self.getMorphemesScore(defMorphemes)
                        
                        if len(defUnknownMorphemes) == 0:
                            ankiFact.tags = canonifyTags(addTags(u'LxDefKnown', ankiFact.tags))
                        
                        defKeyMorphemes = self.morphemesService.getMorphemesDefinitionKey(definition)
                        defKeyMorphemesBase = "".join(m.morphLemme.base for m in defKeyMorphemes)
                        
                        if len(unknownMorphemes) == 1 and unknownMorphemes[0] in defKeyMorphemesBase:
                            ankiFact.tags = canonifyTags(addTags(u'LxDefMatch', ankiFact.tags))
                        
                        if fields[Deck.DEFINITION_SCORE_KEY][1]:
                            try: ankiFact[fields[Deck.DEFINITION_SCORE_KEY][0]] = u'%d' % int(dictMorphemesScore)
                            except KeyError: pass
                  
                except KeyError: pass
            
            ankiFactsId.append(ankiFact.id)
    
    def changeDueCards(self, language):
        
        cards = self.factsService.getAllCardsOrderByScore(language = language)
        newtime = 472777200.0 # 25 Decembre 1984 :)
        
        for card in cards:
            try:
                ankiCard = self.col.getCard(card.ankiCardId)
            except Exception: continue
            deck = self.ankiDecks[card.ankiDeckId]
            
            try:
                if deck.cardIsNew(ankiCard):
                    ankiCard.due = newtime
                    ankiCard.combinedDue = newtime
                    newtime += 3600
            except KeyError:
                log('Error during sorting')

    # Mark Duplicate
    def markDuplicateFacts(self, deck):
        
        ankiDeck = self.deckManager.get(deck.ankiDeckId)
        
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
            
            ankiFact.tags = canonifyTags(deleteTags(u'LxDuplicate', ankiFact.tags))
            if factHasNewMorphemes == False:
                log(str(fact) + " is Duplicate")
                ankiFact.tags = canonifyTags(addTags(u'LxDuplicate', ankiFact.tags))
                ankiFactsId.append(int(ankiFact.id))

        log(ankiFactsId)
        ankiDeck.updateFactTags(ankiFactsId)
        self.col.save()


