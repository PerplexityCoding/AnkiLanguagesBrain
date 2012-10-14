#-*- coding: utf-8 -*-

from learnX.morphology.db.dao.DeckDao import *

from learnX.utils.Log import *


class DecksService:
    def __init__(self, serviceLocator):
        self.serviceLocator = serviceLocator
        self.deckDao = DeckDao()
    
    def setupServices(self):
        self.languagesService = self.serviceLocator.getLanguagesService()
        
    def listDecksByLanguage(self, language):
        list = self.deckDao.listDecksByLanguage(language.id)
        for deck in list:
            if deck.languageId != None:
                deck.language = self.languagesService.getLanguageById(deck.languageId)
        return list
    
    def listDecksIdByLanguage(self, language):
        decks = self.deckDao.listDecksByLanguage(language.id)
        decksId = []
        for deck in decks:
            decksId.append(deck.id)
        return decksId
        
    def getDeck(self, ankiDeckId):
        
        deck = self.deckDao.findDeckById(ankiDeckId)
        if deck == None:
            deck = Deck(ankiDeckId, False, True, None, None, None)
            deck = self.deckDao.insertDeck(deck)
        
        if deck.languageId != None:
            deck.language = self.languagesService.getLanguageById(deck.languageId)
        
        return deck
    
    def countMorphemes(self, deck):
        #FIXME
        deck = deck
    
    def changeLanguage(self, deck, languageName):

        deck.language = self.languagesService.getLanguageByName(languageName)
        if deck.language == None:
            deck.language = self.languagesService.addLanguage(languageName)
        deck.languageId = deck.language.id
        
        deck = self.deckDao.updateDeck(deck)
        
        return deck
    
    def enableDeck(self, deck):
        
        deck.enabled = True
        deck = self.deckDao.updateDeck(deck)
        
        return deck
        
    def disableDeck(self, deck):
        
        deck.enabled = False
        deck = self.deckDao.updateDeck(deck)
        
        return deck
    
    def resetFirstTime(self, deck):
        deck = self.deckDao.resetFirstTime(deck)
    
    def updateDeck(self, deck):
        return self.deckDao.updateDeck(deck)
        