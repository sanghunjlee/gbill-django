from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.forms import inlineformset_factory

from .models import Bill, Item, Person
from .forms import DetailForm, BillForm, ItemForm, IndexPersonForm, BaseItemFormSet

ItemFormSet = inlineformset_factory(Bill, Item, form=ItemForm, formset=BaseItemFormSet, extra=0)
ItemCreateFormSet = inlineformset_factory(Bill, Item, form=ItemForm, formset=BaseItemFormSet, extra=0)

# Create your views here.
class IndexView(generic.ListView):
    template_name = "gbill/index.html"
    context_object_name = "bill_list"

    def post(self, request, **kwargs):
        for k,v in request.POST.items():
            print(k, ': ', v)
        
        if "name" in request.POST:
            print("name inputted")
            form = IndexPersonForm(request.POST)
            if form.is_valid():
                obj = Person()
                obj.name = form.cleaned_data['name']
                obj.save()

                self.object_list = self.get_queryset()
                context = self.get_context_data()

                return self.render_to_response(context)
        return self.get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["person_list"] = Person.objects.all()
        context['personForm'] = IndexPersonForm()
        return context

    def get_queryset(self):
        return Bill.objects.order_by("id")[:9]

class BillView(generic.DetailView):
    model = Bill
    object = "bill"
    form_class = DetailForm
    template_name = "gbill/detail.html"
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        if "add_new_item" in request.POST:
            Item(
                person=Person.objects.get(pk=1), 
                bill=Bill.objects.get(pk=kwargs['pk']), 
                amount=0
            ).save()
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)
        elif "Delete" in request.POST.values():
            for k, v in request.POST.items():
                if "Delete" in v:
                    id_name = k.replace("-DELETE","-id")
                    break
            fk = request.POST.get(id_name)
            Item.objects.get(pk=fk).delete()
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(BillView, self).get_context_data(**kwargs)
        bill = self.get_object()
        context['form'] = DetailForm(instance=bill)
        context['formset'] = ItemFormSet(instance=bill)
        return context

class BillCreateView(generic.FormView):
    model = Bill
    template_name = 'gbill/create.html'
    form_class = BillForm

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if "cancel" in request.POST:
            return HttpResponseRedirect(reverse('gbill:index'))
        if "save" in request.POST:
            form = BillForm(request.POST)
            formset = ItemCreateFormSet(request.POST)
            form_valid = form.is_valid()
            print(formset.data)
            formset_valid = formset.is_valid()
            print(form_valid, formset_valid)
            if form_valid and formset_valid:
                bill_data = form.cleaned_data
                bill = Bill.objects.create(**bill_data)
                for f in formset:
                    data = f.cleaned_data
                    data['bill'] = bill
                    data.pop('DELETE')
                    Item.objects.create(**data)
                return HttpResponseRedirect(reverse('gbill:index'))
        
        if "add_new_item" in request.POST:
            ItemCreateFormSet.extra += 1
        formset = ItemCreateFormSet(request.POST)
        if formset.is_valid():
            print(formset.cleaned_data)
            data = formset.cleaned_data
            pop_id = None
            for i in range(len(data)):
                if 'DELETE' in data[i]:
                    if data[i]['DELETE'] is True:
                        pop_id = i
                    else:
                        data[i]['DELETE'] = 'Delete'
            if pop_id is not None: 
                data.pop(pop_id)
                ItemCreateFormSet.extra -= 1
            print(data, ' && ', ItemCreateFormSet.extra)
            formset = ItemCreateFormSet(initial=data)
        else:
            formset = ItemCreateFormSet()
        context["formset"] = formset
        return self.render_to_response(context)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def delete_bill(request, pk):
    Bill.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse('gbill:index'))

def clear_bills(request):
    Bill.objects.all().delete()
    return HttpResponseRedirect(reverse('gbill:index'))

class PersonView(generic.DetailView):
    model = Person
    
class PersonAddView(generic.CreateView):
    model = Person
    
def delete_person(request, pk):
    try:
        Person.objects.get(pk=pk).delete()
    except:
        pass
    return HttpResponseRedirect(reverse('gbill:index'))

def clear_persons(request):
    Person.objects.filter(bill__payee__isnull = True, item__person__isnull = True).delete()
    return HttpResponseRedirect(reverse('gbill:index'))

""" 
class BillCreateView(generic.CreateView):
    model = Bill
    fields = ['desc', 'payee', 'amount']
    template_name = 'gbill/detail.html'
    form_class = DetailForm

    def post(self, request, *args, **kwargs):
        pass


class BillUpdateView(generic.UpdateView):
    model = Bill
    fields = ['desc', 'payee', 'amount']
    template_name = 'gbill/detail.html'
    form_class = DetailForm

class BillDeleteView(generic.DeleteView):
    model = Bill
    success_url = reverse_lazy('bill-list')
 """