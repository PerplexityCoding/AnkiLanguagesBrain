import os
import sqlite3

learnXPath = 'E:\Project\Workspaces\AnkiPlugins\AnkiLearnX'
#learnXPath = mw.pluginsFolder()

dbPath = os.path.join(learnXPath, 'learnX', 'db', 'db.learnX')
sqlPath = os.path.join(learnXPath, 'learnX', 'morphology', 'db', 'sql', 'tables.sql')

class LearnXdB:
    
    instance = None
    
    @staticmethod
    def getInstance():
       if LearnXdB.instance == None:
           LearnXdB.instance = LearnXdB()
       return LearnXdB.instance
       
    def __init__(self):
        self.conn = sqlite3.connect(dbPath)
        
    def createDataBase(self):
        self.conn = sqlite3.connect(dbPath)
        
        c = self.conn.cursor()
        sqlScript = open(sqlPath, "r")
        c.executescript(sqlScript.read())
        
        self.conn.commit()
        c.close

    def openDataBase(self):
        return self.conn

