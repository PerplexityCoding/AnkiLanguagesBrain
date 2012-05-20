from hashlib import sha1

import time

class Timer:
    
    timer = dict()
    
    @staticmethod
    def start(i):
        if i not in Timer.timer:
            Timer.timer[i] = [0, 0]
        Timer.timer[i][1] = time.clock()

    @staticmethod
    def stop(i):
        Timer.timer[i][0] += time.clock() - Timer.timer[i][1]
    
    @staticmethod    
    def display(i):
        return "Timer (" + str(i) + ") : " + str(Timer.timer[i][0])

class Utils:
    
    @staticmethod
    def checksum(data):
        return sha1(data).hexdigest()
    
    @staticmethod
    def fieldChecksum(data):
        # 32 bit unsigned number from first 8 digits of sha1 hash
        return int(Utils.checksum(data.encode("utf-8"))[:8], 16)
    
    @staticmethod
    def ids2str(ids):
        """Given a list of integers, return a string '(int1,int2,...)'."""
        return "(%s)" % ",".join(str(i) for i in ids)
    
    @staticmethod
    def getList(dict):
        dictList = list()
        for key, value in dict.iteritems():
            dictList.append(value)
        return dictList
