#-*- coding: utf-8 -*-

from learnX.morphology.db.dao.LanguageDao import *

from collections import defaultdict

class LanguagesService:
    
    languageDao = LanguageDao()
    
    languagesName = dict({
        "English"  : 1,
        "Francais" : 2
        #"日本語"    : 500
    })
    
    def getAvailableLanguageName(self):
        availableLanguageName = []
        #log(self.languagesName)
        for languageName in sorted(self.languagesName, key=self.languagesName.get, reverse=False):
            availableLanguageName.append(str(languageName))
        return availableLanguageName
    
    def getLanguageNameFromCode(self, code):
        for v,k in self.languagesName.iteritems():
            if k == code :
                return str(v)
        return None
    
    def getCodeFromLanguageName(self, language):
        return self.languagesName[language]
    
    def getLanguageByCode(self, code):
        return self.languageDao.findByCode(code)
    
    def getLanguageByName(self, name):
        #log("getlbyName: " + str(self.languagesName[name]))
        return self.languageDao.findByCode(self.languagesName[name])
    
    def listLanguages(self):
        return self.languageDao.list()

    def addLanguage(self, name, posType = 1):
        
        languageCode = self.languagesName[name]
        language = Language(languageCode, posType)
        return self.languageDao.insert(language)
    