#-*- coding: utf-8 -*-

from learnX.morphology.db.dao.DeckDao import *

from learnX.morphology.service.LanguagesService import *
from learnX.morphology.service.FactsService import *

class DecksService:
    
    deckDao = DeckDao()
    languagesService = LanguagesService()
    factsService = FactsService()
    
    def listDecks(self):
        list = self.deckDao.list()
    
        for deck in list:
            if deck.languageId != None:
                deck.language = self.languagesService.getLanguageByCode(deck.languageId)
        return list
    
    def createDeck(self, deckName, deckPath):
        
        deck = Deck(deckName, deckPath, False, None, "Expression", None)
        deck = self.deckDao.insert(deck)
        
        return deck
    
    def getDeck(self, deckName, deckPath):
        
        deck = self.deckDao.findByName(deckName, deckPath)
        if deck == None:
            deck = self.createDeck(deckName, deckPath)
        
        if deck.languageId != None:
            deck.language = self.languagesService.getLanguageByCode(deck.languageId)
        
        self.factsService.countMorphemes(deck)
        
        return deck
    
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
        