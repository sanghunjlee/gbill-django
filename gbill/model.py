from typing import Optional, Union, List, Dict, Any, Tuple
import json
from json import JSONDecodeError

from .tools import ftoc, log10
from .exceptions import UnequalDistributionError, UnevenDistributionError


class Transaction:
    descr: str
    payee: str
    payer: List[str]
    amount: float
    distribution: Dict[str, float]
    payment: float

    def __init__(
        self, 
        descr: str,
        payee: str, 
        payer: Union[List[str], str], 
        amount: float, 
        distribution: Optional[Dict[str, float]] = None
    ) -> None:
        if distribution:
            if sorted(distribution.keys()) != sorted(payer):
                raise UnequalDistributionError
            elif round(sum(distribution.values()), 2) != round(amount, 2):
                raise UnevenDistributionError
        self.descr = descr
        self.payee = payee
        self.payer = sorted(payer) if type(payer) is list else [payer]
        self.amount = amount
        self.distribution = distribution if distribution else {g:amount/len(self.payer) for g in self.payer}
        self.payment = sum([self.distribution[n] for n in self.payer if n != self.payee])

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __repr__(self) -> str:
        return f"{self.descr[:26]}\t{self.payee}\t{self.amount}"
    
    def data(self) -> Dict[str, Any]:
        return {
            'descr' : self.descr,
            'payee' : self.payee,
            'payer' : self.payer,
            'amount' : self.amount,
            'distribution' : self.distribution,
        }

class Invoice():
    trans: List[Transaction]

    def __init__(self):
        self.trans = []

    def __getitem__(self, key: int) -> Transaction:
        return self.trans[key]

    def __setitem__(self, key: int, new_value: Transaction):
        self.trans[key] = new_value
    
    def get_payers(self) -> List[str]:
        """Return sorted list of all people involved in the transactions
        * Includes payee even if payee does not need to pay someone else back
        """
        payers = []
        for t in self.trans:
            payers.append(t.payee)
            payers.extend(t.payer)
        return sorted([*set(payers)])

    def get_array(self) -> List[List[float]]:
        """Return n x m array, where:
         a_nm = amount of money in nth transaction for mth person
        * n -- index of the transaction
        * m -- index of the sorted list of all people = self.get_payers() 
        """
        arr = []
        ppl_list = self.get_payers()
        for t in self.trans:
            _d = t.distribution
            for missing_p in [_ for _ in ppl_list if _ not in _d.keys()]:
                _d[missing_p] = 0
            arr.append([_d[p] for p in ppl_list])
        return arr

    def get_matrix(self) -> List[List[float]]:
        ppl = self.get_payers()
        arr = self.get_array()
        mat = []
        for _ in ppl:
            mat.append([0.0] * len(ppl))
        for index, a in enumerate(arr):
            i = ppl.index(self.trans[index].payee)
            for j in range(len(ppl)):
                if i != j:
                    mat[i][j] += a[j]
                else:
                    mat[i][j] = 0

        # mat[i][j] = self.trans.
        # i := index of payee
        # j := index of payer
        return mat
    def list_matrix(self) -> List[List[str]]:
        mat = self.get_matrix()
        ppl = self.get_payers()
        ret_list = []
        ret_list.append(['', *ppl])
        for i, m in enumerate(mat):
            ret_list.append([ppl[i], *["{:.2f}".format(a) for a in m]])
        return ret_list


    def list_all(self) -> List[List[str]]:
        """Return a list of all transaction in formatted string.

        Parameter:
        * show_detail: If true, show description
        """
        _header = self.get_payers()
        _array = self.get_array()
        ret_list = []
        h = ['Payee', 'Desc', *_header, 'Subtotal']
        ret_list.append(h)
        
        m = len(_array[0])
        total = [0.0] * m
        for i, a in enumerate(_array):
            el = [
                self.trans[i].payee,
                self.trans[i].descr,
                *("{:.2f}".format(_) for _ in a), 
                "{:.2f}".format(sum(a))
            ]
            ret_list.append(el)
            for j, _ in enumerate(a):
                total[j] += _
        footer = [
            '',
            'Total',
            *["{:.2f}".format(_) for _ in total],
            "{:.2f}".format(sum(total))
        ]
        ret_list.append(footer)
        return ret_list

    def add_transaction(self, *args, **kwargs):
        try:
            if len(args) > 0 and type(args[0]) is Transaction:
                self.trans.append(args[0])
            else:
                self.trans.append(Transaction(*args, **kwargs))
        except Exception as e:
            print(e)    
    
    def pop(self, index: int) -> Transaction:
        return self.trans.pop(index)

    def remove(self, value: Transaction):
        self.trans.remove(value)

    def clear(self):
        self.trans.clear()

    def save(self, *args, **kwargs) -> str:
        if len(self.trans) == 0:
            return ''
        else:
            return json.dumps([t.data() for t in self.trans], *args, **kwargs)

    def load(self, data: str) -> bool:
        try:
            data_list = json.loads(data)
        except JSONDecodeError:
            print("load: JSONDecodeError")
            return False
        _backup = self.trans
        self.clear()
        try:
            for d in data_list:
                print(d)
                self.add_transaction(**d)
        except Exception as e:
            print(e)
            self.trans = _backup
            return False
        return True

    def invoice(self) -> List[Transaction]:
        inv = []
        cashflow = {}
        # creating a cashflow of each person involved
        for n, p, d in [(t.payee, t.payment, t.distribution) for t in self.trans]:
            if n not in cashflow.keys():
                cashflow[n] = 0
            cashflow[n] += p
            for k,v in [(item[0], item[1])  for item in d.items() if item[0] != n]:
                if k not in cashflow.keys():
                    cashflow[k] = 0
                cashflow[k] -= v
        #cashflow = {k:round(v, 2) for k,v in cashflow.items()}
        i = 0
        
        # min-max the cashflow as long as there is nonzero value in the cashflow vlaues
        while sum([abs(v) for v in cashflow.values()]) != 0:
            print(i, "::" , cashflow)
            most_neg = min(cashflow.values())
            most_pos = max(cashflow.values())
            lpayee = ""
            lpayer = ""
            for k,v in cashflow.items():
                if v == most_pos:
                    lpayee = k
                if v == most_neg:
                    lpayer = k
                if lpayee != "" and lpayer != "":
                    break
            payment = min(abs(most_neg), abs(most_pos))
            new_lpayee_value = cashflow[lpayee] - payment
            new_lpayer_value = cashflow[lpayer] + payment
            if payment == 0 or log10(payment) < -3:
                new_lpayee_value = 0
                new_lpayer_value = 0
            cashflow[lpayee] = new_lpayee_value
            cashflow[lpayer] = new_lpayer_value
            inv_desc = f'{lpayer} pays {ftoc(payment)} to {lpayee}.'
            inv.append(Transaction(inv_desc, lpayee, lpayer, payment))
            i += 1
        return inv


if __name__ == '__main__':
    m = Invoice()
    m.add_transaction('','A', ['A', 'B'], 20)
    m.add_transaction('', 'B', ['A', 'B', 'C', 'D'], 40)
    m.add_transaction('', 'C', ['A', 'B', 'D'], 30)
    m.add_transaction('', 'A', ['A', 'B', 'C', 'D', 'E'], 50)
    m.add_transaction('', 'A', ['A', 'C', 'D'], 30)
    inv = m.invoice()
    print(inv)
    print(m.get_payers())

