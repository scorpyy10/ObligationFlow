from django.db import models
from django.db import models
from django.forms import ModelForm
from datetime import datetime
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django import forms
from django.utils.timezone import now

# Create your models here.
class Document(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100,db_index=True,unique=True)
    file = models.FileField(upload_to='documents/',validators=[FileExtensionValidator( ['docx'] ) ])
    pdf_file = models.FileField(upload_to='pdfs/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING,blank=True, null=True)
    created_on = models.CharField(max_length=100,db_index=True,blank=True)

    def __str__(self):
        return self.name

class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'file','created_by', 'created_on']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'input'})
        self.fields['file'].widget.attrs.update({'class': 'file-input'})
        self.fields['file'].widget.clear_checkbox_label = 'clear'
        self.fields['file'].widget.initial_text = "Uploaded"
        self.fields['file'].widget.input_text = ""

    def clean(self):
        self.cleaned_data['created_by'] = self.request.user
        self.cleaned_data['created_on']= datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if(len(Document.objects.filter(name=self.cleaned_data['name'])) > 0):
            self.cleaned_data['custom_error'] = "Document with similar name is already present."

        if(len(self.cleaned_data['name']) < 3):
            self.cleaned_data['custom_error'] = "Document name should have more than 3 character."

class DocumentResponse(models.Model):
    name = models.CharField(max_length=100,db_index=True,unique=True, blank=False, null=False)
    extracted_terms = models.JSONField(blank=True, null=True, default=dict)
    extracted_clauses = models.JSONField(blank=True, null=True, default=dict)
    extracted_obligations = models.JSONField(blank=True, null=True, default=dict)
    extracted_contract_type = models.CharField(max_length=100,db_index=True,unique=False, blank=True, null=True)

    def __str__(self):
        return self.name

class ObligationMetadata(models.Model):
    obligation_id = models.IntegerField()
    document_id = models.IntegerField()
    metadata = models.JSONField(blank=True, null=True, default=dict)
    suggestions = models.JSONField(blank=True, null=True, default=dict)
  
    def __str__(self):
        return f"Doc:{self.document_id} & Obligation:{self.obligation_id}"
    

class RiskTrackingRecord(models.Model):
    TRACKING_FREQUENCY_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]

    RESPONSIBLE_PARTIES_CHOICES = [
        ('John Smith', 'John Smith'),
        ('Sarah Watson', 'Sarah Watson'),
        ('Abhinav Kohli', 'Abhinav Kohli'),
    ]

    STATUS_CHOICES = [
        ('init', 'Init'),
        ('ongoing', 'Ongoing'),
        ('executed', 'Executed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.AutoField(primary_key=True)
    obligation_id = models.IntegerField(default=3)
    document_id = models.IntegerField(default=86)
    tracking_title = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    review_frequency = models.CharField(max_length=20, choices=TRACKING_FREQUENCY_CHOICES)
    risk_mitigation_plan = models.TextField()
    responsible_parties = models.CharField(max_length=255, choices=RESPONSIBLE_PARTIES_CHOICES)  # Alternatively, use a ManyToManyField if you have a User model.
    ai_trigger_condition = models.TextField(default='No conditon provided as of now')
    email_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='init')
    is_cancel = models.BooleanField(default=False)


    def __str__(self):
        return self.tracking_title
    
    def save(self, *args, **kwargs):
        current_date = datetime.now().date()  # Get today's date (no time component)
        
        if self.is_cancel:
            self.status = 'cancelled'
        elif current_date < self.start_date:
            self.status = 'init'
        elif self.start_date <= current_date < self.end_date:
            self.status = 'ongoing'
        else:
            self.status = 'executed'
        
        super().save(*args, **kwargs)  # Call the "real" save() method
    
class RiskTrackingRecordForm(ModelForm):
    class Meta:
        model = RiskTrackingRecord
        fields = [
            'tracking_title',
            'start_date',
            'end_date',
            'review_frequency',
            'risk_mitigation_plan',
            'responsible_parties',
            'ai_trigger_condition',
            'email_notifications',
            'system_notifications'
        ]

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
        }

    def __init__(self, *args, **kwargs):
        # Capture request from kwargs, if available
        self.request = kwargs.pop('request', None)
        super(RiskTrackingRecordForm, self).__init__(*args, **kwargs)
        
        # Custom field widget attributes (add Bulma classes or other customizations as needed)
        self.fields['tracking_title'].widget.attrs.update({'class': 'input'})
        # self.fields['start_date'].widget.attrs.update({'class': 'input', 'type': 'date'})
        self.fields['review_frequency'].widget.attrs.update({'class': 'select'})
        self.fields['risk_mitigation_plan'].widget.attrs.update({'class': 'textarea', 'rows': 3})
        self.fields['responsible_parties'].widget.attrs.update({'class': 'select'})  # Adjust as needed
        self.fields['ai_trigger_condition'].widget.attrs.update({'class': 'textarea', 'rows': 3})

    def clean(self):
        # Call parent clean method to ensure default validation
        cleaned_data = super(RiskTrackingRecordForm, self).clean()
        
        # Set additional fields automatically
        if self.request:
            cleaned_data['created_by'] = self.request.user
        cleaned_data['created_on'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Custom validations
        if RiskTrackingRecord.objects.filter(tracking_title=cleaned_data.get('tracking_title')).exists():
            self.add_error('tracking_title', "A tracking record with a similar title already exists.")
        
        if len(cleaned_data.get('tracking_title', '')) < 3:
            self.add_error('tracking_title', "The tracking title should have more than 3 characters.")
        
        return cleaned_data
        
class Milestone(models.Model):
    # Foreign key to RiskTrackingRecord
    risk_tracking_record = models.ForeignKey(RiskTrackingRecord, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    due_date = models.DateField()

    def __str__(self):
        return self.title
    

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['risk_tracking_record', 'title', 'due_date']

    # Optionally, customize the queryset for the foreign key field
    risk_tracking_record = forms.ModelChoiceField(
        queryset=RiskTrackingRecord.objects.all(),
        empty_label="Select Risk Tracking Record"
    )

    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )