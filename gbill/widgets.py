from django.forms import widgets

class ButtonWidget(widgets.Input):
    input_type = "submit"

class ListTextWidget(widgets.Select):
    def __init__(self, list_model, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._model = list_model

    def render(self, name, value, attrs=None, renderer=None):
        html = super(ListTextWidget, self).render(name, value, attrs=attrs, renderer=renderer)
        print(self.attrs)
        attrs.update({
            'name': attrs.get('name', name) + '-text',
            'class': self.attrs.get('class', name) + '-text'
        })
        choice = self.choices.queryset.get(pk=value)
        html += widgets.TextInput().render(name, '', attrs=attrs)
        return html
