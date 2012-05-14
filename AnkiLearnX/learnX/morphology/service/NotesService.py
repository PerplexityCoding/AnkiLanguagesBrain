#-*- coding: utf-8 -*-

from learnX.morphology.db.dao.NoteDao import *
from learnX.morphology.db.dao.CardDao import *
from learnX.morphology.db.dao.MorphemeDao import *
from learnX.morphology.db.dao.MorphemeLemmeDao import *
from learnX.morphology.db.dao.DeckDao import *
from learnX.morphology.db.dao.DefinitionDao import *

from learnX.morphology.db.dto.Morpheme import *
from learnX.morphology.db.dto.Note import *

class NotesService:
    def __init__(self, serviceLocator):
        self.serviceLocator = serviceLocator
        self.note_dao = NoteDao()
        self.card_dao = CardDao()
        self.morpheme_dao = MorphemeDao()
        self.lemmeDao = MorphemeLemmeDao()
        self.deck_dao = DeckDao()
        self.definitionDao = DefinitionDao()
        
    def setupServices(self):
        self.decksService = self.serviceLocator.getDecksService()
        
    def retrieveAllNotes(self, ankiCards):    
        
        notes = list()
        for ankiCard in ankiCards:
            ankiNote = ankiCard.note()
            note = Note(ankiNote.id)
            note.ankiNote = ankiNote
            notes.append(note)
            
        return self.note_dao.persistNotes(notes)  
        
    def retrieveAllCards(self, deck, ankiCards):
        
        cards = list()
        for ankiCard in ankiCards:
            card = Card(ankiCard.id, deck.id, ankiCard.note().id)
            card.ankiCard = ankiCard
            cards.append(card)
        
        return self.card_dao.persistAll(cards)    
        
    def getNote(self, deck, ankiNoteId):
        note = self.note_dao.findByAnkiNoteId(deck, ankiNoteId)
        if note == None:
            note = Note(deck.id, ankiNoteId, None, None, False, Note.STATUS_NONE, False, 0)
            note.deck = deck
            note = self.note_dao.insert(note)

        return note
    
    def getDefinition(self, note):
        return self.definitionDao.getDefinition(note.id)

    def getNoteById(self, ankiNoteId):
        note = self.note_dao.findById(ankiNoteId)
        return note
        
    def getAllCardsOrderByScore(self, deck = None, language = None):
        if language:
            decksId = self.decksService.listDecksIdByLanguage(language)
        else:
            decksId = [deck.id]
        return self.card_dao.getCardsOrderByScore(decksId)
    
    def getAllNotesChanged(self, language):
        return self.getAllNotesByLanguage(language)
    
    def getAllNotesByLanguage(self, language):
        return self.note_dao.selectAll()
    
    def computeNotesScore(self, deck):
        
        notes = self.note_dao.selectAll()
        for note in notes:
            lemmes = self.lemmeDao.getLemmeIntervalFromNote(note)
            score = 0
            for lemme in lemmes:
                maxInterval = lemme[0]
                morphemeScore = lemme[1]
            
                factor = pow(2, -1.0 * maxInterval / 24.0) # number between 1 and 0; lim (itv -> +inf) -> 0
                score += 1000 * factor + morphemeScore
            note.score = score
            
        self.note_dao.updateAll(notes) 

    def changeMorphemes(self, note, morphemes):
        self.note_dao.insertNoteMorphemes(note, morphemes)
        
        note.morphemes = morphemes
        return note
    
    def getMorphemes(self, note):
        return self.morpheme_dao.getMorphemesFromNote(note, True)

    def getAllNewCards(self, language):
        decksId = self.decksService.listDecksIdByLanguage(language)
        return self.card_dao.getAllNewCards(decksId)

    def clearAllNotesStatus(self, language):
        decksId = self.decksService.listDecksIdByLanguage(language)
        self.note_dao.clearAllNotesStatus(decksId)
