import floppyforms as forms
#from django.core.exceptions import ValidationError
from djaloha.widgets import AlohaInput
from django.utils.encoding import smart_unicode

class DjalohaForm(forms.Form):
    def __init__(self, model_class, lookup, field_name, data=None, field_value=None, *args, **kwargs):
        super(DjalohaForm, self).__init__(data, *args, **kwargs)
        
        self._model_class = model_class
        self._lookup = lookup
        self._field_name = field_name
        
        model_name = "__".join(
            (model_class.__module__.split('.')[-2], model_class.__name__)
        )
        
        lookup_str = "__".join([k+"__"+unicode(v).strip('"\'') for (k,v) in lookup.items()])
        
        self._form_field = "__".join((
            "djaloha", model_name, lookup_str, field_name))
        
        self.fields[self._form_field] = forms.CharField(required=False, initial=field_value,
            widget = AlohaInput())
        
    #def __getattr__(self, name):
    #    if name == 'clean_'+self._form_field:
    #        return self.clean_field
    #        
    #def clean_field(self):
    #    return self.cleaned_data[self._form_field]
    
    def save(self):
        v = smart_unicode(self.cleaned_data[self._form_field])
        obj, _is_new = self._model_class.objects.get_or_create(**self._lookup)
        setattr(obj, self._field_name, v)
        obj.save()
    
    def as_is(self):
        return self._html_output(
            normal_row = u'%(field)s',
            error_row = u'%s',
            row_ender = '',
            help_text_html = u'',
            errors_on_separate_row = True)
        