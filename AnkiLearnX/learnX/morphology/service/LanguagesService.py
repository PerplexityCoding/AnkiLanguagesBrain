#-*- coding: utf-8 -*-

from learnX.morphology.db.dao.LanguageDao import *
from learnX.morphology.db.dao.DeckDao import *

from collections import defaultdict

from learnX.utils.Log import *

class LanguagesService:
    
    def __init__(self, serviceLocator):
        self.serviceLocator = serviceLocator
        self.languageDao = LanguageDao()
        self.deckDao = DeckDao()
        
        self.languagesName = dict({
            unicode("English", "utf-8")  : 1,
            unicode("Francais", "utf-8") : 2,
            unicode("日本語", "utf-8")   : 500
        })
    
    def setupServices(self):
        self.decksService = self.serviceLocator.getDecksService()
    
    def getAvailableLanguageName(self):
        availableLanguageName = []
        #log(self.languagesName)
        for languageName in sorted(self.languagesName, key=self.languagesName.get, reverse=False):
            availableLanguageName.append(languageName)
        return availableLanguageName
    
    def getLanguageNameFromCode(self, code):
        for v,k in self.languagesName.iteritems():
            if k == code :
                return v
        return None
    
    def getCodeFromLanguageName(self, language):
        return self.languagesName[language]
    
    def getLanguageByCode(self, code):
        return self.languageDao.findByCode(code)
    
    def getLanguageById(self, id):
        return self.languageDao.findById(id)
    
    def getLanguageByName(self, name):
        return self.languageDao.findByCode(self.languagesName[name])
    
    def listLanguages(self):
        return self.languageDao.list()

    def addLanguage(self, name, posType = 1):
        
        languageCode = self.languagesName[name]
        language = Language(languageCode, posType)
        return self.languageDao.insert(language)
    
    def countMorphemes(self, language):
        
        decksId = self.decksService.listDecksIdByLanguage(language)
        
        self.languageDao.countMorphemes(language, decksId)
        self.languageDao.update(language)
        