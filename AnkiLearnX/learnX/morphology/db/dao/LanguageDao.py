from learnX.morphology.db.LearnXdB import *
from learnX.morphology.db.dto.Language import *

class LanguageDao:
    def __init__(self):
        self.learnXdB = LearnXdB.getInstance()
    
    def list(self):
        
        db = self.learnXdB.openDataBase()
        
        c = db.cursor()
        c.execute("select * from Languages")
        
        languages = []
        for row in c:
            languages.append(Language(row[1], row[2], row[0]))
        
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

    def findByCode(self, code):
        db = self.learnXdB.openDataBase()
        c = db.cursor()
        
        t = (code,)
        c.execute("Select * From Languages Where name_id = ?", t)
        
        language = None
        for row in c:
            language = Language(row[1], row[2], row[0])
            
        db.commit()
        c.close()

        return language
