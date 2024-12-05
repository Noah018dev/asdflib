from typing import Optional
from retry import retry
import time, os


def SeedHelperHash(Number, Modulos):
    return (Number ^ (Number >> 16)) % Modulos

def Succession(Number : int) -> int :
    return Number + 1

@retry(OverflowError, tries=10)
def PseudoRandomSeed(Length = 32) -> int :
    HashedTime = SeedHelperHash(Succession(time.thread_time_ns()) * Succession(time.process_time_ns()) * Succession(time.time_ns()), time.time())

    
    try :
        while round(HashedTime * 100000000) < 10 ** Length :
            HashedTime = HashedTime * 1.251133333
    except OverflowError :
        raise OverflowError('Too large of a seed size. Only a length of 256 or less is stable.') from None

    
    return (round(HashedTime * 100000000)  + (round(time.time() * 100) % 2)) % (10 ** Length)

def LCGGenerator(Seed : int, a, c, m) :
    return (a * Seed + c) % m

def OffsetSeed(Seed : int, Offset : int) -> int :
    return SeedHelperHash(Seed, Offset) + SeedHelperHash(Offset, Seed) * Seed

class RandomGenerator() :
    def __init__(self, Seed : Optional[int] = None) :
        if Seed is None :
            try :
                Seed = PseudoRandomSeed(Length=256)
            except OverflowError :
                Seed = PseudoRandomSeed(Length=256)
        
        self.__Seed = Seed
        self.__Offset = 0
    
    def RandomInteger(self, Minium : int, Maxium : int) -> int :
        self.__Offset += 1
        a = 48271
        c = 0
        BaseNumber = LCGGenerator(
            OffsetSeed(self.__Seed, self.__Offset),
            a,
            c,
            (Maxium - Minium)
        )
        
        FinalNumber = Minium + (BaseNumber % (Maxium - Minium))
        
        return FinalNumber
    
    def RandomBytes(self, Count : int, Encoding = 'utf-8', Range = (0, 255)) -> bytes :
        Bytes = b''
        
        for _ in range(Count) :
            Bytes += bytes(chr(self.RandomInteger(Range[0], Range[1])), encoding=Encoding)
        
        return Bytes
    
    def Random(self, Level : int = 32) -> float :
        return self.RandomInteger(0, 10 ** Level) / 10 ** Level
    
    def MakeRandomFile(self, FileName : str, ByteSize : int, Encoding = 'utf-8', Range = (0, 255)):
        os.utime(FileName, None)
        
        with open(FileName, 'wb') as File :
            File.write(self.RandomBytes(ByteSize, Encoding, Range))