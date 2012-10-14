import os
import sqlite3

from languagesBrain.utils.Log import *
from languagesBrain.utils.Globals import *

from aqt import mw

class LanguagesBrainDB:
    
    instance = None

    @staticmethod
    def getInstance():
       if LanguagesBraindB.instance == None:
           LanguagesBraindB.instance = LanguagesBraindB()
       return LanguagesBraindB.instance
       
    def __init__(self):

        lbPathDb = mw.pm.profileFolder()
        lbPath = Globals.LanguagesBrainPath
        
        self.dbPath = os.path.join(lbPathDb, 'collection.morphemes.db')
        self.sqlPath = os.path.join(lbPath, 'learnX', 'morphology', 'db', 'sql', 'tables.sql')
        if os.path.exists(self.dbPath) == False:
            self.createDataBase()
        
        self.conn = sqlite3.connect(self.dbPath)
        
    def createDataBase(self):
        self.conn = sqlite3.connect(self.dbPath)
        
        c = self.conn.cursor()
        sqlScript = open(self.sqlPath, "r")
        c.executescript(sqlScript.read())
        
        self.conn.commit()
        c.close

    def openDataBase(self):
        return self.conn

