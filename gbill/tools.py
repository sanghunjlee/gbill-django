from typing import Dict, List, Any
import math

def stof(str_val: str) -> float:
    if type(str_val) is str:
        _ = ''.join([_ for _ in str_val.replace(',', '') if _.isnumeric() or _ == '.'])
        if _.count('.') > 1:
            _ = _[:_.index('.')+1] + _[_.index('.'):].replace('.', '')
        return 0.0 if _.strip() == '' else float(_)
    return 0.0

def ftoc(float_val: float) -> str:
    return ('$' + str(round(float_val,2))).replace('$-', '-$')

def log10(val: float) -> float:
    return math.log10(val)

def rmv_dups(dups: List[Any]) -> List[Any]:
    no_dups = []
    if len(dups) > 0:
        for _ in dups:
            if _ not in no_dups:
                no_dups.append(_)
    return no_dups

def rpad(text: str, width: int) -> str:
    trimmed = text[:width]
    if len(trimmed) == width and width > 10:
        trimmed = trimmed[:-3] + "..."
    return trimmed.ljust(width)


def optimize(d: Dict[str, float]) -> Dict[str, float]:
    pass

if __name__ == '__main__':
    while True:
        _ = stof(input('str_val?'))
        print(_)
        if _ == '': break