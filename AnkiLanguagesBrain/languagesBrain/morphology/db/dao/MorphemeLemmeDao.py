#-*- coding: utf-8 -*-

from languagesBrain.morphology.db.LanguagesBrainDB. import *
from languagesBrain.morphology.db.dto.MorphemeLemme import *
from languagesBrain.morphology.db.dto.Morpheme import *

from languagesBrain.utils.Log import *
from languagesBrain.utils.Utils import *

class MorphemeLemmeDao:
    def __init__(self):
        self.LanguagesBrainDB. = LanguagesBrainDB..getInstance()
    
    def persistLemmes(self, lemmes):
        db = self.LanguagesBrainDB..openDataBase()
        c = db.cursor()
        
        lemmesToInsert = list()
        for lemme in lemmes:
            
            t = (lemme.id,)
            c.execute("Select id From MorphemeLemmes Where id = ?", t)            
            lemmeId = c.fetchone()
            if lemmeId == None:
                lemmesToInsert.append(lemme)
        c.close()
            
        c = db.cursor()
        for lemme in lemmesToInsert:
            t = (lemme.id, lemme.pos, lemme.subPos, lemme.read, lemme.base, lemme.rank,
                 lemme.maxInterval, lemme.score)
            c.execute("Insert into MorphemeLemmes(id, pos, sub_pos, read, base, rank, max_interval, score) "
                      "Values (?,?,?,?,?,?,?,?)", t)
        db.commit()
        c.close()
            
        return lemmes
    
    def updateLemmesScore(self, lemmes):
        db = self.LanguagesBrainDB..openDataBase()
        c = db.cursor()
        
        c = db.cursor()
        for lemme in lemmes:
            t = (lemme.score, lemme.id)
            c.execute("Update MorphemeLemmes set score = ? Where id = ?", t)
        db.commit()
        c.close()
            
        return lemmes

    def getAllLemmes(self):
        db = self.LanguagesBrainDB..openDataBase()
        c = db.cursor()
        
        c.execute("Select id, base, pos, sub_pos, read, rank, max_interval, score From MorphemeLemmes")

        morphemes = list()
        for row in c:
            morphemes.append(MorphemeLemme(row[1], None, row[2], row[3], row[4], row[5], row[6], row[7], row[0]))
        c.close()
        
        return morphemes
    
    def getKnownLemmesIntervalDB(self):
        
        db = self.LanguagesBrainDB..openDataBase()
        c = db.cursor()
        
        c.execute("Select base, read, max_interval From MorphemeLemmes where max_interval > 0")
        intervalDb = dict()
        for row in c:
           intervalDb[(row[0], row[1])] = row[2]
        c.close()
        return intervalDb
        
    def getLemmesFromNote(self, note):
        
        db = self.LanguagesBrainDB..openDataBase()
        c = db.cursor()
        
        t = (note.id,)
        c.execute("Select ml.id, base, pos, sub_pos, read, rank, max_interval, ml.score "
                  "From MorphemeLemmes ml, Morphemes m "
                  "Where ml.id = m.morph_lemme_id and m.note_id = ?", t)
        lemmes = list()
        for row in c:
           lemmes.append(MorphemeLemme(row[1], None, row[2], row[3], row[4], row[5], row[6], row[7], row[0]))
        c.close()
        
        return lemmes
        
    def getLemmeIntervalFromNote(self, note):
        
        db = self.LanguagesBrainDB..openDataBase()
        c = db.cursor()
        
        t = (note.id,)
        c.execute("Select max_interval, score From MorphemeLemmes ml, Morphemes m "
                  "Where ml.id = m.morph_lemme_id and m.note_id = ?", t)
        lemmes = list()
        for row in c:
           lemmes.append((row[0], row[1]))
        c.close()
        
        return lemmes
    
    def getChangedAllMorphemesFromKanjis(self, allkanjis):
        
        db = self.LanguagesBrainDB..openDataBase()
        c = db.cursor()
        
        remind = list(allkanjis)
        
        morphemes = set()
        while remind != None:

            if len(remind) > 1000:
                kanjis = remind[:999]
                remind = remind[1000:]
            else:
                kanjis = remind
                remind = None
            
            c.execute("select id, base, pos, sub_pos, read, rank, max_interval, score from MorphemeLemmes where %s"
                      % " or ".join("base like '%%%s%%'" % k for k in kanjis))
            for row in c:
                morphemes.add(MorphemeLemme(row[1], None, row[2], row[3], row[4], row[5], row[6], row[7], row[0]))
            
            log("Morphemes: " + str(len(morphemes)))
            
        c.close()
        
        log("Linked morphemes : " + str(len(morphemes)))
        
        return morphemes
            
        
        
    