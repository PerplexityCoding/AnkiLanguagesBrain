#-*- coding: utf-8 -*-

from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.MecabMorpheme import *
from learnX.morphology.db.dto.Morpheme import *

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
    
    def getMorphemes(self, decksId = None, expressions = None, status = None, status_changed = None, pos = None, subPos = None):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        sql = "Select base, pos, sub_pos, read, m.id, m.status, m.status_changed, mm.id, count(fm.fact_id) as c, m.score "
        sql += "From Morphemes m, FactsMorphemes fm, MecabMorphemes mm, Facts f "
        
        if decksId != None:
            sql += ", Decks d "
        
        sql += "Where mm.id = m.morph_impl_id and m.id = fm.morpheme_id and f.id = fm.fact_id "
        
        if decksId != None:
            sql += "and d.id = f.deck_id "
        
        t = list()
        if expressions != None:
            for expression in expressions:
                sql += " and (mm.base like ? or mm.read like ?) " 
                t.append("%" + expression + "%")
                t.append("%" + expression + "%")
        if status != None:
            sql += "and m.status = ? " 
            t.append(status)
        if status_changed != None:
            sql += "and m.status_changed = ? " 
            if status_changed:
                t.append(1)
            else:
                t.append(0)
        if pos != None:
            sql += "and pos = ? "
            t.append(pos)
        if subPos != None:
            sql += "and sub_pos = ? "
            t.append(subPos)
        if decksId != None and len(decksId) > 0:
            sql += "and ("
            i = 1
            for deckId in decksId:
                t.append(deckId)
                sql += "d.id = ?"
                if i < len(decksId):
                    sql += " or "
                i += 1
            sql += ")"
        
        sql += " group by m.id"
        
        log("getMorphemes SQL Start")
        log(sql)
        log(t)
        if len(t) > 0:
            c.execute(sql, t)
        else:
            c.execute(sql)
        log("getMorphemes SQL End")
        
        log("getMorphemes get Result Start")
        morphemes = []
        for row in c:
            mecabMorpheme = MecabMorpheme(row[0], None, row[1], row[2], row[3], row[4])
            morpheme = Morpheme(row[5], row[6], Morpheme.TYPE_MECAB, row[7], mecabMorpheme, row[9], row[4])
            morpheme.factsCount = row[8]
            morphemes.append(morpheme)
        log("getMorphemes get Result End")
        
        c.close()
        
        return morphemes
    
    def getAllPOS(self):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c.execute("Select distinct pos from MecabMorphemes")
        
        posList = []
        for row in c:
            posList.append(row[0])
        
        c.close()
            
        return posList
    
    def getAllSubPOS(self):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        c.execute("Select distinct sub_pos from MecabMorphemes")
        
        subPosList = []
        for row in c:
            subPosList.append(row[0])
        
        c.close()
            
        return subPosList
        