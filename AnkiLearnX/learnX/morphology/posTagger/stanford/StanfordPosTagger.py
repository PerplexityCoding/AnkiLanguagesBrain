
import os, subprocess, sys

from learnX.utils.Log import *
from learnX.morphology.db.dto.MorphemeLemme import *

class StanfordPosTagger():
    def __init__(self, options):
        self.stanfordTagger = "E:\\Project\\LearnX\\stanford-postagger-full-2012-03-09\\"
        self.jarPath = self.stanfordTagger + "stanford-postagger.jar"
        self.modelPath = self.stanfordTagger + "models\\"
        self.frenchModel = self.modelPath + "french.tagger"
        
        self.data = "E:\\Project\\Git\\AnkiLearnX\\AnkiLearnX\\learnX\\morphology\\posTagger\\stanford\\data\\french\\"
        
        self.dataIn = self.data + "french.in"
        self.dataOut = self.data + "french.out"
        
        self.options = options
        
        self.process = self.stanfordPosTagger()
        
    def stanfordPosTagger(self):
        
        posCmd = ["java", "-mx300m", "-cp", self.jarPath,
                  "edu.stanford.nlp.tagger.maxent.MaxentTagger",
                  "-model", self.frenchModel]
        
        p = subprocess.Popen(posCmd, bufsize=-1, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        # Pass verbose
        p.stdout.readline()
        p.stdout.readline()
        p.stdout.readline()
        p.stdout.readline()
        
        return p
        
    def posTag(self, expression):
        p = self.process
        expression = expression.encode( 'utf-8', 'ignore' )
        p.stdin.write(expression)
        p.stdin.write("\n")
        p.stdin.flush()

        result = p.stdout.readline()
        p.stdout.readline()

        return result
    
    def filterExpression(self, expression):
        expression = expression.replace('-', ' ')
        expression = expression.replace("'", "' ")
        return expression

    def getMorphemes(self, expression):
        
        expression = self.filterExpression(expression)
        
        taggedExpression = self.posTag(expression)
        
        morphemes = list()
        taggedTerms = taggedExpression.split(" ")
        for taggedTerm in taggedTerms:
            termArray = taggedTerm.split("_")
            if len(termArray) == 2:
                base = unicode(termArray[0].strip(), "utf-8")
                pos = unicode(termArray[1].strip(), "utf-8")
                if len(base) <= 2:
                    continue
                
                morphemes.append(MorphemeLemme(base, None, pos, pos, base))
            else:
                log("Error:" + taggedTerm)
        
        return morphemes

        

