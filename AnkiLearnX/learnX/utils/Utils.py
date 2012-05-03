from hashlib import sha1

class Utils:
    
    @staticmethod
    def checksum(data):
        return sha1(data).hexdigest()
    
    @staticmethod
    def fieldChecksum(data):
        # 32 bit unsigned number from first 8 digits of sha1 hash
        return int(Utils.checksum(data.encode("utf-8"))[:8], 16)