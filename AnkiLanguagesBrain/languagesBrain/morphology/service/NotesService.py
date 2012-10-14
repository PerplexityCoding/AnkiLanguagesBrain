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
            note = Note(ankiCard.note.id)
            note.ankiNote = ankiCard.note
            notes.append(note)
        
        log("persist")
        return self.note_dao.persistNotes(notes)  
        
    def retrieveAllCards(self, deck, ankiCards):
        
        log("list all cards")
        cards = list()
        for ankiCard in ankiCards:
            card = Card(ankiCard.id, deck.id, ankiCard.note.id)
            card.ankiCard = ankiCard
            cards.append(card)
        
        log("persist")
        return self.card_dao.persistCards(cards)    
    
    def getAllCards(self):
        return self.card_dao.selectAllCards()
    
    def computeNotesScore(self, notes):
        
        if notes == None:
            return None
        
        log("Compute Notes " + str(len(notes)))
        
        modifiedNotes = list()
        for note in notes:
            lemmes = self.lemmeDao.getLemmeIntervalFromNote(note) # surly slow ?
            score = 0
            for lemme in lemmes:
                maxInterval = lemme[0]
                morphemeScore = lemme[1]
            
                factor = pow(2, -1.0 * maxInterval / 24.0) # number between 1 and 0; lim (itv -> +inf) -> 0
                score += 1000 * factor + morphemeScore
            
            if note.score == 0 or note.score == None or abs(int(note.score) - int(score)) >= 15:
                note.score = score
                modifiedNotes.append(note)
        
        log("Modified Notes " + str(len(modifiedNotes)))
        if len(modifiedNotes) > 0:
            self.note_dao.updateNotes(modifiedNotes)
            
            return modifiedNotes
        
        return None


    
