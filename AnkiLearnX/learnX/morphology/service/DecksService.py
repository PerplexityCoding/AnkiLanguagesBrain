#-*- coding: utf-8 -*-

from learnX.morphology.db.dao.DeckDao import *

from learnX.utils.Log import *


class DecksService:
    def __init__(self, serviceLocator):
        self.serviceLocator = serviceLocator
        self.deckDao = DeckDao()
    
    def setupServices(self):
        self.languagesService = self.serviceLocator.getLanguagesService()
    
    # Unused
    def listDecks(self):
        list = self.deckDao.list()
    
        for deck in list:
            if deck.languageId != None:
                deck.language = self.languagesService.getLanguageById(deck.languageId)
        return list
    
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
        
    def getDecksPathChanged(self):
        return self.deckDao.listDeckPathWithFactsModified()
    
    def createDeck(self, deckName, deckPath):
        
        deck = Deck(deckName, deckPath, False, None, None, None)
        deck = self.deckDao.insert(deck)
        
        return deck
    
    def getDeck(self, deckName, deckPath):
        
        deck = self.deckDao.findByName(deckName, deckPath)
        if deck == None:
            deck = self.createDeck(deckName, deckPath)
        
        if deck.languageId != None:
            deck.language = self.languagesService.getLanguageById(deck.languageId)
        
        return deck
    
    def getDeckByPath(self, deckPath):
        deck = self.deckDao.findByPath(deckPath)
        
        if deck.languageId != None:
            deck.language = self.languagesService.getLanguageById(deck.languageId)
        
        return deck
    
    def getDeckById(self, id):
        return self.deckDao.findById(id)
    
    def countMorphemes(self, deck):
        self.deckDao.countMorphemes(deck)
        self.deckDao.update(deck)
    
    def changeLanguage(self, deck, languageName):

        deck.language = self.languagesService.getLanguageByName(languageName)
        if deck.language == None:
            deck.language = self.languagesService.addLanguage(languageName)
        deck.languageId = deck.language.id
        
        deck = self.deckDao.update(deck)
        
        return deck
    
    def enableDeck(self, deck):
        
        deck.enabled = True
        deck = self.deckDao.update(deck)
        
        return deck
        
    def disableDeck(self, deck):
        
        deck.enabled = False
        deck = self.deckDao.update(deck)
        
        return deck
    
    def updateDeck(self, deck):
        return self.deckDao.update(deck)
        