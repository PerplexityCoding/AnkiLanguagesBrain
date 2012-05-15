
from learnX.morphology.db.dao.MorphemeLemmeDao import *
from learnX.morphology.db.dao.MorphemeDao import *
from learnX.morphology.db.dao.NoteDao import *
from learnX.morphology.db.dao.CardDao import *
from learnX.morphology.db.dao.DeckDao import *
from learnX.morphology.db.dao.DefinitionDao import *

from learnX.morphology.db.dto.Card import *
from learnX.morphology.db.dto.Morpheme import *

from learnX.utils.Log import *
from learnX.utils.Utils import *
from learnX.utils.KanjiHelper import *

from learnX.morphology.lemmatizer.cst.CstLemmatizer import *

class MorphemesService:
    
    def __init__(self, serviceLocator):
        self.serviceLocator = serviceLocator
        
        self.lemmeDao = MorphemeLemmeDao()
        self.morphemeDao = MorphemeDao()
        self.noteDao = NoteDao()
        self.cardDao = CardDao()
        self.deckDao = DeckDao()
        self.definitionDao = DefinitionDao()
    
    def setupServices(self):
        self.decksService = self.serviceLocator.getDecksService()
        self.notesService = self.serviceLocator.getNotesService()


    def extractMorphemes(self, expression, deck, language):
        morphemes = language.posTagger.posMorphemes(expression, deck, language)
        return morphemes
    
    def analyzeLemmes(self, notes, deck, language):
    
        # Unique Morphemes
        log("Extract Morphemes")
        allUniqueMorphLemmes = dict()
        for note in notes:
            morphLemmes = self.extractMorphemes(note.ankiNote[deck.expressionField], deck, language)
            noteMorphLemmes = list()
            for morphLemme in morphLemmes:
                if morphLemme in allUniqueMorphLemmes:
                    morphLemme = allUniqueMorphLemmes[morphLemme]
                else:
                    allUniqueMorphLemmes[morphLemme] = morphLemme
                noteMorphLemmes.append(morphLemme)
            note.morphLemmes = noteMorphLemmes
        
        allUniqueMorphLemmes = Utils.getList(allUniqueMorphLemmes)
        
        log("Lemmatize Morphemes : " + str(len(allUniqueMorphLemmes)))
        if language.lemmatizer:
            language.lemmatizer.lemmatizeMorphemes(allUniqueMorphLemmes)
        
        self.filterMorphLemmes(allUniqueMorphLemmes)
        
        self.rankMorphLemmes(allUniqueMorphLemmes)
        
        log("persist All Lemmes")
        self.lemmeDao.persistLemmes(allUniqueMorphLemmes)
    
    def analyzeMorphemes(self, notes, deck, language):
        
        log("Compute Notes <-> Morphemes")
        allMorphemes = list()
        for note in notes:
            noteUniqueMorphemes = list()
            for morphLemme in note.morphLemmes:
                morpheme = Morpheme(note.id, -1, False, morphLemme.id, -1)
                if morpheme not in noteUniqueMorphemes:    
                    noteUniqueMorphemes.append(morpheme)
                    allMorphemes.append(morpheme)
            note.expressionCsum = Utils.fieldChecksum(note.ankiNote[deck.expressionField])
            note.lastUpdated = note.ankiNote.mod
            note.ankiNote = None
        
        log("persist All Morphemes")
        self.morphemeDao.persistMorphemes(allMorphemes)
        
        log("update All")
        self.noteDao.updateNotes(notes) 
        
        for note in notes:
            note.morphLemmes = None
    
    # FIXME: on considère qu'il y a une seul carte par note ! pour le moment
    def refreshInterval(self, modifiedCards):
        
        for card in modifiedCards:
            card.interval = card.ankiCard.ivl
            
        self.cardDao.updateCards(modifiedCards)
        self.morphemeDao.updateInterval(modifiedCards)
        
    def resetLemmesChanged(self):
        return self.lemmeDao.resetLemmesChanged()
    
    def getLemmesFromNote(self, note):
        return self.lemmeDao.getLemmesFromNote(note)
