from typing import Optional, Union, List, Dict, Any

from tools import ftoc
from exceptions import UnequalDistributionError, UnevenDistributionError


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

class Invoice():
    trans: List[Transaction]

    def __init__(self):
        self.trans = []

    def __getitem__(self, key: int) -> Transaction:
        return self.trans[key]

    def __setitem__(self, key: int, new_value: Transaction):
        self.trans[key] = new_value
    
    def get_payers(self):
        payers = []
        for t in self.trans:
            payers.append(t.payee)
            payers.extend(t.payer)
        return sorted([*set(payers)])

    def add_transaction(self, *args, **kwargs):
        try:
            if type(args[0]) is Transaction:
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
        cashflow = {k:round(v, 2) for k,v in cashflow.items()}
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
            cashflow[lpayee] = round(cashflow[lpayee] - payment, 2)
            cashflow[lpayer] = round(cashflow[lpayer] + payment, 2)
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

