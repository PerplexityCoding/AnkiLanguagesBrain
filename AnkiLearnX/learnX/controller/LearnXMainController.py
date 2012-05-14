
from learnX.morphology.service.ServicesLocator import *

from learnX.morphology.db.dto.Deck import *
from learnX.morphology.db.dto.Card import *

from learnX.utils.AnkiHelper import *
from learnX.utils.Log import *

from anki.utils import intTime, joinFields, ids2str

#from anki.utils import deleteTags, addTags, canonifyTags, stripHTML

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
        self.analyzeDeck(deck)
        
        log("Process Notes Start")
        self.processNotes(deck.language)
        log("Process Notes Stop")
        
        self.interface.refreshAll()
        log("End")
    
    def analyzeLanguage(self, language):
        
        log(language)
        decks = self.decksService.listDecksByLanguage(language)
        for deck in decks:
            self.analyzeDeck(deck)
        
        log("Process Notes Start")
        self.processNotes(deck.language)
        log("Process Notes Stop")
        
        self.interface.refreshAll()
        
        log("End")
        
    def analyzeDeck(self, deck):
        
        self.morphemesService = self.servicesLocator.getMorphemesService(deck.language)

        log("Get All Notes / Cards")
        self.ankiCards = ankiCards = AnkiHelper.getCards(deck.id)
        i = 0
        
        log("Store All Notes : " + str(len(ankiCards)) + " cards")
        
        notes = self.notesService.retrieveAllNotes(ankiCards)
        
        log("Determine Modified Notes : " + str(len(notes)))
        
        modifiedNotes = []
        for note in notes:
            if note.ankiNote.mod == note.lastUpdated:
                continue
            if note.expressionCsum != None and Utils.fieldChecksum(note.ankiNote[deck.expressionField]) == note.expressionCsum:
                continue
            modifiedNotes.append(note)
        
        log("Analyze Morphemes on " + str(len(modifiedNotes)) + " notes")
        if len(modifiedNotes) > 0:
            self.morphemesService.analyzeLemmes(modifiedNotes, deck, deck.language)
            self.morphemesService.analyzeMorphemes(modifiedNotes, deck, deck.language)

        log("getAllCardsChanged")
        cards = self.notesService.retrieveAllCards(deck, ankiCards)
        
        modifiedCards = list()
        for card in cards:
            if card.ankiCard.mod == card.lastUpdated:
                continue
            if card.ankiCard.ivl == card.interval:
                continue
            modifiedCards.append(card)
        
        log("refreshInterval")
        self.morphemesService.refreshInterval(modifiedCards)
        
        log("Calculed morpheme Score Start")
        self.morphemesService.computeMorphemesScore(deck.language)
        
        log("Calculed notes Score Start")
        self.notesService.computeNotesScore(deck)
        
    def processNotes(self, language):
        
        log("self.markNotes()")     
        self.markNotes(language)
        
        log("self.changeDueCards()")     
        self.changeDueCards(language)
        
        #self.notesService.clearAllNotesStatus(language)
        
        self.col.save()

    
    def getMorphemesScore(self, morphemes):
        knownMorphemes = []
        unknownMorphemes = []
        morphemesScore = 0
        for morpheme in morphemes:
            morphLemme = morpheme.morphLemme
            if morpheme.interval > 0:
                knownMorphemes.append(morphLemme.base)
            else:
                unknownMorphemes.append(morphLemme.base)
            morphemesScore += morpheme.score
        return morphemesScore, knownMorphemes, unknownMorphemes
    
    def markNotes(self, language):
        notes = self.notesService.getAllNotesByLanguage(language)
        ankiNotesId = list()
        
        #i = 0
        modifiedFields = []
        for note in notes:
            try:
                ankiNote = self.col.getNote(note.id)
            except Exception: continue
            
            origFlds = []
            origFlds.extend(ankiNote.fields)
            
            fields = { #FIXME
                Deck.LEARNX_SCORE_KEY : ("LearnXScore", True, True),
                Deck.VOCAB_SCORE_KEY : ("VocabScore", True, True),
                Deck.UNKNOWNS_KEY : ("UnknownMorphemes", True, False),
                Deck.KNOWNS_KEY : ("KnownMorphemes", True, False),
                Deck.COPY_UNKNOWN_1_TO_KEY : ("VocabExpression", True, False),
                Deck.COPY_MATURE_TO_KEY : ("SentenceExpression", True, False),
                Deck.DEFINITION_SCORE_KEY : ("DefinitionScore", True, False)
            }
            
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
            
            if True: # FIXME: sure ?
                if fields[Deck.LEARNX_SCORE_KEY][1]:
                    try: ankiNote[fields[Deck.LEARNX_SCORE_KEY][0]] = u'%d' % int(note.score)
                    except KeyError: pass
                
                if fields[Deck.VOCAB_SCORE_KEY][1]:
                    try: ankiNote[fields[Deck.VOCAB_SCORE_KEY][0]] = u'%d' % int(morphemesScore)
                    except KeyError: pass
        
                if fields[Deck.UNKNOWNS_KEY][1]:
                    try: ankiNote[fields[Deck.UNKNOWNS_KEY][0]] = u','.join(u for u in unknownMorphemes)
                    except KeyError: pass
        
                if fields[Deck.KNOWNS_KEY][1]:
                    try: ankiNote[fields[Deck.KNOWNS_KEY][0]] = u','.join(u for u in knownMorphemes)
                    except KeyError: pass
                    
                if len(unknownMorphemes) == 1:
                    if fields[Deck.COPY_UNKNOWN_1_TO_KEY][1]:
                        try: ankiNote[fields[Deck.COPY_UNKNOWN_1_TO_KEY][0]] = u','.join(u for u in unknownMorphemes)
                        except KeyError: pass
                #elif len(unknownMorphemes) == 0:
                #    if fields[Deck.COPY_MATURE_TO_KEY][1]:
                #        try: ankiNote[fields[Deck.COPY_MATURE_TO_KEY][0]] = u'%s' % ankiNote[deck.expressionField]
                #        except KeyError: pass
                
                #self.col.tags.remFromStr(note.getAllStatusTag(), self.col.tags.join(ankiNote.tags))
                #self.col.tags.addToStr(note.getAllStatusTag(), self.col.tags.join(ankiNote.tags))
                                                       
            #if deck.definitionField:
            #    try:
            #        ankiNote.tags = canonifyTags(deleteTags(u'LxDefKnown,LxDefMatch', ankiNote.tags))
            #        definition = self.notesService.getDefinition(note)
                    
            #        if definition and definition.definitionHash and int(definition.definitionHash) != 0:
                    
            #            defMorphemes = self.morphemesService.getMorphemesDefinition(definition)
            #            dictMorphemesScore, defMatureMorphemes, defKnownMorphemes, defLearnMorphemes, defUnknownMorphemes = self.getMorphemesScore(defMorphemes)
                        
            #            if len(defUnknownMorphemes) == 0:
            #                ankiNote.tags = canonifyTags(addTags(u'LxDefKnown', ankiNote.tags))
            #            
            #            defKeyMorphemes = self.morphemesService.getMorphemesDefinitionKey(definition)
            #            defKeyMorphemesBase = "".join(m.morphLemme.base for m in defKeyMorphemes)
            #            
            #            if len(unknownMorphemes) == 1 and unknownMorphemes[0] in defKeyMorphemesBase:
            #                ankiNote.tags = canonifyTags(addTags(u'LxDefMatch', ankiNote.tags))
            #            
            #            if fields[Deck.DEFINITION_SCORE_KEY][1]:
            #                try: ankiNote[fields[Deck.DEFINITION_SCORE_KEY][0]] = u'%d' % int(dictMorphemesScore)
            #                except KeyError: pass
            #      
            #    except KeyError: pass
            
            flds = joinFields(ankiNote.fields)
            if flds != joinFields(origFlds):
                modifiedFields.append(dict(nid=ankiNote.id,flds=flds,u=self.col.usn(),m=intTime()))
            ankiNotesId.append(ankiNote.id)
    
        self.col.db.executemany("update notes set flds=:flds,mod=:m,usn=:u where id=:nid", modifiedFields)
        self.col.updateFieldCache(ankiNotesId)
    
    def changeDueCards(self, language):
        
        now = intTime()
        cards = self.notesService.getAllCardsOrderByScore(language = language)

        d = []
        for card in cards:
            if card.score != 0:
                due = card.score
                d.append(dict(now=now, due=due, usn=self.col.usn(), cid=card.id))
        self.col.db.executemany("update cards set due=:due, mod=:now, usn=:usn where id = :cid", d)

    # Mark Duplicate
    def markDuplicateNotes(self, deck):
        
        ankiDeck = self.deckManager.get(deck.id)
        
        cards = self.notesService.getAllCardsOrderByScore(deck = deck)
        ankiNotesId = list()
    
        ankiNotes = AnkiHelper.getNotes(ankiDeck)
        ankiNotesDict = dict()
        for ankiNote in ankiNotes:
            ankiNotesDict[ankiNote.id] = ankiNote
    
        uniqueMorphemes = dict()
        #i = 0
        for card in cards:
            note = self.notesService.getNoteById(card.noteId)
            morphemes = self.notesService.getMorphemes(note)
            
            noteHasNewMorphemes = False
            for morpheme in morphemes:
                if morpheme.id not in uniqueMorphemes:
                    uniqueMorphemes[morpheme.id] = morpheme.id
                    noteHasNewMorphemes = True
            
            try:
                ankiNote = ankiNotesDict[note.ankiNoteId]
            except Exception:continue
            
            ankiNote.tags = canonifyTags(deleteTags(u'LxDuplicate', ankiNote.tags))
            if noteHasNewMorphemes == False:
                log(str(note) + " is Duplicate")
                ankiNote.tags = canonifyTags(addTags(u'LxDuplicate', ankiNote.tags))
                ankiNotesId.append(int(ankiNote.id))

        log(ankiNotesId)
        ankiDeck.updateNoteTags(ankiNotesId)
        self.col.save()


