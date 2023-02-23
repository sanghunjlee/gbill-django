from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.forms import inlineformset_factory, formset_factory

from .models import Bill, Item, Person
from .forms import DetailForm, BillForm, ItemForm, IndexPersonForm, BaseItemFormSet, BaseInlineItemFormSet

ExisitngItemFormSet = inlineformset_factory(Bill, Item, form=ItemForm, formset=BaseInlineItemFormSet, extra=0)
ItemFormSet = inlineformset_factory(Bill, Item, form=ItemForm, formset=BaseItemFormSet, extra=0)
ItemCreateFormSet = inlineformset_factory(Bill, Item, form=ItemForm, formset=BaseInlineItemFormSet, extra=0)

# Create your views here.
class IndexView(generic.ListView):
    template_name = "gbill/index.html"
    context_object_name = "bill_list"

    def post(self, request, **kwargs):
        print('post')
        for k,v in request.POST.items():
            print(k, ': ', v)
        if "add_new_bill" in request.POST:
            persons = Person.objects.all()
            if len(persons) < 1:
                messages.error(request, 'You need at least 1 person in the group to create a bill.')
            else:
                return HttpResponseRedirect(reverse("gbill:bill_add"))
        elif "name" in request.POST:
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
        print('get')
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if "back" in request.POST:
            for deleted_item in Item.objects.filter(is_deleted=True):
                deleted_item.is_deleted = False
                deleted_item.save()
            return HttpResponseRedirect(reverse("gbill:index"))

        if "save" in request.POST:
            Item.objects.filter(bill=self.object, is_deleted=True).delete()

            form = self.form_class(request.POST)
            ex_formset = ExisitngItemFormSet(request.POST, prefix="ex-item")
            formset = ItemFormSet(request.POST)

            form_valid = form.is_valid()
            ex_formset_valid = ex_formset.is_valid()
            formset_valid = formset.is_valid()
            
            if form_valid and ex_formset_valid and formset_valid:
                bill_data = form.cleaned_data
                for k, v in bill_data.items():
                    if hasattr(self.object, k):
                        setattr(self.object, k, v)
                self.object.save()

                for ex_f in ex_formset:
                    ex_data = ex_f.cleaned_data
                    ex_item = ex_data.pop('id')
                    ex_data.pop('bill')
                    for k, v in ex_data.items():
                        if hasattr(ex_item, k):
                            setattr(ex_item, k, v)
                    ex_item.save(update_fields=['person', 'amount'])

                for f in formset:
                    data = f.cleaned_data
                    data['bill'] = self.object
                    data.pop('DELETE')
                    Item.objects.create(**data)

            return self.get(request, *args, **kwargs)

        if 'delete' in request.POST:
            self.object.delete()
            return HttpResponseRedirect(reverse('gbill:index'))

        if "add_new_item" in request.POST:
            ItemFormSet.extra += 1
        
        ex_formset = ExisitngItemFormSet(request.POST, prefix='ex-item')
        if ex_formset.is_valid():
            for data in ex_formset.cleaned_data:
                if data['DELETE'] is True:
                    data['id'].is_deleted = True
                    data['id'].save()
        formset = ItemFormSet(request.POST)
        if formset.is_valid():
            data = formset.cleaned_data
            pop_id = None
            for i in range(len(data)):
                if data[i]['DELETE'] is True:
                    pop_id = i
                else:
                    data[i]['DELETE'] = 'Delete'
            if pop_id is not None:
                data.pop(pop_id)
                ItemFormSet.extra -= 1
            formset = ItemFormSet(initial=data)
        else:
            formset = ItemFormSet()
        
        context = self.get_context_data(**kwargs)
        context['formset'] = formset
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(BillView, self).get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)
        context['existingFormset'] = ExisitngItemFormSet(
            prefix='ex-item',
            instance=self.object,
            queryset=Item.objects.filter(is_deleted=False)
        )
        context['formset'] = ItemFormSet()
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