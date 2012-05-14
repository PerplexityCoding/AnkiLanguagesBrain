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
        
        log("list all cards")
        notes = list()
        for ankiCard in ankiCards:
            ankiNote = ankiCard.note()
            note = Note(ankiNote.id)
            note.ankiNote = ankiNote
            notes.append(note)
        
        log("persist")
        return self.note_dao.persistNotes(notes)  
        
    def retrieveAllCards(self, deck, ankiCards):
        
        cards = list()
        for ankiCard in ankiCards:
            note = ankiCard.note()
            card = Card(ankiCard.id, deck.id, note.id)
            card.ankiCard = ankiCard
            cards.append(card)
        
        return self.card_dao.persistCards(cards)    
        
    def getAllNotesByLanguage(self, language):
        return self.note_dao.selectNotes()
    
    def computeNotesScore(self):
        
        notes = self.note_dao.selectNotes()
        for note in notes:
            lemmes = self.lemmeDao.getLemmeIntervalFromNote(note)
            score = 0
            for lemme in lemmes:
                maxInterval = lemme[0]
                morphemeScore = lemme[1]
            
                factor = pow(2, -1.0 * maxInterval / 24.0) # number between 1 and 0; lim (itv -> +inf) -> 0
                score += 1000 * factor + morphemeScore
            note.score = score
            
        self.note_dao.updateNotes(notes)
