from languagesBrain.morphology.db.LearnXdB import *
from languagesBrain.morphology.db.dto.Language import *

from languagesBrain.morphology.db.dto.Morpheme import *

from languagesBrain.utils.Log import *

import pickle

class LanguageDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def listLanguages(self):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        c.execute("select * from Languages")
        
        languages = []
        for row in c:
            language = Language(row[1], row[2], posOptions = row[3], id = row[0],
                total = row[4], known = row[5])
            if language.posOptions:
                language.posOptions = pickle.loads(str(language.posOptions))
            languages.append(language)
        
        c.close()
        
        return languages
    
    def insertLanguage(self, language):
        
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
    
    def updateLanguage(self, language):
        
        db = self.learnXdB.openDataBase()
        c = db.cursor()

        posOptions = language.posOptions
        if posOptions:
            posOptions = sqlite3.Binary(pickle.dumps(posOptions, 2))

        t = (language.nameId, language.posTaggerId, posOptions, language.totalMorphemes, language.knownMorphemes, language.id)
        c.execute("Update Languages Set name_id = ?, pos_tagger_id = ?, pos_tagger_options = ?, total_morphemes = ?, known_morphemes = ? "
                  "Where id = ?", t)
        db.commit()
        c.close()

    def findLanguageById(self, id):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (id,)
        c.execute("Select * From Languages Where id = ?", t)
        
        language = None
        for row in c:
            language = Language(row[1], row[2], posOptions = row[3], id = row[0],
                total = row[4], known = row[5])
            if language.posOptions:
                language.posOptions = pickle.loads(str(language.posOptions))
            
        db.commit()
        c.close()

        return language

    def findLanguageByCode(self, code):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (code,)
        c.execute("Select * From Languages Where name_id = ?", t)
        
        language = None
        for row in c:
            language = Language(row[1], row[2], posOptions = row[3], id = row[0],
                total = row[4], known = row[5])
            if language.posOptions:
                language.posOptions = pickle.loads(str(language.posOptions))
            
        db.commit()
        c.close()

        return language


