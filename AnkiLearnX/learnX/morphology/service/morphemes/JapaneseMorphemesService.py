
from learnX.morphology.service.MorphemesService import *


class JapaneseMorphemesService(MorphemesService):
    
    def __init__(self, serviceLocator):
        MorphemesService.__init__(self, serviceLocator)
    
        # return a Rank between 0 and 100
    def rankKanji(self, kanji):
        kanjiFreq, kanjiStrokeCount = KanjiHelper.getKanjiInfo(kanji)
        
        freqScore = math.exp(kanjiFreq / 600.0)
        freqScore = freqScore / 1.5
        if freqScore > 100:
            freqScore = 100
        
        strokeScore = kanjiStrokeCount * 100.0 / 28.0
        if strokeScore > 100:
            strokeScore = 100
        
        kanjiScore = ((freqScore + strokeScore) / 2.0) * 2.0
        return kanjiScore

    # Adapted from MorphMan 2
    def rankMorpheme(self, knownDb, expr, read):
        wordEase = 0
        numCharsConsidered = 0
        hasKanji = False
        if (expr, read) in knownDb:
            for i,c in enumerate( expr ):
                if c < u'\u4E00' or c > u'\u9FBF': continue
                hasKanji = True
                wordEase += self.rankKanji(c)
        else:
            for i,c in enumerate( expr ):
                # skip non-kanji
                if c < u'\u4E00' or c > u'\u9FBF': continue
        
                hasKanji = True
                charEase = 200
                #charEase = self.rankKanji(c)
                npow = 0
                numCharsConsidered += 1
                for (e,r) in knownDb:
                    # has same kanji
                    if c in e:
                        if npow > -0.5: npow -= 0.1
                        # has same kanji at same pos
                        if len(e) > i and c == e[i]:
                            if npow > -1.0: npow -= 0.1
                            # has same kanji at same pos with similar reading
                            if i == 0 and read[0] == r[0] or i == len(expr)-1 and read[-1] == r[-1]:
                                npow -= 0.8
                charEase += self.rankKanji(c)
                wordEase += charEase * pow(2, npow)
        if not hasKanji:
            return len(expr)
        return wordEase
    
    def computeMorphemesScore(self, language):
        
        decksId = self.decksService.listDecksIdByLanguage(language)
        
        log("lemmeDao.getMorphemes() Start")
        allMorphemes = self.lemmeDao.getMorphemes(decksId)
        log("lemmeDao.getMorphemes() Stop")
        
        log("Rank Morphemes Start")
        rankDb = self.morphemeDao.getAllKnownSimpleMorphemes()
        modifiedMorphemes = list()
        for morpheme in allMorphemes:
            score = self.rankMorpheme(rankDb, morpheme.morphLemme.base, morpheme.morphLemme.read)
            if morpheme.score != score:
                morpheme.score = score
                morpheme.statusChanged = True #FIXME
                modifiedMorphemes.append(morpheme)
        log("Rank Morphemes Stop")
        
        self.morphemeDao.updateAll(modifiedMorphemes)
        
        return modifiedMorphemes
    
    def filterMorphLemmes(self, morphLemmesList):
        # Do nothing
        return morphLemmesList
        