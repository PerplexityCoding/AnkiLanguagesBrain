
import os, subprocess, sys, time, re

from learnX.utils.Log import *
from learnX.morphology.db.dto.MorphemeLemme import *

from learnX.utils.Globals import *

class StanfordPosTagger():
    def __init__(self, options):
        self.path = Globals.LearnXPath
        
        self.stanfordPath = self.path + "\\learnX\\morphology\\posTagger\\stanford\\"
        self.jarPath = self.stanfordPath + "\\lib\\stanford-postagger.jar"
        self.modelPath = self.stanfordPath + "\\data\\french\\model\\"
        self.frenchModel = self.modelPath + "french.tagger"
        
        self.options = options
        
        self.process = self.stanfordPosTagger()
        
    def stanfordPosTagger(self):
        
        posCmd = ["java", "-mx300m", "-cp", self.jarPath,
                  "edu.stanford.nlp.tagger.maxent.MaxentTagger",
                  "-model", self.frenchModel]
        
        p = subprocess.Popen(posCmd, bufsize=-1, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        # Flush verbose
        
        #time.sleep(2)
        #p.stdout.flush()
        p.stdout.readline()
        p.stdout.readline()
        p.stdout.readline()
        p.stdout.readline()
        p.stdout.flush()
        
        return p
        
    def posTag(self, expression):
        
        p = self.process
        
        log ((expression,))
        
        expression = expression.encode('latin-1', 'ignore')

        expression = self.filterExpression(expression)

        p.stdin.write(expression)
        p.stdin.write("\n")
        p.stdin.flush()
        
        #time.sleep(0.01)

        result = p.stdout.readline()
        result = result.decode("utf-8", "ignore")
        
        log((result,))
        
        p.stdout.flush()
  
        return result
    
    def stripHTML(self, s):
        s = re.sub("(?s)<style.*?>.*?</style>", "", s)
        s = re.sub("(?s)<script.*?>.*?</script>", "", s)
        s = re.sub("<.*?>", "", s)
        return s
    
    def filterExpression(self, expression):
        expression = expression.replace('-', ' ')
        expression = expression.replace("'", "' ")
        expression = expression.replace("<br>", "; ")
        expression = expression.replace("</br>", "; ")
        expression = expression.replace("<br />", "; ")
        expression = expression.replace(".", "; ")
        expression = expression.replace("?", "; ")
        expression = expression.replace("!", "; ")
        expression = expression.replace("\n", "; ")
        expression = expression.replace("/", "; ")
        expression = expression.replace("[", "; ")
        expression = expression.replace("]", "; ")
        expression = expression.replace("(", "; ")
        expression = expression.replace(")", "; ")
        expression = self.stripHTML(expression)
        expression = expression.replace("<", "; ")
        expression = expression.replace(">", "; ")
        expression = expression.replace("</", "; ")
        expression = expression.replace("/>", "; ")
        # remove html !!!!
        
        return expression

    def filterMorpheme(self, morpheme):
        if morpheme.find("www") >= 0:
            return None
        return morpheme

    def posMorphemes(self, expression):
        
        if len(expression) == 0:
            return list()
        
        taggedExpression = self.posTag(expression)
        
        morphemes = list()
        taggedTerms = taggedExpression.split(" ")
        for taggedTerm in taggedTerms:
            #log(taggedTerm)
            termArray = taggedTerm.split("_")
            if len(termArray) == 2:
                base = self.filterMorpheme(termArray[0].strip())
                if base == None:
                    continue
                if len(base) <= 2:
                    continue
                
                pos = termArray[1].strip()
                
                morphemes.append(MorphemeLemme(base, None, pos, "", ""))
            else:
                log("Error:" + taggedTerm)
        
        return morphemes
