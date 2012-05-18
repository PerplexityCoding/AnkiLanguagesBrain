
from learnX.morphology.service.ServicesLocator import *

from learnX.morphology.db.dto.Deck import *
from learnX.morphology.db.dto.Card import *

from learnX.utils.AnkiHelper import *
from learnX.utils.Log import *

from anki.utils import intTime, joinFields, ids2str

class LearnXMainController:
    def __init__(self, interface):
        self.interface = interface
        
        self.col = interface.col
        self.deckManager = interface.deckManager
        
        self.servicesLocator = ServicesLocator.getInstance()
        self.decksService = self.servicesLocator.getDecksService()
        self.languagesService = self.servicesLocator.getLanguagesService()
        self.notesService = self.servicesLocator.getNotesService()
        
    def analyze(self, deck):
        log("Start")
        modifiedLemmes = self.analyzeDeck(deck)
        
        log("Process Notes Start")
        self.processGlobal(deck.language, deck.firstTime, modifiedLemmes)
        
        if deck.firstTime:
            log("decksService.resetFirstTime()") 
            self.decksService.resetFirstTime(deck)
        
        log("Refresh Interface")
        self.interface.refreshAll()
        log("End")
    
    def analyzeLanguage(self, language):
        
        log("Start")
        decks = self.decksService.listDecksByLanguage(language)
        
        firstTimeDecks = list()
        modifiedLemmes = set()
        firstTime = False
        for deck in decks:
            modifiedLemmes.update(self.analyzeDeck(deck))
            if deck.firstTime == True:
                firstTimeDecks.append(deck)
                firstTime = True
                
        log("Process Notes Start")
        self.processGlobal(language, firstTime, modifiedLemmes)
        
        log("decksService.resetFirstTime()") 
        for ftd in firstTimeDecks:
            self.decksService.resetFirstTime(ftd)
        
        log("Refresh Interface")
        self.interface.refreshAll()
        log("End")
        
    def analyzeDeck(self, deck):
        
        self.morphemesService = self.servicesLocator.getMorphemesService(deck.language)

        log("Get All Notes / Cards")
        self.ankiCards = ankiCards = AnkiHelper.getCards(deck.id)
        i = 0
        
        log("Retrieve All Notes : " + str(len(ankiCards)) + " cards")
        
        notes = self.notesService.retrieveAllNotes(ankiCards)
        
        log("Determine Modified Notes : " + str(len(notes)))
        
        modifiedNotes = []
        for note in notes:
            if note.ankiNote.mod == note.lastUpdated:
                continue
            if note.expressionCsum != None and int(Utils.fieldChecksum(note.ankiNote[deck.expressionField])) == int(note.expressionCsum):
                continue
            modifiedNotes.append(note)
        
        log("Analyze Morphemes on " + str(len(modifiedNotes)) + " notes")
        if len(modifiedNotes) > 0:
            self.morphemesService.analyzeLemmes(modifiedNotes, deck, deck.language)
            self.morphemesService.analyzeMorphemes(modifiedNotes, deck, deck.language)

        log("Retrieve All Cards")
        cards = self.notesService.retrieveAllCards(deck, ankiCards)
        
        modifiedCards = list()
        for card in cards:
            if card.ankiCard.mod == card.lastUpdated:
                continue
            if card.ankiCard.ivl == card.interval:
                continue
            modifiedCards.append(card)
        
        if len(modifiedCards) <= 0:
            return set()
            
        log("refreshInterval " + str(len(modifiedCards)))
        return self.morphemesService.refreshInterval(modifiedCards)    
            
    def processGlobal(self, language, firstTime, modifiedLemmes):

        log("Refresh Linked Morphemes")
        lemmes = self.morphemesService.refreshLinkedMorphemes(modifiedLemmes)
                    
        log("Calculed morpheme Score Start")
        notes = self.morphemesService.computeMorphemesScore(lemmes)
        
        log("Calculed notes Score Start")
        notes = self.notesService.computeNotesScore(notes)
        
        log("self.markNotes()")     
        self.markNotes(notes)
        
        log("self.changeDueCards()")     
        self.changeDueCards(notes)
        
        log("col.save()")
        self.col.save()
    
    def markNotes(self, notes):
        
        if not notes:
            return
        
        fields = { #FIXME
            Deck.LEARNX_SCORE_KEY : "LearnXScore",
            Deck.VOCAB_SCORE_KEY : "VocabScore",
            Deck.UNKNOWNS_KEY : "UnknownMorphemes",
            Deck.KNOWNS_KEY : "KnownMorphemes",
            Deck.COPY_UNKNOWN_1_TO_KEY : "VocabExpression",
            Deck.DEFINITION_SCORE_KEY : "DefinitionScore"
        }
        
        modifiedFields = list()
        ankiNotesId = list()
        for note in notes:
            try:
                ankiNote = self.col.getNote(note.id)
            except Exception: continue
            
            try:
                ankiScore = int(ankiNote[fields[Deck.LEARNX_SCORE_KEY]])
            except Exception: continue
            
            if abs(ankiScore - int(note.score)) >= 15:
                continue
            
            tm = self.col.tags
            origFlds = joinFields(ankiNote.fields)
            origTags = tm.join(ankiNote.tags)
            
            lemmes = self.morphemesService.getLemmesFromNote(note)
            morphemesScore = 0
            knownMorphemes = list()
            unknownMorphemes = list()
            
            for lemme in lemmes:
                if lemme.maxInterval > 0:
                    knownMorphemes.append(lemme.base)
                else:
                    unknownMorphemes.append(lemme.base)
                morphemesScore += lemme.score
            
            try: ankiNote[fields[Deck.LEARNX_SCORE_KEY]] = u'%d' % int(note.score)
            except KeyError: pass
            
            try: ankiNote[fields[Deck.VOCAB_SCORE_KEY]] = u'%d' % int(morphemesScore)
            except KeyError: pass
    
            try: ankiNote[fields[Deck.UNKNOWNS_KEY]] = u','.join(u for u in unknownMorphemes)
            except KeyError: pass
    
            try: ankiNote[fields[Deck.KNOWNS_KEY]] = u','.join(u for u in knownMorphemes)
            except KeyError: pass
            
            ankiNote.tags = tm.split(tm.remFromStr(u'LxReview LxToLearn LxTooDifficult', tm.join(ankiNote.tags)))
            
            if len(unknownMorphemes) == 1:
                try: ankiNote[fields[Deck.COPY_UNKNOWN_1_TO_KEY]] = u','.join(u for u in unknownMorphemes)
                except KeyError: pass
                tag = u'LxToLearn'
            elif len(unknownMorphemes) == 0:
                tag = u'LxReview'
            else:
                tag = u'LxTooDifficult'
            ankiNote.tags = tm.split(tm.addToStr(tag, tm.join(ankiNote.tags)))
            
            flds = joinFields(ankiNote.fields)
            tags = tm.join(ankiNote.tags)
            
            if flds != origFlds or origTags != tags:
                modifiedFields.append(dict(nid=ankiNote.id, flds=flds, tags=tags, u=self.col.usn(), m=intTime()))
            ankiNotesId.append(ankiNote.id)
    
        log ("update fields notes " + str(len(modifiedFields)))
        if len(modifiedFields) > 0:
            self.col.tags.register([u'LxReview', u'LxToLearn', u'LxTooDifficult'])
            self.col.db.executemany("update notes set flds=:flds, tags=:tags, mod=:m,usn=:u where id=:nid", modifiedFields)
        if len(ankiNotesId) > 0:
            self.col.updateFieldCache(ankiNotesId)
    
    def changeDueCards(self, notes):
        
        log("get all cards")
        cardsId = self.notesService.getAllCards()
        
        log("choose cards " + str(len(cardsId)))
        d = []
        now = intTime()
        for cardId, score in cardsId:
            try:
                ankiCard = self.col.getCard(cardId)
            except Exception: continue
            
            if score != 0 and ankiCard.due != score and ankiCard.ivl == 0:
                d.append(dict(now=now, due=score, usn=self.col.usn(), cid=cardId))
                    
        log("update")
        if len(d) > 0:
            self.col.db.executemany("update cards set due=:due, mod=:now, usn=:usn where id = :cid", d)
