#-*- coding: utf-8 -*-

import os, subprocess, sys, time
import unicodedata, codecs

from learnX.utils.Log import *
from learnX.utils.Globals import *

class CstLemmatizer:
    def __init__(self):
        self.path = Globals.LearnXPath
        self.lemmatizer = self.path + "\\learnX\\morphology\\lemmatizer\\cst\\"
        self.bin = self.lemmatizer + "bin\\cstlemma.exe"
        
        self.data = self.lemmatizer + "data\\french\\"
        self.lexique = self.data + "corpus\\OLDlexiqueSimplePos.txt"
        
        self.dict = self.data + "french.dict"
        self.flex = self.data + "french.flex"
        
        self.dataIn = self.data + "french.in"
        self.dataOut = self.data + "french.out"
        
    def cst(self):
        
        cstCmd = [self.bin, "-L",
            "-f", self.flex,
            "-d", self.dict,
            "-u-",
            "-U-",
            "-b$w",
            "-B$w",
            "-c$w/$t/$b1[[$b?]~1$B]\n",
            "-o", self.dataOut,
            "-i", self.dataIn
        ]
        
        p = subprocess.Popen(cstCmd, bufsize=-1, stdin=None, stdout=None,
            stderr=None, shell=True, startupinfo=None)
        
    def makeDict(self):
        
        cstCmd = [self.bin, "-D", "-cFBT", "-i" + self.lexique, "-o" + self.dict]
        subprocess.Popen(cstCmd)
        
    def makeFlexRules(self):
        
        cstCmd = [self.bin, "-F", "-cFBT", "-i" + self.lexique, "-o" + self.flex]
        subprocess.Popen(cstCmd)
        
    def lemmatizeMorphemes(self, morphemes):
        
        log("Get Big Expr from morphemes")
        #exp = ""
        #for morpheme in morphemes:
        #    exp += morpheme.base + "/" + morpheme.pos + " "
        
        exp = " ".join(morpheme.base + "/" + morpheme.pos for morpheme in morphemes)
        
        log("Lemmatize")
        lemmes = self.lemmatize(exp)
        
        log("Nb lemmes = " + str(len(lemmes)))
        
        i = 0
        for lemme in lemmes:
            lemmeArray = lemme.split("/")
            if len(lemmeArray) == 3:
                morpheme = morphemes[i]
                if morpheme.base != lemmeArray[0] or morpheme.pos != lemmeArray[1]:
                    log("!! Error !! morpheme.base !=")
                    continue
                morpheme.base = lemmeArray[2]
            else:
                log("!! Error !! len(lemmeArray) != 3")
                
            i += 1
        
        return morphemes
        
    def lemmatize(self, expr):

        #log((expr,))
        log("Lemmatize exp:" + str(len(expr)))

        log ("Encode in Latin-1")
        expr = expr.encode('latin-1', 'ignore')
        
        log("Write to In File")
        filein = open(self.dataIn, "wb")
        filein.write(expr)
        filein.close()
        
        #time.sleep(5)
        
        fileout = open(self.dataOut, "wb")
        fileout.write("")
        fileout.close()
        
        cstCmd = [self.bin, "-L",
            "-f", self.flex,
            "-d", self.dict,
            "-u-",
            "-U-",
            "-e1",
            "-b$w",
            "-B$w",
            "-c$w/$t/$b1[[$b?]~1$B]\n",
            "-o", self.dataOut,
            "-i", self.dataIn
        ]
        
        p = subprocess.Popen(cstCmd, bufsize=-1, stdin=None, stdout=None,
            stderr=None, startupinfo=None)

        fileout = open(self.dataOut, "r")
        maxTry = 0
        while fileout.readline() == "" and maxTry < 30:
            log("sleep")
            time.sleep(2)
            maxTry += 1
        
        fileout = open(self.dataOut, "r")
        result = list()
        
        line = fileout.readline()
        while len(line) > 0:
            #log((line,))
            result.append(line.decode("latin-1", "ignore"))
            line = fileout.readline()  

        return result
        
#cst = CstLemmatizer()
#cst.makeDict()
#cst.makeFlexRules()
#print(cst.lemmatize("prends/V écouté/V close/N mangés/V prise/A ahhum/I prie/V prisent/V fait/V est/V"))
#print(cst.lemmatize("prends/V écouté/V close/N mangés/V prise/A ahhum/I prie/V prisent/V fait/V est/V"))
#print(cst.lemmatize("prends/V écouté/V close/N mangés/V prise/A ahhum/I prie/V prisent/V fait/V est/V"))

#cst.lemmatize()

#time.sleep(50)

