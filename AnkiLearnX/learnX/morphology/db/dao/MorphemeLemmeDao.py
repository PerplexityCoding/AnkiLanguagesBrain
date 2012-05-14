#-*- coding: utf-8 -*-

from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.MorphemeLemme import *
from learnX.morphology.db.dto.Morpheme import *

from learnX.utils.Log import *
from learnX.utils.Utils import *

class MorphemeLemmeDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def persistLemmes(self, lemmes):
        db = self.learnXdB.openDataBase()
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
                 lemme.maxInterval, lemme.score, lemme.changed)
            c.execute("Insert into MorphemeLemmes(id, pos, sub_pos, read, base, rank, max_interval, score, changed) "
                      "Values (?,?,?,?,?,?,?,?,?)", t)
        db.commit()
        c.close()
            
        return lemmes
    
    def updateLemmesScore(self, lemmes):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c = db.cursor()
        for lemme in lemmes:
            t = (lemme.score, lemme.id)
            c.execute("Update MorphemeLemmes set score = ? Where id = ?", t)
        db.commit()
        c.close()
            
        return lemmes
    
    def resetLemmesChanged(self):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        c.execute("Update MorphemeLemmes set changed = 0 where changed = 1")
        db.commit()
        c.close()
    
    def getAllLemmes(self):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c.execute("Select id, base, pos, sub_pos, read, rank, max_interval, score, changed From MorphemeLemmes")

        morphemes = list()
        for row in c:
            morphemes.append(MorphemeLemme(row[1], None, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[0]))
        c.close()
        
        return morphemes
    
    def getAllModifiedLemmes(self):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c.execute("Select id, base, pos, sub_pos, read, rank, max_interval, score, changed From MorphemeLemmes "
                  "Where changed = 1")

        morphemes = list()
        for row in c:
            morphemes.append(MorphemeLemme(row[1], None, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[0]))
        c.close()
        
        return morphemes
    
    def getKnownLemmesIntervalDB(self):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c.execute("Select base, read, max_interval From MorphemeLemmes where max_interval > 0")
        intervalDb = dict()
        for row in c:
           intervalDb[(row[0], row[1])] = row[2]
        c.close()
        return intervalDb
        
    def getLemmesFromNote(self, note):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (note.id,)
        c.execute("Select ml.id, base, pos, sub_pos, read, rank, max_interval, ml.score, ml.changed "
                  "From MorphemeLemmes ml, Morphemes m "
                  "Where ml.id = m.morph_lemme_id and m.note_id = ?", t)
        lemmes = list()
        for row in c:
           lemmes.append(MorphemeLemme(row[1], None, row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[0]))
        c.close()
        
        return lemmes
        
    def getLemmeIntervalFromNote(self, note):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (note.id,)
        c.execute("Select max_interval, score From MorphemeLemmes ml, Morphemes m "
                  "Where ml.id = m.morph_lemme_id and m.note_id = ?", t)
        lemmes = list()
        for row in c:
           lemmes.append((row[0], row[1]))
        c.close()
        
        return lemmes
    