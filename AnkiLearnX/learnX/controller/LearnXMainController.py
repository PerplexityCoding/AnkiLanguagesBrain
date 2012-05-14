
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
        log("Start")
        self.analyzeDeck(deck)
        
        log("Process Notes Start")
        self.processNotes(deck.language)
        log("Process Notes Stop")
        
        self.interface.refreshAll()
        log("End")
    
    def analyzeLanguage(self, language):
        
        log("Start")
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
            if note.expressionCsum != None and int(Utils.fieldChecksum(note.ankiNote[deck.expressionField])) == int(note.expressionCsum):
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
        
        if len(modifiedCards) > 0:
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
    
    def markNotes(self, language):
        notes = self.notesService.getAllNotesByLanguage(language)
        ankiNotesId = list()
        
        #i = 0
        modifiedFields = []
        for note in notes:
            try:
                ankiNote = self.col.getNote(note.id)
            except Exception: continue
            
            tm = self.col.tags
            origFlds = joinFields(ankiNote.fields)
            origTags = tm.join(ankiNote.tags)
            
            fields = { #FIXME
                Deck.LEARNX_SCORE_KEY : ("LearnXScore", False, True),
                Deck.VOCAB_SCORE_KEY : ("VocabScore", False, True),
                Deck.UNKNOWNS_KEY : ("UnknownMorphemes", False, False),
                Deck.KNOWNS_KEY : ("KnownMorphemes", False, False),
                Deck.COPY_UNKNOWN_1_TO_KEY : ("VocabExpression", False, False),
                Deck.DEFINITION_SCORE_KEY : ("DefinitionScore", False, False)
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
            
            ankiNote.tags = tm.split(tm.remFromStr(u'LxReview LxToLearn LxTooDifficult', tm.join(ankiNote.tags)))
            
            if len(unknownMorphemes) == 1:
                if fields[Deck.COPY_UNKNOWN_1_TO_KEY][1]:
                    try: ankiNote[fields[Deck.COPY_UNKNOWN_1_TO_KEY][0]] = u','.join(u for u in unknownMorphemes)
                    except KeyError: pass
                tag = u'LxToLearn'
            elif len(unknownMorphemes) == 0:
                tag = u'LxReview'
            else:
                tag = u'LxTooDifficult'
            ankiNote.tags = tm.split(tm.addToStr(tag, tm.join(ankiNote.tags)))
            
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
            tags = tm.join(ankiNote.tags)
            
            if flds != origFlds or origTags != tags:
                modifiedFields.append(dict(nid=ankiNote.id, flds=flds, tags=tags, u=self.col.usn(), m=intTime()))
            ankiNotesId.append(ankiNote.id)
    
        self.col.tags.register([u'LxReview', u'LxToLearn', u'LxTooDifficult'])
        self.col.db.executemany("update notes set flds=:flds, tags=:tags, mod=:m,usn=:u where id=:nid", modifiedFields)
        self.col.updateFieldCache(ankiNotesId)
    
    def changeDueCards(self, language):
        
        now = intTime()
        log("select")
        cards = self.notesService.getAllNotesByLanguage(language)

        log("get Cards")
        d = []
        for card in cards:
            try:
                ankiCard = self.col.getCard(card.id)
            except Exception: continue
            
            if card.score != 0 and ankiCard.due != card.score:
                due = card.score
                d.append(dict(now=now, due=due, usn=self.col.usn(), cid=card.id))
                
        log("update")
        if len(d) > 0:
            self.col.db.executemany("update cards set due=:due, mod=:now, usn=:usn where id = :cid", d)


