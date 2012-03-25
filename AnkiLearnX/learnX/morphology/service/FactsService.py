#-*- coding: utf-8 -*-

from learnX.morphology.db.dao.FactDao import *
from learnX.morphology.db.dao.CardDao import *
from learnX.morphology.db.dao.MorphemeDao import *
from learnX.morphology.db.dao.DeckDao import *

from learnX.morphology.db.dto.Morpheme import *
from learnX.morphology.db.dto.Fact import *

class FactsService:
    def __init__(self):
        self.fact_dao = FactDao()
        self.card_dao = CardDao()
        self.morpheme_dao = MorphemeDao()
        self.deck_dao = DeckDao()
        
    def getFact(self, deck, ankiFactId):
        fact = self.fact_dao.findById(deck, ankiFactId)
        if fact == None:
            fact = Fact(deck.id, ankiFactId, None, None, False, Fact.STATUS_NONE, False, 0)
            fact.deck = deck
            fact = self.fact_dao.insert(fact)

        return fact

    def getAllFacts(self, deck, ankiFacts):
        
        facts = []
        factsToInsert = []
        i = 0
        for ankiFact in ankiFacts:
            fact = self.fact_dao.findById(deck, ankiFact.id)
            if fact == None:
                fact = Fact(deck.id, ankiFact.id, None, None, False, Fact.STATUS_NONE, False, 0)
                fact.deck = deck
                factsToInsert.append(fact)
            fact.ankiFactIndex = i
            fact.ankiLastModified = ankiFact.modified
            facts.append(fact)
            i += 1

        if len(factsToInsert) > 0:
            self.fact_dao.insertAll(factsToInsert)
        
        return facts
    
    def getAllCardsOrderByScore(self):
        return self.card_dao.getCardsOrderByScore()
    
    def calcCardStatus(self, ankiCard):
        if ankiCard.interval < 4:
            return Card.STATUS_NONE
        if ankiCard.interval < 7:
            return Card.STATUS_LEARNT
        if ankiCard.interval < 21:
            return Card.STATUS_KNOWN
        return Card.STATUS_MATURE
        
    def getAllCards(self, deck, ankiCards):
        
        cards = []
        cardsToInsert = []
        for ankiCard in ankiCards:
            card = self.card_dao.findById(deck, ankiCard.id)
            if card == None:
                fact = self.getFact(deck, ankiCard.fact.id)
                status = self.calcCardStatus(ankiCard)
                card = Card(deck.id, fact.id, ankiCard.id, status, False)
                card.deck = deck
                card.fact = fact
                cardsToInsert.append(card)
            card.ankiLastModified = ankiCard.modified
            cards.append(card)

        if len(cardsToInsert) > 0:
            self.card_dao.insertAll(cardsToInsert)
        
        return cards
    
    def getAllChanged(self):
        facts = self.fact_dao.selectAllChanged() 
        decks = dict()
        for fact in facts:
            deck = None
            try:
                deck = decks[fact.deckId]
            except KeyError as e:
                deck = self.deck_dao.findById(fact.deckId)
                decks[fact.deckId] = deck
            fact.deck = deck
        return facts
    
    def computeCardsMaturity(self):
        
        facts = self.fact_dao.findByChangedMorphemes()
        for fact in facts:
            morphemes = self.morpheme_dao.getMorphemesFromFact(fact)
        
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
            log(morphemesScore)
            total = len(morphemes)
            mature = len(matureMorphemes)
            known = len(knownMorphemes)
            learnt = len(learnMorphemes)
            unknown = len(unknownMorphemes)
            
            status = fact.status
            if unknown == 0:
                if learnt == 0 and known == 0:
                    status = Fact.STATUS_REVIEW_EASY
                elif learnt > 0:
                    status = Fact.STATUS_REVIEW_HARD
                else :
                    status = Fact.STATUS_REVIEW_MEDIUM
            elif unknown == 1:
                if learnt == 0 and known == 0:
                    status = Fact.STATUS_LEARN_EASY
                elif learnt > 0:
                    status = Fact.STATUS_LEARN_HARD
                else :
                    status = Fact.STATUS_LEARN_MEDIUM
            else:
                status = Fact.STATUS_TOO_DIFFICULT

            if status != fact.status:
                fact.status = status
                fact.statusChanged = True
            
            score = (mature * 1 + known * 2 + learnt * 6 + unknown * 30) * 300 + morphemesScore
            if score != fact.score:
                fact.score = score
                fact.statusChanged = True
            
        self.fact_dao.updateAll(facts) 

        self.morpheme_dao.clearMorphemesStatus()

        return facts

    def changeMorphemes(self, fact, morphemes):
        self.fact_dao.insertFactMorphemes(fact, morphemes)
        
        fact.morphemes = morphemes
        return fact


        