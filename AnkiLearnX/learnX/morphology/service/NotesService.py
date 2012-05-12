#-*- coding: utf-8 -*-

from learnX.morphology.db.dao.NoteDao import *
from learnX.morphology.db.dao.CardDao import *
from learnX.morphology.db.dao.MorphemeDao import *
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
        self.deck_dao = DeckDao()
        self.definitionDao = DefinitionDao()
        
    def setupServices(self):
        self.decksService = self.serviceLocator.getDecksService()
        
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
        note.deck = self.deck_dao.findById(note.deckId)
        
        return note
    
    def getAllNotes(self, col, deck, ankiCards):
        
        notes = []
        notesToInsert = []
        for ankiCard in ankiCards:
            ankiCard = col.getCard(ankiCard)
            ankiNote = ankiCard.note()
            note = self.note_dao.findByAnkiNoteId(deck, ankiNote.id)
            if note == None:
                note = Note(deck.id, ankiNote.id, None, None, False, Note.STATUS_NONE, False, 0)
                note.deck = deck
                notesToInsert.append(note)
            note.ankiNote = ankiNote
            notes.append(note)

        if len(notesToInsert) > 0:
            self.note_dao.insertAll(notesToInsert)
        
        return notes
    
    def getAllCardsOrderByScore(self, deck = None, language = None):
        if language:
            decksId = self.decksService.listDecksIdByLanguage(language)
        else:
            decksId = [deck.id]
        log(decksId)
        return self.card_dao.getCardsOrderByScore(decksId)
    
    def calcCardStatus(self, deck, ankiCard):
        if ankiCard.ivl == 0:
            return Card.STATUS_NONE
        if ankiCard.ivl < deck.knownTreshold:
            return Card.STATUS_LEARNT
        if ankiCard.ivl < deck.matureTreshold:
            return Card.STATUS_KNOWN
        return Card.STATUS_MATURE
        
    def getAllCardsChanged(self, col, deck, ankiCards):
        
        changedCards = []
        cardsToInsert = []
        cardsToUpdate = []
        for ankiCard in ankiCards:
            ankiCard = col.getCard(ankiCard)
            card = self.card_dao.findById(deck, ankiCard.id)
            status = self.calcCardStatus(deck, ankiCard)
            if card == None:
                note = self.getNote(deck, ankiCard.note().id)
                card = Card(deck.id, note.id, ankiCard.id, ankiCard.ivl, status, True)
                card.deck = deck
                card.note = note
                cardsToInsert.append(card)
                changedCards.append(card)
            else:
                if card.interval != ankiCard.ivl:
                    card.interval = ankiCard.ivl
                    card.statusChanged = True
                if status != card.status:
                    card.statusChanged = True
                    changedCards.append(card)
                card.status = status               
                cardsToUpdate.append(card)  
            card.ankiLastModified = ankiCard.mod
            
        if len(cardsToInsert) > 0:
            self.card_dao.insertAll(cardsToInsert)
        
        if len(cardsToUpdate) > 0:
            self.card_dao.updateAll(cardsToUpdate)
        
        return changedCards
    
    def getAllNotesChanged(self, language):
        return self.getAllNotesByLanguage(language, 1)
    
    def getAllNotesByLanguage(self, language, statusChanged = None):
        
        decksId = self.decksService.listDecksIdByLanguage(language)
        notes = self.note_dao.selectAll(decksId, statusChanged) 
        decks = dict()
        for note in notes:
            deck = None
            try:
                deck = decks[note.deckId]
            except KeyError as e:
                deck = self.deck_dao.findById(note.deckId)
                decks[note.deckId] = deck
            note.deck = deck
        return notes
    
    def computeNotesMaturity(self, language):
        
        decksId = self.decksService.listDecksIdByLanguage(language)
        notes = self.note_dao.selectAll(decksId, None) #FIXME: Buggggg with other decks !! replace with all notes for now ?
        for note in notes:
            morphemes = self.morpheme_dao.getMorphemesFromNote(note)
        
            matureMorphemes = []
            knownMorphemes = []
            learnMorphemes = []
            unknownMorphemes = []
            morphemesScore = 0
            for morpheme in morphemes:
                if morpheme.status == Morpheme.STATUS_MATURE:
                    matureMorphemes.append(morpheme)
                if morpheme.status == Morpheme.STATUS_KNOWN:
                    knownMorphemes.append(morpheme)
                if morpheme.status == Morpheme.STATUS_LEARNT:
                    learnMorphemes.append(morpheme)
                if morpheme.status == Morpheme.STATUS_NONE:
                    unknownMorphemes.append(morpheme)
                morphemesScore += morpheme.score
            total = len(morphemes)
            mature = len(matureMorphemes)
            known = len(knownMorphemes)
            learnt = len(learnMorphemes)
            unknown = len(unknownMorphemes)
            
            status = note.status
            if unknown == 0:
                if learnt == 0 and known == 0:
                    status = Note.STATUS_REVIEW_EASY
                elif learnt > 0:
                    status = Note.STATUS_REVIEW_HARD
                else :
                    status = Note.STATUS_REVIEW_MEDIUM
            elif unknown == 1:
                if learnt == 0 and known == 0:
                    status = Note.STATUS_LEARN_EASY
                elif learnt > 0:
                    status = Note.STATUS_LEARN_HARD
                else :
                    status = Note.STATUS_LEARN_MEDIUM
            else:
                status = Note.STATUS_TOO_DIFFICULT

            if status != note.status:
                note.status = status
                note.statusChanged = True
            
            score = (mature * 1 + known * 2 + learnt * 6 + unknown * 30) * 300 + morphemesScore
            if score != note.score:
                note.score = score
                note.statusChanged = True
            
        self.note_dao.updateAll(notes) 

        #self.morpheme_dao.clearMorphemesStatus()

        return notes

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