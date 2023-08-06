# oppia/forms.py
import math
from django import forms
from django.conf import settings
from django.contrib.admin import widgets
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Layout, Fieldset, ButtonHolder, Submit, Div, HTML

from oppia.models import Schedule

class UploadCourseForm(forms.Form):
    course_file = forms.FileField(
                help_text=_('Max size %(size)d Mb') % {'size':int(math.floor(settings.OPPIA_MAX_UPLOAD_SIZE / 1024 / 1024))},
                required=True,
                error_messages={'required': _('Please select a file to upload')},)
    tags = forms.CharField(
                help_text=_("A comma separated list of tags to help classify your course"),
                required=True,
                error_messages={'required': _('Please enter at least one tag')},)
    is_draft = forms.BooleanField(
                help_text=_("Whether this course is only a draft"),
                required=False,)
    
    def __init__(self, *args, **kwargs):
        super(UploadCourseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('oppia_upload')
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
                'course_file',
                'tags',
                'is_draft',
                Div(
                   Submit('submit', _(u'Upload'), css_class='btn btn-default'),
                   css_class='col-lg-offset-2 col-lg-4',
                ),
            )  
    
    def clean(self):
        cleaned_data = super(UploadCourseForm, self).clean()
        file = cleaned_data.get("course_file")
        
        if file is not None and file._size > settings.OPPIA_MAX_UPLOAD_SIZE:  
            size = int(math.floor(settings.OPPIA_MAX_UPLOAD_SIZE / 1024 / 1024))
            raise forms.ValidationError(_("Your file is larger than the maximum allowed (%(size)d Mb). You may want to check your course for large includes, such as images etc.") % {'size':size, })
        
        if file is not None and file.content_type != 'application/zip' and file.content_type != 'application/x-zip-compressed':
            raise forms.ValidationError(_("You may only upload a zip file"))
        
        return cleaned_data
        
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ('title', 'default')
        widgets = {
            'title': forms.TextInput(attrs={'size':'60'}),     
        }
        
class ActivityScheduleForm(forms.Form):
    title = forms.CharField(widget=forms.HiddenInput())
    digest =  forms.CharField(widget=forms.HiddenInput())
    start_date = forms.DateTimeField(required=False)
    end_date = forms.DateTimeField(required=False)
    section = forms.CharField(widget=forms.HiddenInput())
    
    def clean(self):
        cleaned_data = super(ActivityScheduleForm, self).clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date is None and end_date is not None:
            raise forms.ValidationError("You must enter both a start and end date.")

        if start_date is not None and end_date is None:
            raise forms.ValidationError("You must enter both a start and end date.")
        
        if start_date > end_date:
            raise forms.ValidationError("Start date must be before the end date.")

        return cleaned_data
    
class CohortForm(forms.Form):
    description = forms.CharField(required=True)
    teachers = forms.CharField(widget=forms.Textarea(), required=False)
    students = forms.CharField(widget=forms.Textarea(),required=True)
    start_date = forms.DateTimeField(required=True)
    end_date = forms.DateTimeField(required=True)
    