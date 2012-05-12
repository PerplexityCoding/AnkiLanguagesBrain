
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
        
        realDeck = self.deckManager.get(deck.ankiDeckId)
        log(realDeck)
        log("Get All Notes / Cards")
        self.ankiCards = ankiCards = self.deckManager.cids(realDeck["id"])
        i = 0
        
        log("Store All Notes : " + str(len(ankiCards)) + " cards")
        notes = self.notesService.getAllNotes(self.col, deck, ankiCards)
        
        log("Determine Modified Notes : " + str(len(notes)))
        
        #XXX: Ne pas faire la vérification la 1er fois, prendre tous les notes !
        # Verifier a ne prendre que les notes modifié
        # Pas besoin pour anki 2 ?
        modifiedNotes = []
        for note in notes:
            if note.ankiNote.mod == note.lastUpdated:
                continue
            if note.expressionHash != None and Utils.fieldChecksum(note.ankiNote.__getitem__(deck.expressionField)) == note.expressionHash:
                continue
            modifiedNotes.append(note)
        
        log("Analyze Morphemes on " + str(len(modifiedNotes)) + " notes")
        if len(modifiedNotes) > 0:
            self.morphemesService.analyzeMorphemes(modifiedNotes, deck, deck.language)

        log("getAllCardsChanged")
        modifiedCards = self.notesService.getAllCardsChanged(self.col, deck, ankiCards)
        
        log("computeMorphemesMaturity: " + str(len(modifiedCards)) + " cards")
        if len(modifiedCards) > 0:
            self.morphemesService.computeMorphemesMaturity(modifiedCards)
        
        log("Calculed morpheme Score Start")
        self.morphemesService.computeMorphemesScore(deck.language)
        
        log("Analyze Definitions")
        #if deck.definitionField:
        #    self.morphemesService.analyseDefinition(deck, deck.language, notes, ankiNotes)
        
        log("decksService.countMorphemes Start")
        self.decksService.countMorphemes(deck)
        
        log("decksService.countMorphemes Start")
        self.languagesService.countMorphemes(deck.language)
        
        log("notesService.computeNotesMaturity Start")
        self.notesService.computeNotesMaturity(deck.language)
        
        log("Saves Decks Start")
        self.col.save()
        log("Saves Decks Stop")
        
    def processNotes(self, language):
        
        #log("self.setupProcessNotes()")
        #self.setupProcessNotes(language)

        log("self.markNotes()")     
        self.markNotes(language)
        
        log("self.changeDueCards()")     
        self.changeDueCards(language)
        
        self.notesService.clearAllNotesStatus(language)
        
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
    
    def markNotes(self, language):
        notes = self.notesService.getAllNotesByLanguage(language)
        ankiNotesId = list()
        
        #i = 0
        modifiedFields = []
        for note in notes:
            try:
                ankiNote = self.col.getNote(note.ankiNoteId)
            except Exception: continue
            
            origFlds = []
            origFlds.extend(ankiNote.fields)
            
            deck = note.deck
            fields = deck.fields
            
            morphemes = self.notesService.getMorphemes(note)
            morphemesScore, matureMorphemes, knownMorphemes, learnMorphemes, unknownMorphemes = self.getMorphemesScore(morphemes)
            
            if True: # FIXME: sure ?
                #if fields[Deck.LEARNX_SCORE_KEY][1]:
                try: ankiNote[fields[Deck.LEARNX_SCORE_KEY][0]] = u'%d' % int(note.score)
                except KeyError: pass
                
                #if fields[Deck.VOCAB_SCORE_KEY][1]:
                try: ankiNote[fields[Deck.VOCAB_SCORE_KEY][0]] = u'%d' % int(morphemesScore)
                except KeyError: pass
        
                #if fields[Deck.UNKNOWNS_KEY][1]:
                try: ankiNote[fields[Deck.UNKNOWNS_KEY][0]] = u','.join(u for u in unknownMorphemes)
                except KeyError: pass
        
                #if fields[Deck.LEARNTS_KEY][1]:
                try: ankiNote[fields[Deck.LEARNTS_KEY][0]] = u','.join(u for u in learnMorphemes)
                except KeyError: pass
                    
                #if fields[Deck.KNOWNS_KEY][1]:
                try: ankiNote[fields[Deck.KNOWNS_KEY][0]] = u','.join(u for u in knownMorphemes)
                except KeyError: pass
                    
                #if fields[Deck.MATURES_KEY][1]:
                try: ankiNote[fields[Deck.MATURES_KEY][0]] = u','.join(u for u in matureMorphemes)
                except KeyError: pass
    
                if len(unknownMorphemes) == 1:
                    #if fields[Deck.COPY_UNKNOWN_1_TO_KEY][1]:
                    try: ankiNote[fields[Deck.COPY_UNKNOWN_1_TO_KEY][0]] = u','.join(u for u in unknownMorphemes)
                    except KeyError: pass
                elif len(unknownMorphemes) == 0:
                    #if fields[Deck.COPY_MATURE_TO_KEY][1]:
                    try: ankiNote[fields[Deck.COPY_MATURE_TO_KEY][0]] = u'%s' % ankiNote[deck.expressionField]
                    except KeyError: pass
                
                self.col.tags.remFromStr(note.getAllStatusTag(), self.col.tags.join(ankiNote.tags))
                self.col.tags.addToStr(note.getAllStatusTag(), self.col.tags.join(ankiNote.tags))
                                                       
            if deck.definitionField:
                try:
                    ankiNote.tags = canonifyTags(deleteTags(u'LxDefKnown,LxDefMatch', ankiNote.tags))
                    definition = self.notesService.getDefinition(note)
                    
                    if definition and definition.definitionHash and int(definition.definitionHash) != 0:
                    
                        defMorphemes = self.morphemesService.getMorphemesDefinition(definition)
                        dictMorphemesScore, defMatureMorphemes, defKnownMorphemes, defLearnMorphemes, defUnknownMorphemes = self.getMorphemesScore(defMorphemes)
                        
                        if len(defUnknownMorphemes) == 0:
                            ankiNote.tags = canonifyTags(addTags(u'LxDefKnown', ankiNote.tags))
                        
                        defKeyMorphemes = self.morphemesService.getMorphemesDefinitionKey(definition)
                        defKeyMorphemesBase = "".join(m.morphLemme.base for m in defKeyMorphemes)
                        
                        if len(unknownMorphemes) == 1 and unknownMorphemes[0] in defKeyMorphemesBase:
                            ankiNote.tags = canonifyTags(addTags(u'LxDefMatch', ankiNote.tags))
                        
                        if fields[Deck.DEFINITION_SCORE_KEY][1]:
                            try: ankiNote[fields[Deck.DEFINITION_SCORE_KEY][0]] = u'%d' % int(dictMorphemesScore)
                            except KeyError: pass
                  
                except KeyError: pass
            
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
                d.append(dict(now=now, due=due, usn=self.col.usn(), cid=card.ankiCardId))
        self.col.db.executemany("update cards set due=:due,mod=:now,usn=:usn where id = :cid", d)

    # Mark Duplicate
    def markDuplicateNotes(self, deck):
        
        ankiDeck = self.deckManager.get(deck.ankiDeckId)
        
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


