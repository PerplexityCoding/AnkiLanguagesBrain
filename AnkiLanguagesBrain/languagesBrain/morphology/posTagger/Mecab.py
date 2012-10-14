#-*- coding: utf-8 -*-
#
# Class taken from Morphman 2
#

import sys, os, platform, re, subprocess
from anki.utils import stripHTML, isWin, isMac

from learnX.utils.Utils import *
from learnX.morphology.db.dto.MorphemeLemme import *

class Mecab:

    mecabArgs = ['--node-format=%f[6]\t%m\t%f[0]\t%f[1]\t%f[7]\r', '--eos-format=\n',
            '--unk-format=%m\tUnknown\tUnknown\tUnknown\r']

    MECAB_NODE_PARTS = ['%f[6]','%m','%f[0]','%f[1]','%f[7]']
    MECAB_NODE_READING_INDEX = 4
    MECAB_NODE_LENGTH = len(MECAB_NODE_PARTS)
    
    DEFAULT_BLACKLIST = [u'記号', u'助詞', u'助動詞', u'UNKNOWN']
    
    def __init__(self, options):
        
        if sys.platform == "win32":
            self.si = subprocess.STARTUPINFO()
            try:
                self.si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            except:
                self.si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
        else:
            self.si = None
        
        self.options = options
        self.mecab = None
    
    def escapeText(self, text):
        # strip characters that trip up kakasi/mecab
        #text = text.replace("\n", " ")
        text = text.replace(u'\uff5e', "~")
        text = re.sub("<br( /)?>", "---newline---", text)
        text = stripHTML(text)
        text = text.replace("---newline---", "<br>")
        return text
    
    def mungeForPlatform(self, popen):
        if isWin:
            popen = [os.path.normpath(x) for x in popen]
            popen[0] += ".exe"
        elif not isMac:
            popen[0] += ".lin"
        return popen
    
    def fixReading(self, morpheme): # MecabProc -> Morpheme -> IO Morpheme
        if morpheme.pos in [u'動詞', u'助動詞', u'形容詞']: # verb, aux verb, i-adj
            n = self.interact(morpheme.base).split('\t')
            if len(n) == self.MECAB_NODE_LENGTH:
                morpheme.read = n[self.MECAB_NODE_READING_INDEX].strip()
        return morpheme
    
    def setup(self):
        base = "../../addons/japanese/support/"
        self.mecabCmd = self.mungeForPlatform(
            [base + "mecab"] + self.mecabArgs + [
                '-d', base, '-r', base + "mecabrc"])
        os.environ['DYLD_LIBRARY_PATH'] = base
        if not isWin:
            os.chmod(self.mecabCmd[0], 0755)

    def ensureOpen(self):
        if not self.mecab:
            self.setup()
            try:
                self.mecab = subprocess.Popen(
                    self.mecabCmd, bufsize=-1, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    startupinfo=self.si)
            except OSError:
                raise Exception("Please install mecab")

    def interact(self, expr):
        self.ensureOpen()
        expr = self.escapeText(expr)
        self.mecab.stdin.write(expr.encode("euc-jp", "ignore") + '\n')
        self.mecab.stdin.flush()
        return u'\r'.join([unicode(self.mecab.stdout.readline().rstrip('\r\n'), 'euc-jp') for l in expr.split('\n')])
    
    def filterPos(self, pos, deck, language):
        disablePosList = deck.posOptions["disabledPos"]
        for disablePos in disablePosList:
            if pos == disablePos:
                return None
        
        posFound = False
        availablePosList = language.posOptions["availablePos"]    
        for availablePos in availablePosList:
            if pos == availablePos:
                posFound = True
                break
        if posFound == False:
            return None
        
        return pos
    
        # MecabProc -> Str -> PosWhiteList? -> PosBlackList? -> IO [Morpheme]
    def posMorphemes(self, expression, deck, language):
        morphemes = [tuple(m.split('\t')) for m in self.interact(expression).split('\r')] # morphemes
        morphemes = [MorphemeLemme(*m) for m in morphemes if len(m) == self.MECAB_NODE_LENGTH] # filter garbage
        whiteList = language.posOptions["availablePos"]
        blackList = deck.posOptions["disabledPos"]
        morphemes = [m for m in morphemes if m.pos in whiteList]
        morphemes = [m for m in morphemes if m.pos not in blackList]
        morphemes = [self.fixReading(m) for m in morphemes]
        return morphemes
    