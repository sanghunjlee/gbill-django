from typing import List, Dict, Optional, Union, Any

from ..exceptions import UnequalDistributionError, UnevenDistributionError

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
