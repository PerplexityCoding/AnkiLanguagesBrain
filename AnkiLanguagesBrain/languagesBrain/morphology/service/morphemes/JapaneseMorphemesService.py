
from learnX.morphology.service.MorphemesService import *


class JapaneseMorphemesService(MorphemesService):
    
    def __init__(self, serviceLocator):
        MorphemesService.__init__(self, serviceLocator)
        
        self.initFactors()
    
    # return a Rank between 0 and 500
    def rankKanji(self, kanji):
        kanjiFreq, kanjiStrokeCount = KanjiHelper.getKanjiInfo(kanji)
        
        freqScore =  pow(2, kanjiFreq / 900) * 35.0
        if freqScore > 350:
            freqScore = 350.0
        
        strokeScore = kanjiStrokeCount * 150.0 / 28.0
        if strokeScore > 150:
            strokeScore = 150.0
        
        return freqScore + strokeScore

    def initFactors(self):
        self.cachePow = dict()
        for i in range(1000):
            self.cachePow[i] = pow(2, -1.0 * i / 24.0)

    def getFactor(self, interval):
        return self.cachePow[interval]

    # Adapted from MorphMan 2
    def rankMorpheme(self, intervalDb, expr, read, rank):
        score = rank
        
        if read == None or rank == None:
            return 0
        
        if (expr, read) in intervalDb:
            interval = intervalDb[(expr, read)]
            score = score * self.getFactor(interval)
        else:
            hasKanji = False
            for i, c in enumerate(expr):
                # skip non-kanji
                if c < u'\u4E00' or c > u'\u9FBF': continue
                
                hasKanji = True
                npow = 0
                for (e,r), ivl in intervalDb.iteritems():
                    # has same kanji
                    if c in e:
                        if npow > -1.0: npow -= 0.25
                        # has same kanji at same pos
                        if len(e) > i and c == e[i]:
                            if npow > -1.5: npow -= 0.2
                            # has same kanji at same pos with similar reading
                            if i == 0 and read[0] == r[0] or i == len(expr)-1 and read[-1] == r[-1]:
                                npow -= 1.0
                        npow = npow * (1.0 - self.getFactor(ivl))
                score *= pow(2, npow)
        return score
    
    def rankMorphLemmes(self, lemmes):
        
        log("rankMorphemes")
        for lemme in lemmes:
            
            expr = lemme.base 
            lemme.rank = len(expr) * 10
            
            for i,c in enumerate(expr):
                # skip non-kanji
                if c < u'\u4E00' or c > u'\u9FBF': continue
                
                lemme.rank += self.rankKanji(c)
            
    def computeMorphemesScore(self, allLemmes):
        
        log("lemmeDao.getMorphemes() Start")
        if allLemmes == None or len(allLemmes) <= 0:
            return set()
            
        log("Rank Morphemes Start: " + str(len(allLemmes)))
        intervalDb = self.lemmeDao.getKnownLemmesIntervalDB()
        
        modifiedLemmes = list()
        for lemme in allLemmes:
            score = self.rankMorpheme(intervalDb, lemme.base, lemme.read, lemme.rank)
            if lemme.score == None or lemme.score == 0 or abs(int(lemme.score) - int(score)) >= 5:
                lemme.score = score
                modifiedLemmes.append(lemme)
        
        log("Update all Score " + str(len(modifiedLemmes)))
        if len(modifiedLemmes) > 0:
            self.lemmeDao.updateLemmesScore(modifiedLemmes)
        
            log("Mark Modified Notes: " + str(len(modifiedLemmes)))
            notes = self.morphemeDao.getModifiedNotes(modifiedLemmes)
            log("getModifiedNotes() : " + str(len(modifiedLemmes)))
            return notes
        
        return set()
    
    def getLinkedMorphemes(self, allLemmes):
        
        if len(allLemmes) <= 0:
            return set()
        
        kanjis = set()
        for lemme in allLemmes:
            expr = lemme.base
            for i, c in enumerate(expr):
                # skip non-kanji
                if c < u'\u4E00' or c > u'\u9FBF': continue
                kanjis.add(c)

        if len(kanjis) < 0:
            return allLemmes
        return self.lemmeDao.getChangedAllMorphemesFromKanjis(kanjis)
    
    def filterMorphLemmes(self, morphLemmesList):
        # Do nothing
        return morphLemmesList
        