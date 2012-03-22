#-*- coding: utf-8 -*-

from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.MecabMorpheme import *

from learnX.utils.Log import *

class MecabMorphemeDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def persist(self, morpheme):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (morpheme.pos, morpheme.subPos, morpheme.read, morpheme.base)
        c.execute("Select id From MecabMorphemes Where pos = ? and sub_pos = ? and read = ? and base = ?", t)
        
        morphemeId = c.fetchone()
        if morphemeId:
            morpheme.id = morphemeId[0]
            c.close()
            return morpheme
        else:
            c.close()
            
            c = db.cursor()
            c.execute("Insert into MecabMorphemes(pos, sub_pos, read, base) "
                  "Values (?,?,?,?)", t)
            db.commit()
            c.close()
            
            c = db.cursor()
            c.execute("Select count(*) From MecabMorphemes")
            for row in c:
                morpheme.id = row[0] - 1
            c.close()
            
            return morpheme
    
    def persistAll(self, morphemes):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        mecabMorphemesToInsert = list()
        for morpheme in morphemes:
            mecabMorpheme = morpheme.morph
            
            t = (mecabMorpheme.pos, mecabMorpheme.subPos, mecabMorpheme.read, mecabMorpheme.base,)
            c.execute("Select id From MecabMorphemes Where pos = ? and sub_pos = ? and read = ? and base = ?", t)            
            morphemeId = c.fetchone()
            if morphemeId:
                mecabMorpheme.id = morphemeId[0]
            else:
                mecabMorphemesToInsert.append(mecabMorpheme)
        c.close()
            
        c = db.cursor()
        for mecabMorpheme in mecabMorphemesToInsert:
            t = (mecabMorpheme.pos, mecabMorpheme.subPos, mecabMorpheme.read, mecabMorpheme.base)
            c.execute("Insert into MecabMorphemes(pos, sub_pos, read, base) "
                      "Values (?,?,?,?)", t)
        db.commit()
        c.close()
        
        c = db.cursor()
        for mecabMorpheme in mecabMorphemesToInsert:
            t = (mecabMorpheme.pos, mecabMorpheme.subPos, mecabMorpheme.read, mecabMorpheme.base)
            c.execute("Select id From MecabMorphemes Where pos = ? and sub_pos = ? and read = ? and base = ?", t)
            morphemeId = c.fetchone()
            if morphemeId:
                mecabMorpheme.id = morphemeId[0]
        c.close()
            
        return morphemes
        