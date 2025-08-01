from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
# import pythoncom
from django.shortcuts import get_object_or_404, render
from docx2pdf import convert
import pandas as pd
import os
import sys
import subprocess
from django.shortcuts import render
from .models import Document
# from .forms import DocumentForm
from .tasks import extract_data_from_contract
# from .utils import get_extension
from .models import *
from .tasks import *
from .helper_functions import *




# def get_extension(filename):
#     return os.path.splitext(filename)[1].lower()
# Create your views here.
def index(request):
    context ={}
    document_count = Document.objects.all().count()
    context['document_count'] = document_count
    context['document'] = Document.objects.all()
    form = DocumentForm(request.POST or None)
    # context['document'] = page_wise_documents
    context['form']= form
    # context['document'] = page_wise_documents
    # return HttpResponse("Hello, world. You're at the index page.")
    return render(request, "dashboard.html", context)

# @login_required
def document_table_list(request):
    # paginator = Paginator(Document.objects.all(),10)
    # page_number = request.GET.get('page')
    # page_wise_documents = paginator.get_page(page_number)
    form = DocumentForm(request.POST or None)
    context ={}
    context['document'] = Document.objects.all()
    # context['document'] = page_wise_documents
    context['form']= form
    return render(request, "document_table_list.html",context)

def document_obligation_table_list(request,id):
    context = {}
    data = Document.objects.filter(id=id).first()
    # response = SingleApiCall.objects.filter(name=data.name)

    context['selected_document'] = data
    # context['response'] = response
    return render(request, "obligation_table_list.html",context)



def convert_docx_to_pdf_cross_platform(docx_path, pdf_path):
    if sys.platform == "win32":
        # Windows conversion using docx2pdf
        pass
        # try:
        #     import pythoncom
        #     from docx2pdf import convert

        #     pythoncom.CoInitialize()
        #     convert(docx_path, pdf_path)
        # finally:
        #     pythoncom.CoUninitialize()
    else:
        # macOS/Linux conversion using LibreOffice
        result = subprocess.run([
            "soffice", "--headless", "--convert-to", "pdf", docx_path,
            "--outdir", os.path.dirname(pdf_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            raise Exception(f"LibreOffice conversion failed: {result.stderr.decode()}")

def create_document_from_list_view(request):
    context = {}
    context['document'] = Document.objects.all()
    form = DocumentForm(request.POST or None, request.FILES)
    form.request = request

    if form.is_valid():
        if "custom_error" in form.cleaned_data and form.cleaned_data['custom_error'] != "":
            context['document_err'] = form.cleaned_data['custom_error']
        else:
            document = form.save()
            file_name = form.cleaned_data['file'].name
            file_type = get_extension(file_name)
            name = form.cleaned_data['name']
            document = Document.objects.get(name=name)
            document_id = document.id

            # Convert DOCX to PDF if needed
            if file_name.endswith('.docx') and not document.pdf_file:
                docx_path = document.file.path
                pdf_path = docx_path.replace('.docx', '.pdf')

                try:
                    convert_docx_to_pdf_cross_platform(docx_path, pdf_path)
                    with open(pdf_path, 'rb') as pdf_file:
                        document.pdf_file.save(os.path.basename(pdf_path), pdf_file, save=True)
                except Exception as e:
                    context['document_err'] = f"PDF conversion failed: {e}"

            data = {
                'document_id': document_id,
                'name': name,
                'file_type': file_type,
            }
            extract_data_from_contract.delay(data)

    context['form'] = form
    return render(request, "document_table_list.html", context)

def display_extracted_result(request, id):
    context = {}
    data = Document.objects.filter(id=id).first()
    document = get_object_or_404(Document, id=id)
    # response = SingleApiCall.objects.filter(name=data.name)

    # context['selected_document'] = data
    # context['response'] = response
    # context = {
    #     'selected_document': document,
    #     'pdf_url': document.pdf_file.url if document.pdf_file else None,
    # }
    response = DocumentResponse.objects.filter(name=data.name).first()

    processed_obligations = []
    total_risk = 0
    valid_risk_count = 0
    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0

    if response:
        for obligation in response.extracted_obligations['obligations']:
            if obligation:  # Ensure the obligation dictionary is not empty
                last_key, last_value = list(obligation.items())[-1]  # Get the last key-value pair
                risk_percentage = int(obligation['risk_percentage']) if (isinstance(obligation['risk_percentage'], (str, int)) and obligation['risk_percentage'] != 'NA') else 0
                print(last_key, last_key)
                print("actual: ",obligation['risk_percentage'])
                print("processed: ",int(obligation['risk_percentage']) if (isinstance(obligation['risk_percentage'], str) or isinstance(obligation['risk_percentage'], int)) and obligation['risk_percentage'] != 'NA' else 0)
                processed_obligations.append({
                    'obligation_category': obligation['obligation_category'],
                    'last_key': last_key,
                    'last_value': last_value,
                    'risk_percentage': int(obligation['risk_percentage']) if (isinstance(obligation['risk_percentage'], str) or isinstance(obligation['risk_percentage'], int)) and obligation['risk_percentage'] != 'NA' else 0,
                    'reason':obligation['reason'],
                    'id':obligation['id'],
                    'risk_value':obligation['risk_value'],
                    'responsible_party':obligation['responsible_party'],
                    'due_date':obligation['due_date'],
                    'penalty':obligation['penalty'],
                })

                 # Calculate total risk percentage for averaging
                if risk_percentage > 0:
                    total_risk += risk_percentage
                    valid_risk_count += 1

                if risk_percentage > 70:
                    high_risk_count += 1
                elif risk_percentage > 30:
                    medium_risk_count += 1
                else:
                    low_risk_count += 1

    obligations_sorted = sorted(processed_obligations, key=lambda x: x['risk_percentage'], reverse=True)
    # context['selected_document'] = data
    # Calculate average risk percentage
    print("total risk", total_risk)
    
    avg_risk_percentage = total_risk / valid_risk_count if valid_risk_count > 0 else 0
    print("low risk", low_risk_count)

    if response:
        context['terms'] = response.extracted_terms['terms']
        context['clauses'] = response.extracted_clauses['clauses']
        context['contract_type'] = response.extracted_contract_type
        context['term_length']=len(response.extracted_terms['terms']),
        context['clause_length']=len(response.extracted_clauses['clauses']),
    context['obligations'] = obligations_sorted
    context['selected_document'] = document
    context['pdf_url'] = document.pdf_file.url if document.pdf_file else None
    context['document_id'] = id
    context['avg_risk_percentage']= avg_risk_percentage,

    context['obligation_length']=len(processed_obligations),
    context['high_risk_count']=high_risk_count,
    context['medium_risk_count']=medium_risk_count,
    context['low_risk_count']=low_risk_count
    # context['obligations'] = response.extracted_obligations['obligations']
    # return render(request, "display_extracted_result.html",context)
    # return render(request, "my-template.html",context)
    
    return render(request, "single_page_contract_view.html",context)

def obligation_task(request, doc_id, obligation_id):
    context = {}
    context['obligation_id'] = obligation_id
    context['document_id'] = doc_id
    match_obligation = None
    document = Document.objects.filter(id=doc_id).first()
    document_response = DocumentResponse.objects.filter(name=document.name).first()
    for obligation in document_response.extracted_obligations.get('obligations', []):
            if obligation and obligation['id'] == obligation_id:
                match_obligation = obligation
                break
    context['obligation'] = match_obligation
    context['risk_percentage'] = int(match_obligation['risk_percentage']) if (isinstance(match_obligation['risk_percentage'], str) or isinstance(match_obligation['risk_percentage'], int)) and match_obligation['risk_percentage'] != 'NA' else 0
    last_key, last_value = list(match_obligation.items())[-1] 
    context['obligation_key'] = last_key
    context['obligation_value'] = last_value
    obligation_metadata = ObligationMetadata.objects.filter(document_id=doc_id, obligation_id=obligation_id).first()
    
    if obligation_metadata:
        if obligation_metadata.suggestions:
            suggestions = obligation_metadata.suggestions['suggestions']
            risk_neutralized_obligations = obligation_metadata.suggestions['risk_neutralized_obligations']
            
            if suggestions and suggestions != 'NA' and suggestions != []:
                context['suggestions'] = suggestions
                print("Maaiz Sug",suggestions)

            if risk_neutralized_obligations and risk_neutralized_obligations != 'NA' and risk_neutralized_obligations != []:
                context['risk_neutralized_obligations'] = risk_neutralized_obligations
                print("Maaiz risk_neutralized_obligations",risk_neutralized_obligations)
        else:
            context['suggestions'] = 'NA'       
            context['risk_neutralized_obligations'] = 'NA'       
        
    else:
        data = {
            'document_id':doc_id, 
            'obligation_id': obligation_id, 
        }
        extract_risk_neutralization_suggestion_from_obligation.delay(data)

    # if request.method == 'POST':
    #     form = RiskTrackingRecordForm(request.POST, request=request)
    #     if form.is_valid():
    #         # Create an instance but don't commit yet
    #         risk_record = form.save(commit=False)

    #         # Assign the additional data to the instance
    #         risk_record.document_id = doc_id
    #         risk_record.obligation_id = obligation_id
            
    #         # current_date = datetime.now().date()
    #         # start_date = risk_record.start_date
    #         # end_date = risk_record.end_date

          

    #         # status = 'init'
    #         # if current_date < start_date:
    #         #     status = 'init'
    #         # elif current_date >= start_date and current_date < end_date:
    #         #     status = 'ongoing'
    #         # elif current_date >= end_date:
    #         #     status = 'executed'
    #         # else:
    #         #     status = 'cancelled'

    #         # risk_record.status = status

    #         # Save the instance to the database
    #         risk_record.save()
    #         # form.save()
    #         # return HttpResponse('success_page')  # Redirect as needed
    # else:
    #     form = RiskTrackingRecordForm()
    risk_form = RiskTrackingRecordForm()
    milestone_form = MilestoneForm()
    if request.method == 'POST':
        # Handling RiskTrackingRecordForm
        if 'form' in request.POST:
            risk_form = RiskTrackingRecordForm(request.POST)
            if risk_form.is_valid():
                risk_record = risk_form.save(commit=False)

                # Assign the additional data to the instance
                risk_record.document_id = doc_id
                risk_record.obligation_id = obligation_id
                risk_record.save()
                # return redirect('success_page')  # Redirect after saving the risk form
        
        # Handling MilestoneForm
        elif 'form1' in request.POST:
            milestone_form = MilestoneForm(request.POST)
            if milestone_form.is_valid():
                milestone_form.save()
                print("Milestone Form")
                # return redirect('success_page')  # Redirect after saving the milestone form
    else:
        # Initialize forms for GET request (to render the forms)
        risk_form = RiskTrackingRecordForm()
        milestone_form = MilestoneForm()
        print("milestone_form")

    # return render(request, 'obligation_task.html', {
    #     'form': risk_form,
    #     'form1': milestone_form,
    # })

    context['form'] = risk_form
    context['form1'] = milestone_form

    return render(request, "obligation_task.html",context)


def create_risk_tracking(request):
    if request.method == 'POST':
        form = RiskTrackingRecordForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return redirect('success_page')  # Redirect as needed
    else:
        form = RiskTrackingRecordForm()

    return render(request, 'obligation_task.html', {'form': form})

def create_milestone(request):
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('milestone_list')  # Redirect to a milestone list or another page
    else:
        form = MilestoneForm()

    return render(request, 'create_milestone.html', {'form': form})

def task_dashboard(request):

    tasks = RiskTrackingRecord.objects.all()
    milestones = Milestone.objects.all()
    milestone_list_task = []
    for task in tasks:
        milestones = Milestone.objects.filter(risk_tracking_record=task)
        milestone_list_task.append(milestones)

    context = {
        'tasks': tasks,
        'milestones': milestone_list_task,
        'today': datetime.today().date()
    }
    return render(request, 'task_dashboard.html', context)

def export_data_to_excel(request):
    
    doc_data = []
    doc_response_data = []
    obligation_data = []

    doc_objs = Document.objects.all()
    for doc_obj in doc_objs:
        doc_data.append({
            "id":doc_obj.id,
            "name":doc_obj.name,
            "file":doc_obj.file,
            "pdf_file":doc_obj.pdf_file,
            "created_by":doc_obj.created_by,
            "created_on":doc_obj.created_on,
        })
    pd.DataFrame(doc_data).to_excel('doc_output.xlsx')

    doc_response_objs = DocumentResponse.objects.all()
    for doc_response_obj in doc_response_objs:
        doc_response_data.append({
            "name":doc_response_obj.name,
            "extracted_terms":doc_response_obj.extracted_terms,
            "extracted_clauses":doc_response_obj.extracted_clauses,
            "extracted_obligations":doc_response_obj.extracted_obligations,
            "extracted_contract_type":doc_response_obj.extracted_contract_type,
        })
    pd.DataFrame(doc_response_data).to_excel('doc_response_output.xlsx')

    obligation_objs = ObligationMetadata.objects.all()
    for obligation_obj in obligation_objs:
        obligation_data.append({
            "obligation_id":obligation_obj.obligation_id,
            "document_id":obligation_obj.document_id,
            "suggestions":obligation_obj.suggestions,
        })
    pd.DataFrame(obligation_data).to_excel('obligation_output.xlsx')

    return HttpResponse({'status_code':200})



def create_risk_and_milestone(request):
    if request.method == 'POST':
        # Handling RiskTrackingRecordForm
        if 'form' in request.POST:
            risk_form = RiskTrackingRecordForm(request.POST)
            if risk_form.is_valid():
                risk_form.save()
                return redirect('success_page')  # Redirect after saving the risk form
        # Handling MilestoneForm
        elif 'form1' in request.POST:
            milestone_form = MilestoneForm(request.POST)
            if milestone_form.is_valid():
                milestone_form.save()
                return redirect('milestone_list')  # Redirect after saving the milestone form
    else:
        risk_form = RiskTrackingRecordForm()
        milestone_form = MilestoneForm()
        print("milestone_form")

    return render(request, 'obligation_task.html', {
        'form': risk_form,
        'form1': milestone_form,
    })