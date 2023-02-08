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

def list_max(ll: List[List[Any]]) -> List[int]:
    nll = [0] * len(ll[0])
    for _ in ll:
        for i in range(len(_)):
            if len(_[i]) > nll[i]:
                nll[i] = len(_[i])
    return nll

def rpad(text: str, width: int) -> str:
    if len(text) > width:
        if width > 10:
            return (text[:width-3] + "...").ljust(width)
        else:
            return text[:width].ljust(width)
    else:
        return text.ljust(width)

def lpad(text: str, width: int) -> str:
    if len(text) > width:
        if width > 10:
            return (text[:width-3] + "...").rjust(width)
        else:
            return text[:width].rjust(width)
    else:
        return text.rjust(width)

def cpad(text: str, width: int, multiline: bool = False) -> str:
    args = (width, multiline)
    if '\n' in text:
        return cpad(text[:text.index('\n')], *args) + '\n' \
             + cpad(text[text.index('\n')+1:], *args)
    else:
        if len(text) > width:
            if multiline:
                return cpad(text[:width] + '\n' + text[width:], *args)
            if width > 10:
                return (text[:width-3] + "...").center(width)
            else:
                return text[:width].center(width)
        else:
            return text.center(width)

def print_array(
    arr: List[List[Any]], _format: str = 'r', padx: int = 1, pady: int = 0,
    header: str = '', footer: str = '',
    top: str = '', left: str = '', right: str = '', bottom: str = ''
) -> str:
    """Format array (n x m matrix) into a string.
    Parameter:
    * arr : a list of list of string where each list has the same dimension
    * _format : string of ['l', 'c', 'r', '|', '/'] where:\n
        'l', 'c', 'r' := left, center, right alignment
        '|' := line
        '/' := linebreak
    """
    # Check parameter condition:
    # (1) Check that arr is a matrix:
    if len(set([len(_) for _ in arr])) > 1:
        print('ArrayDimensionError')
        return ''
    printout = ''
    dim_r = len(arr)
    dim_c = len(arr[0])
    maxw = list_max(arr)
    width = sum(maxw) + (padx * 2 * dim_c) + (_format.count('|'))
    height = dim_r
    _format = _format.replace(' ', '')
    farr = _format.split('/')
    
    for i in range(dim_r):
        flist = list(farr[-1])
        if i < len(farr):
            flist = list(farr[i])
        for j in range(dim_c):
            if len(flist) > 0 and flist[0] == '|':
                printout += '|'
                flist.pop(0)
            if len(flist) > 0 and flist[0] in 'lcr':
                fi = lpad if flist[0] == 'r' else cpad if flist[0] == 'c' else rpad
                flist.pop(0)
            xspace = ' ' * padx
            printout += xspace + fi(arr[i][j], maxw[j]) + xspace
            if len(flist) > 0 and flist[0] == '|':
                printout += '|'
                flist.pop(0)
        yspace = '\n' * pady
        printout += '\n' + yspace

    # Adding top, bottom, left, right
    lwidth = 1 if len(left) <= height else len(left) // height
    lprint = cpad(cpad(left, lwidth * height), lwidth, True).split('\n')
    rwidth = 1 if len(right) <= height else len(right) // height
    rprint = cpad(cpad(right, rwidth * height), rwidth, True).split('\n')
    printout = '\n'.join([lprint[i] + printout.split('\n')[i] + rprint[i] for i in range(height)])
    tprint = ' ' * lwidth + cpad(top, width, True) + ' ' * rwidth
    bprint = ' ' * lwidth + cpad(bottom, width, True) + ' ' * rwidth
    printout = tprint + '\n' + printout + '\n' + bprint

    # Adding header & footer
    if header != '':
        header = cpad(header, width + lwidth + rwidth, True) + '\n\n'
    if footer != '':
        footer = '\n\n' + cpad(footer, width + lwidth + rwidth, True)

    printout = header + printout + footer

    return printout

    
def optimize(d: Dict[str, float]) -> Dict[str, float]:
    pass

if __name__ == '__main__':
    pass