#-*- coding: utf-8 -*-
from sys import *


from learnX.morphology.service.ServicesLocator import *

from learnX.morphology.service.DecksService import *
from learnX.morphology.service.LanguagesService import *
from learnX.morphology.service.MorphemesService import *
from learnX.morphology.service.FactsService import *
from learnX.morphology.db.LearnXdB import *
from learnX.utils.Log import *
from learnX.morphology.db.dao.MecabMorphemeDao import *

serviceLocator = ServicesLocator.getInstance()

log(serviceLocator.getFactsService())


#LearnXdB.getInstance().createDataBase()
clearLog()
languagesService = serviceLocator.getLanguagesService()
factsService = serviceLocator.getFactsService()

#languagesService.countMorphemes(None)


#factsService.computeCardsMaturity()
#morphemesService = MorphemesService()
#factService = FactsService()

#mecabDao = MecabMorphemeDao()

#morphemes = morphemesService.extractMorphemes("私")
#print morphemes

#mecabDao.persistAll(morphemes)

#deck = decksService.createDeck("test2", "testo")
#deck = decksService.getDeck("test2", "testo")

#fact = factService.getFact(deck, 1)
#print fact




#print fact.morphemes

#print deck.fields

#deck2 = decksService.getDeck("test", "testo")
#print deck2

#language = languagesService.addLanguage("日本語")
#print language
#language = languagesService.addLanguage("Francais")
#print language

print languagesService.getAvailableLanguageName()

languages = languagesService.listLanguages()
for language in languages:
    print language
