from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Language import *

from learnX.morphology.db.dto.Morpheme import *

from learnX.utils.Log import *

class LanguageDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def list(self):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        c.execute("select * from Languages")
        
        languages = []
        for row in c:
            languages.append(Language(row[1], row[2], row[0], row[3], row[4], row[5], row[6]))
        
        c.close()
        
        return languages
    
    def insert(self, language):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (language.nameId, language.posType)
        c.execute("Insert into Languages(name_id, pos_type)"
                  "Values (?,?)", t)
        
        db.commit()
        c.close()
        
        c = db.cursor()
        
        u = (language.nameId,)
        c.execute("Select id From Languages Where name_id = ?", u)
        for row in c:
            language.id = row[0]
        c.close()
        
        return language
    
    def update(self, language):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()

        t = (language.nameId, language.posType, language.totalMorphemes, language.learntMorphemes, language.knownMorphemes, language.matureMorphemes, language.id)
        c.execute("Update Languages Set name_id = ?, pos_type = ?, total_morphemes = ?, learnt_morphemes = ?,"
                  "known_morphemes = ?, mature_morphemes = ? "
                  "Where id = ?", t)
        db.commit()
        c.close()

    def findById(self, id):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (id,)
        c.execute("Select * From Languages Where id = ?", t)
        
        language = None
        for row in c:
            language = Language(row[1], row[2], row[0], row[3], row[4], row[5], row[6])
            
        db.commit()
        c.close()

        return language

    def findByCode(self, code):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (code,)
        c.execute("Select * From Languages Where name_id = ?", t)
        
        language = None
        for row in c:
            language = Language(row[1], row[2], row[0], row[3], row[4], row[5], row[6])
            
        db.commit()
        c.close()

        return language

    def countMorphemes(self, language, deckIds):
        db = self.learnXdB.openDataBase()
        
        decksIdsSql = ""
        if deckIds != None and len(deckIds) > 0:
            decksIdsSql = " and ("
            i = 1
            for deckId in deckIds:
                decksIdsSql += " f.deck_id = ?"
                if i < len(deckIds):
                    decksIdsSql += " or "
                i += 1
            decksIdsSql += ")"
        
        sql = "Select count (distinct fm.morpheme_id) From FactsMorphemes fm, Facts f "
        sql += "Where f.id = fm.fact_id " + decksIdsSql
        log(sql)
        c = db.cursor()
        t = list()
        for deckId in deckIds:
            t.append(deckId)
        c.execute(sql, t)
        row = c.fetchone()
        language.totalMorphemes = 0
        if row:
            language.totalMorphemes = row[0]
        c.close
        
        sql = "Select count (distinct fm.morpheme_id) From FactsMorphemes fm, Facts f, Morphemes m "
        sql += "Where f.id = fm.fact_id and fm.morpheme_id = m.id and m.status = ? " + decksIdsSql
        
        c = db.cursor()
        t = list()
        t.append(Morpheme.STATUS_LEARNT)
        for deckId in deckIds:
            t.append(deckId)
        c.execute(sql, t)
        row = c.fetchone()
        language.learntMorphemes = 0
        if row:
            language.learntMorphemes = row[0]
        c.close
        
        c = db.cursor()
        t = list()
        t.append(Morpheme.STATUS_KNOWN)
        for deckId in deckIds:
            t.append(deckId)
        c.execute(sql, t)
        row = c.fetchone()
        language.knownMorphemes = 0
        if row:
            language.knownMorphemes = row[0]
        c.close
        
        c = db.cursor()
        t = list()
        t.append(Morpheme.STATUS_MATURE)
        for deckId in deckIds:
            t.append(deckId)
        c.execute(sql, t)
        row = c.fetchone()
        language.matureMorphemes = 0
        if row:
            language.matureMorphemes = row[0]
        c.close

