from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Language import *

from learnX.morphology.db.dto.Morpheme import *

from learnX.utils.Log import *

import pickle

class LanguageDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def list(self):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        c.execute("select * from Languages")
        
        languages = []
        for row in c:
            language = Language(row[1], row[2], posOptions = row[3], id = row[0],
                total = row[4], learnt = row[5], known = row[6], mature = row[7])
            if language.posOptions:
                language.posOptions = pickle.loads(str(language.posOptions))
            languages.append(language)
        
        c.close()
        
        return languages
    
    def insert(self, language):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        posOptions = language.posOptions
        if posOptions:
            posOptions = sqlite3.Binary(pickle.dumps(posOptions, 2))
        
        t = (language.nameId, language.posTaggerId, posOptions)
        c.execute("Insert into Languages(name_id, pos_tagger_id, pos_tagger_options)"
                  "Values (?,?,?)", t)
        
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

        posOptions = language.posOptions
        if posOptions:
            posOptions = sqlite3.Binary(pickle.dumps(posOptions, 2))

        t = (language.nameId, language.posTaggerId, posOptions, language.totalMorphemes, language.learntMorphemes, language.knownMorphemes, language.matureMorphemes, language.id)
        c.execute("Update Languages Set name_id = ?, pos_tagger_id = ?, pos_tagger_options = ?, total_morphemes = ?, learnt_morphemes = ?,"
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
            language = Language(row[1], row[2], posOptions = row[3], id = row[0],
                total = row[4], learnt = row[5], known = row[6], mature = row[7])
            if language.posOptions:
                language.posOptions = pickle.loads(str(language.posOptions))
            
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
            language = Language(row[1], row[2], posOptions = row[3], id = row[0],
                total = row[4], learnt = row[5], known = row[6], mature = row[7])
            if language.posOptions:
                language.posOptions = pickle.loads(str(language.posOptions))
            
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
        
        sql = "Select count (distinct fm.morpheme_id) From NotesMorphemes fm, Notes f "
        sql += "Where f.id = fm.note_id " + decksIdsSql
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
        
        sql = "Select count (distinct fm.morpheme_id) From NotesMorphemes fm, Notes f, Morphemes m "
        sql += "Where f.id = fm.note_id and fm.morpheme_id = m.id and m.status = ? " + decksIdsSql
        
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

