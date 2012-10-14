#-*- coding: utf-8 -*-
from sys import *


from languagesBrain.morphology.service.ServicesLocator import *

from languagesBrain.morphology.service.DecksService import *
from languagesBrain.morphology.service.LanguagesService import *
from languagesBrain.morphology.service.MorphemesService import *
from languagesBrain.morphology.service.FactsService import *
from languagesBrain.morphology.db.LanguagesBrainDB. import *
from languagesBrain.utils.Log import *
from languagesBrain.morphology.db.dao.MorphemeLemmeDao import *
from languagesBrain.morphology.db.dto.Deck import *

from languagesBrain.morphology.service.FactsService import *

serviceLocator = ServicesLocator.getInstance()

#log(serviceLocator.getFactsService())

#cst = CstLemmatizer()
#cst.lemmatize("test")

#LanguagesBrainDB..getInstance().createDataBase()
clearLog()
languagesService = serviceLocator.getLanguagesService()
#factsService = serviceLocator.getFactsService()
#tagger = serviceLocator.getStanfordPosTagger()
#print(tagger.posTag("Bonjour ca va ?"))
#print(tagger.posTag("Bonjour ca va et toi ?"))

decks = serviceLocator.getDecksService().listDecks()
#for deck in decks:
#    deck.fields = {
#        Deck.LB_SCORE_KEY : ("LearnXScore", False, True),
#        Deck.VOCAB_SCORE_KEY : ("VocabScore", False, True),
#        Deck.UNKNOWNS_KEY : ("UnknownMorphemes", False, False),
#        Deck.LEARNTS_KEY : ("LearntMorphemes", False, False),
#        Deck.KNOWNS_KEY : ("KnownMorphemes", False, False),
#        Deck.MATURES_KEY : ("MatureMorphemes", False, False),
#        Deck.COPY_UNKNOWN_1_TO_KEY : ("VocabExpression", False, False),
#        Deck.COPY_MATURE_TO_KEY : ("SentenceExpression", False, False),
#        Deck.DEFINITION_NAME_KEY : ("DefinitionKey", False, False),
#        Deck.DEFINITION_KEY : ("Definition", False, False),
#        Deck.DEFINITION_SCORE_KEY : ("DefinitionScore", False, False)
#    }
#    serviceLocator.getDecksService().updateDeck(deck)
    

#languagesService.countMorphemes(None)


#factsService.computeCardsMaturity()
#morphemesService = MorphemesService()
#factService = FactsService()

#lemmeDao = MorphemeLemmeDao()

#morphemes = morphemesService.extractMorphemes("私")
#print morphemes

#lemmeDao.persistAll(morphemes)

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
