from django.db import models
from django.urls import reverse

# Create your models here.
class Person(models.Model):
    """Field(s): name"""
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name
        
    def get_absolute_url(self):
        return reverse('person', kwargs={'pk': self.pk})

class Bill(models.Model):
    """desc, payee, amount"""
    desc = models.CharField(default="", max_length=200)
    payee = models.ForeignKey(Person, default=1, on_delete=models.PROTECT)
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return self.desc
    
    def get_absolute_url(self):
        return reverse('bill_detail', kwargs={'pk': self.pk})

    def get_persons_involved(self):
        return [_.person for _ in Item.objects.filter(bill=self.pk)]

    def get_items(self):
        return Item.objects.filter(bill=self.pk)


class Item(models.Model):
    """Fields:
    person = models.Person
    bill = models.Bill
    amount = DecimalField
    """
    person = models.ForeignKey(Person, default=1, on_delete=models.PROTECT)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return "{0} - {1} ({2}{3:.2f})".format(self.bill, self.person, "-$" if self.amount < 0 else "$", self.amount)