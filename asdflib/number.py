from typing import Literal


def IsFloat(TestNumber : float | int) -> bool :
    try :
        float(TestNumber)
        return True
    except ValueError :
        return False

MoreNumberValues = Literal[
    'infinity',
    'nan',
    '-infinity'
]

def AutoFormat3f(Number : float) -> str :
    if IsFloat(Number) :
        if str(Number) == f'{self.__Number:.3f}' :
            return str(Number)
        else :
            return f'{self.__Number:.3f}...'
    else :
        return str(Number)

class Fraction(object) :
    def __init__(self, Numerator : float, Denominator : float) -> None :
        self.__Numerator = Numerator
        self.__Denominator = Denominator
        self.__Value = Numerator / Denominator
    
    def __add__(self, other) -> float :
        return self.__Value + float(other)
    
    def __sub__(self, other) -> float :
        return self.__Value - float(other)
    
    def __mul__(self, other) -> float :
        return (float(other) * self.__Numerator) / self.__Denominator

ExportNumberType = int | float | MoreNumberValues

class Number() :
    def __init__(self, ThisNumberValue : ExportNumberType | Fraction) -> None :
        self.__Number = ThisNumberValue
        self.__IsFloat = IsFloat(ThisNumberValue)
        self.__IsInteger = not self.__IsFloat
    
    def __int__(self) -> int :
        if self.__IsInteger :
            return int(self.__Number)
        else :
            raise ValueError(f'The number "{AutoFormat3f(self.__Number)}" is not an integer.')
    
    def __float__(self) -> float :
        if self.__IsFloat :
            return self.__Number
        else :
            return float(self.__Number)
    
    def __str__(self) -> str :
        return str(float(self.__Number))
    
    def __format__(self, format_spec: str) -> str:
        if format_spec == '__asdf_raw' :
            return str({
                'Number' : self.__Number,
                'IsFloat' : self.__IsFloat,
                'IsInteger' : self.__IsInteger
            })