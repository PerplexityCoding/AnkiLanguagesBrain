#-*- coding: utf-8 -*-
#
# Class taken from Morphman 2
#

import os, subprocess, sys
import unicodedata

from learnX.morphology.db.dto.MorphemeLemme import *

class Mecab:

    MECAB_NODE_PARTS = ['%f[6]','%m','%f[0]','%f[1]','%f[7]']
    MECAB_NODE_READING_INDEX = 4
    MECAB_NODE_LENGTH = len(MECAB_NODE_PARTS)
    
    DEFAULT_BLACKLIST = [u'記号', u'助詞', u'助動詞', u'UNKNOWN']
    
    def __init__(self, options):
        self.options = options
        self.process = self.mecab()
    
    def which(self, app): # PartialAppPath -> [FullAppPath]
        def isExe(path):
            return os.path.exists(path) and os.access(path, os.X_OK)
        apath, aname = os.path.split(app)
        if apath and isExe(app):  # full path was provided
            return [app]
        else:                       # search $PATH for matches
            ps = [os.path.join(p, aname) for p in os.environ['PATH'].split(os.pathsep)]
            return [p for p in ps if isExe(p)]
    
    # Creates an instance of mecab process
    def mecab(self, customPath=None): # Maybe Path -> IO MecabProc
        try: from japanese.reading import si
        except: si = None
    
        path = customPath or 'mecab'
        if not self.which('mecab'): # probably on windows and only has mecab via Anki
            # maybe we're running from anki?
            aPath = os.path.dirname(os.path.abspath(sys.argv[0]))
            amPath = os.path.join(aPath, 'mecab', 'bin', 'mecab.exe')
    
            # otherwise check default anki install loc
            if not self.which(amPath):
                if os.path.exists(r'C:\Program Files (x86)\Anki'):
                    aPath = r'C:\Program Files (x86)\Anki'
                else:
                    aPath = r'C:\Program Files\Anki'
            os.environ['PATH'] += ';%s\\mecab\\bin' % aPath
            os.environ['MECABRC'] = '%s\\mecab\\etc\\mecabrc' % aPath
        nodeFmt = '\t'.join(self.MECAB_NODE_PARTS) + '\r'
        mecabCmd = [path, '--node-format=%s' % nodeFmt, '--eos-format=\n', '--unk-format=%m\tUnknown\tUnknown\tUnknown\r']
        
        return subprocess.Popen(mecabCmd, bufsize=-1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=si)
    
    def interact(self, expr): # MecabProc -> Str -> IO Str
        p = self.process
        expr = expr.encode( 'euc-jp', 'ignore' )
        p.stdin.write( expr + '\n' )
        p.stdin.flush()
        return u'\r'.join( [ unicode( p.stdout.readline().rstrip( '\r\n' ), 'euc-jp' ) for l in expr.split('\n') ] )
    
    def fixReading(self, morpheme): # MecabProc -> Morpheme -> IO Morpheme
        if morpheme.pos in [u'動詞', u'助動詞', u'形容詞']: # verb, aux verb, i-adj
            n = self.interact(morpheme.base).split('\t')
            if len(n) == self.MECAB_NODE_LENGTH:
                morpheme.read = n[self.MECAB_NODE_READING_INDEX].strip()
        return morpheme
    
        # MecabProc -> Str -> PosWhiteList? -> PosBlackList? -> IO [Morpheme]
    def posMorphemes(self, expression):
        morphemes = [tuple(m.split('\t')) for m in self.interact(expression).split('\r')] # morphemes
        morphemes = [MorphemeLemme(*m) for m in morphemes if len(m) == self.MECAB_NODE_LENGTH] # filter garbage
        #if whiteList: morphemes = [m for m in morphemes if m.pos in whiteList]
        #if blackList: morphemes = [m for m in morphemes if m.pos not in blackList]
        morphemes = [self.fixReading(m) for m in morphemes]
        return morphemes
    