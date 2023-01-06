from typing import Dict, List, Any

def stof(str_val: str) -> float:
    if type(str_val) is str:
        _ = ''.join([_ for _ in str_val.replace(',', '') if _.isnumeric() or _ == '.'])
        if _.count('.') > 1:
            _ = _[:_.index('.')+1] + _[_.index('.'):].replace('.', '')
        return 0.0 if _.strip() == '' else float(_)
    return 0.0

def rmv_dups(dups: List[Any]) -> List[Any]:
    no_dups = []
    if len(dups) > 0:
        for _ in dups:
            if _ not in no_dups:
                no_dups.append(_)
    return no_dups


def optimize(d: Dict[str, float]) -> Dict[str, float]:
    pass

if __name__ == '__main__':
    while True:
        _ = stof(input('str_val?'))
        print(_)
        if _ == '': break