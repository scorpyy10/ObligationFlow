from celery import shared_task
import requests
import os
import boto3
import json
import re
import docx
import PyPDF2

from ObligationFlowApp.models import *
from ObligationFlowProject.settings import *

class Extractor:
    def __init__(self):
        # Get AWS credentials from environment variables
        self.aws_access_key_id = "ACCESS_KEY_ID"
        self.aws_secret_access_key = "SECRET_KEY_ACCESS"
        self.aws_region = "REGION"

    def invokeBedRockTerm(self, context, temperature=0.0, top_p=0.0, max_gen_len=512):
        try:
            # MODELID = "meta.llama3-8b-instruct-v1:0"
            MODELID = "meta.llama3-70b-instruct-v1:0"
    
            prmpt = """
             You are a legal contract analysis AI. Your task is to extract terms from the context of a legal document. Context is the paragraph of document which will be passed 1-by-1. You will output the extracted information in a structured JSON format as follows:
                output = {
                    "terms": [{
                        "<term_value_name>": "<extracted_term_value_or_NA>",
                    }]
                }
                 
                If the context does not contain any term return following structure,
                {
                    "terms": [],
                }
                
                Ensure all information is carefully extracted and structured as requested.
                
                NOTE: Please give only output once. Do not repeat it. And in place of <term_value_name> extract term value name for example Effective date and also extract its value in place of <extracted_term_value_or_NA>
                {
                    "context": "#_CONTEXT_#"
                }

                Do not include Input in your response. 
                Also do not repeat  the same terms again and again if once extracted for the same context.
            """

            # Create boto3 client for Bedrock
            brt = boto3.client(service_name='bedrock-runtime', region_name='us-east-1', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)
            
            prmpt = prmpt.replace("#_CONTEXT_#",context)

            # Define the request body
            body = {
                "prompt": prmpt.strip(),
                "max_gen_len": max_gen_len,
                "temperature": temperature,
                "top_p": top_p
            }
            
            # Convert the request body to JSON format
            body_str = json.dumps(body)
    
            # Invoke the model with correct contentType and accept headers
            response = brt.invoke_model(
                body=body_str,
                modelId=MODELID,
                accept="application/json",  # Ensure this is correct for your model
                contentType="application/json"
            )
            
            # Parse the response body
            response_body = json.loads(response.get('body').read())
            # print("response",response_body['generation'].strip())
            return response_body['generation'].strip()
    
        except Exception as e:
            # Catch and print the error for debugging
            print(f"Error: {e}")

    def invokeBedRockClause(self, context, temperature=0.0, top_p=0.0, max_gen_len=512):
        try:
            # MODELID = "meta.llama3-8b-instruct-v1:0"
            MODELID = "meta.llama3-70b-instruct-v1:0"
    
            prmpt = """
             You are a legal contract analysis AI. Your task is to extract clauses from the context of a legal document, and assess the risk associated with each clause with general contracts by comparing it, give risk percentage in number in the range of 0 to 100 along with reason.Context is the paragraph of document which will be passed 1-by-1. You will output the extracted information in a structured JSON format as follows:
                output = {
                    "clauses": [{
                        "<clause_value_name>": "<extracted_clause_value_or_NA>",
                        "risk_percentage": "<assessed_risk_percentage_for_clause_or_NA>",
                        "risk_reason": "<reason_for_assessed_risk_or_NA>"
                    }],
                }
                 
                If the context does not contain any clause then return following structure,
                {
                    "clauses": []
                }
                
                Ensure all information is carefully extracted and structured as requested.
                
                NOTE: Please give only output once. Do not repeat it. And in place of <clause_value_name> extract clause value name for example Force Majeure Clause and also extract its value in place of <extracted_clause_value_or_NA>.
                Input:
                {
                    "context": "#_CONTEXT_#"
                }

                Do not include Input in your response.
                Also do not repeat  the same clauses again and again if once extracted for the same context.
            """

            # Create boto3 client for Bedrock
            brt = boto3.client(service_name='bedrock-runtime', region_name='us-east-1', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)
            
            prmpt = prmpt.replace("#_CONTEXT_#",context)

            # Define the request body
            body = {
                "prompt": prmpt.strip(),
                "max_gen_len": max_gen_len,
                "temperature": temperature,
                "top_p": top_p
            }
            
            # Convert the request body to JSON format
            body_str = json.dumps(body)
    
            # Invoke the model with correct contentType and accept headers
            response = brt.invoke_model(
                body=body_str,
                modelId=MODELID,
                accept="application/json",  # Ensure this is correct for your model
                contentType="application/json"
            )
            
            # Parse the response body
            response_body = json.loads(response.get('body').read())
            # print("response",response_body['generation'].strip())
            return response_body['generation'].strip()
    
        except Exception as e:
            # Catch and print the error for debugging
            print(f"Error: {e}")

    def invokeBedRockObligation(self, context, temperature=0.0, top_p=0.0, max_gen_len=512):
        try:
            # MODELID = "meta.llama3-8b-instruct-v1:0"
            MODELID = "meta.llama3-70b-instruct-v1:0"
    
            prmpt = """
             You are a legal contract analysis AI. Your task is to extract obligations along with its category from the context of a legal document, and assess the risk associated with each obligation with general contracts by comparing it, give risk percentage in number in the range of 0 to 100 along with reason.Context is the paragraph of document which will be passed 1-by-1. You will output the extracted information in a structured JSON format as follows:
                output = {
                    "obligations": [{
                        "<obligation_value>": "<extracted_obligation_value_or_NA>",
                        "obligation_category": "<extracted_obligation_category_or_NA>",
                        "risk_percentage": "<assessed_risk_percentage_for_obligation_or_NA>",
                        "risk_reason": "<reason_for_assessed_risk_or_NA>",
                        "risk_value": "<extracted_risk_value_in_terms_of_some_amount_money_or_NA>",
                        "penalty": "<extracted_penalty_in_terms_of_some_amount_money_or_NA>",
                        "responsible_party": "<extracted_responsible_party_or_NA>",
                        "due_date": "<extracted_due_date_in_terms_of_dd/mm/yyyy_format_or_NA>",
                        
                    }]
                }
                 
                If the context does not contain any obligation then return following structure,
                {
                    "obligations": []
                }
                
                Ensure all information is carefully extracted and structured as requested.
                
                NOTE: Please give only output once. Do not repeat it. And in place of <obligation_value_name> extract obligation value name and also extract its value in place of <extracted_obligation_value_or_NA>. 
                Input:
                {
                    "context": "#_CONTEXT_#"
                }

                Do not include Input in your response.
                Also do not repeat  the same obligations again and again if once extracted for the same context.
                Do not provide nested json structure inside output json means one json inside another, strickly follow output format.
            """

            # Create boto3 client for Bedrock
            brt = boto3.client(service_name='bedrock-runtime', region_name='us-east-1', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)
            
            prmpt = prmpt.replace("#_CONTEXT_#",context)

            # Define the request body
            body = {
                "prompt": prmpt.strip(),
                "max_gen_len": max_gen_len,
                "temperature": temperature,
                "top_p": top_p
            }
            
            # Convert the request body to JSON format
            body_str = json.dumps(body)
    
            # Invoke the model with correct contentType and accept headers
            response = brt.invoke_model(
                body=body_str,
                modelId=MODELID,
                accept="application/json",  # Ensure this is correct for your model
                contentType="application/json"
            )
            
            # Parse the response body
            response_body = json.loads(response.get('body').read())
            # print("response",response_body['generation'].strip())
            return response_body['generation'].strip()
    
        except Exception as e:
            # Catch and print the error for debugging
            print(f"Error: {e}")

    def invokeBedRockContractType(self, context, temperature=0.0, top_p=0.0, max_gen_len=512):
        try:
            # MODELID = "meta.llama3-8b-instruct-v1:0"
            MODELID = "meta.llama3-70b-instruct-v1:0"
    
            prmpt = """
             You are a legal contract analysis AI. Your task is to extract contract type from the context of a legal document.Context is the paragraph of document which will be passed 1-by-1. You will output the extracted information in a structured JSON format as follows:
                output = {
                    "contract_type": "<contract_type_value_or_NA>"
                }
                 
                
                Ensure all information is carefully extracted and structured as requested.
                
                NOTE: Please give only output once. Do not repeat it. 
                Input:
                {
                    "context": "#_CONTEXT_#"
                }

                Do not include Input in your response.
            """

            # Create boto3 client for Bedrock
            brt = boto3.client(service_name='bedrock-runtime', region_name='us-east-1', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)
            
            prmpt = prmpt.replace("#_CONTEXT_#",context)

            # Define the request body
            body = {
                "prompt": prmpt.strip(),
                "max_gen_len": max_gen_len,
                "temperature": temperature,
                "top_p": top_p
            }
            
            # Convert the request body to JSON format
            body_str = json.dumps(body)
    
            # Invoke the model with correct contentType and accept headers
            response = brt.invoke_model(
                body=body_str,
                modelId=MODELID,
                accept="application/json",  # Ensure this is correct for your model
                contentType="application/json"
            )
            
            # Parse the response body
            response_body = json.loads(response.get('body').read())
            # print("response",response_body['generation'].strip())
            return response_body['generation'].strip()
    
        except Exception as e:
            # Catch and print the error for debugging
            print(f"Error: {e}")

    def invokeBedRockObligationMetadata(self, context, temperature=0.0, top_p=0.0, max_gen_len=512):
        try:
            # MODELID = "meta.llama3-8b-instruct-v1:0"
            MODELID = "meta.llama3-70b-instruct-v1:0"
    
            prmpt = """
             Your task is to extract metadata from the context of a legal document.Do not add it from your side, strictly whatever meta-data you found from the given context just extract that. Context is the paragraph of document. You will output the extracted information in a structured JSON format:
                output = {
                   
                }
                 
                
                Ensure all information is carefully extracted and structured as requested.
                
                NOTE: Please give only output once. Do not repeat it.
                INPUT:
                {
                    "context": "#_CONTEXT_#"
                }

                Do not include Input in your response. 
                Also do not repeat  the same things again and again if once extracted for the same context.
            """

            # Create boto3 client for Bedrock
            brt = boto3.client(service_name='bedrock-runtime', region_name='us-east-1', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)
            
            prmpt = prmpt.replace("#_CONTEXT_#",context)

            # Define the request body
            body = {
                "prompt": prmpt.strip(),
                "max_gen_len": max_gen_len,
                "temperature": temperature,
                "top_p": top_p
            }
            
            # Convert the request body to JSON format
            body_str = json.dumps(body)
    
            # Invoke the model with correct contentType and accept headers
            response = brt.invoke_model(
                body=body_str,
                modelId=MODELID,
                accept="application/json",  # Ensure this is correct for your model
                contentType="application/json"
            )
            
            # Parse the response body
            response_body = json.loads(response.get('body').read())
            # print("response",response_body['generation'].strip())
            return response_body['generation'].strip()
    
        except Exception as e:
            # Catch and print the error for debugging
            print(f"Error: {e}")

    def invokeBedRockRiskNeutralization(self, context, temperature=0.0, top_p=0.0, max_gen_len=512):
        try:
            # MODELID = "meta.llama3-8b-instruct-v1:0"
            MODELID = "meta.llama3-70b-instruct-v1:0"
    
            prmpt = """
             Your task is to generate risk neutralization suggestions after understanding the risk from input given below and also provide risk neutralized obligation. You will output the risk neutralization suggestion and risk neutralized obligation in a structured JSON format:
                output = {
                   "suggestions":["<suggestion_1_value>", ]
                   "risk_neutralized_obligations":["<risk_neutralized_obligation_1_value>", ]
                }
                 
                
                Ensure all suggestions are well structured as requested.

                if no suggestion and risk_neutralized_obligations are there give output as below:
                output = {
                   "suggestions":[]
                   "risk_neutralized_obligations":[]
                }
                
                NOTE: Please give only output once. Do not repeat it.
                INPUT:
                {
                    "context": "#_CONTEXT_#"
                }

                Do not include Input in your response. 
                Also do not repeat  the same suggestion again and again. And only give output once. And write "DONE" after output.
            """

            # Create boto3 client for Bedrock
            brt = boto3.client(service_name='bedrock-runtime', region_name='us-east-1', aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)
            
            prmpt = prmpt.replace("#_CONTEXT_#",context)

            # Define the request body
            body = {
                "prompt": prmpt.strip(),
                "max_gen_len": max_gen_len,
                "temperature": temperature,
                "top_p": top_p,
                "stop":["DONE"]
            }
            
            # Convert the request body to JSON format
            body_str = json.dumps(body)
    
            # Invoke the model with correct contentType and accept headers
            response = brt.invoke_model(
                body=body_str,
                modelId=MODELID,
                accept="application/json",  # Ensure this is correct for your model
                contentType="application/json",
            )
            
            # Parse the response body
            response_body = json.loads(response.get('body').read())
            # print("response",response_body['generation'].strip())
            return response_body['generation'].strip()
    
        except Exception as e:
            # Catch and print the error for debugging
            print(f"Error: {e}")


    def extract_text_from_pdf(self, file):
        """Extract text from a PDF file-like object."""
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
        return text

    def extract_text_from_docx(self, file):
        """Extract text from a DOCX file-like object."""
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    
    def extract_text_from_uploaded_document(self, document_id):
        # Get the Document instance
        document = Document.objects.get(id=document_id)
        print(document.file)
        # Open the file and pass it to the extraction function
        with document.file.open('rb') as file:
            text = self.extract_text_from_docx(file)
        
        print(text)
        return text

    def chunk_document_into_paragraphs(self, document):
        # Use regex to find paragraphs ending with a period followed by a newline
        paragraphs = re.split(r'\.\n+', document)
        
        # Append the period back to the end of each paragraph (since split removes it)
        paragraphs = [para.strip() + '.' for para in paragraphs if len(para.strip()) > 0]
        
        return paragraphs
    
    def extract_json_from_response(self, response_text):
        # Flexible regex for output JSON containing terms, clauses, obligations
        output_pattern = r'\{\s*("terms"\s*:\s*\[.*?\])?\s*,?\s*("clauses"\s*:\s*\[.*?\])?\s*,?\s*("obligations"\s*:\s*\[.*?\])?\s*\}'

        output_json = None

        # Extract output JSON
        output_match = re.search(output_pattern, response_text, re.DOTALL)
        if output_match:
            output_json = output_match.group()

        return output_json

    def extract(self, document_id):
        document_text = self.extract_text_from_uploaded_document(document_id)
        print(document_text)
        paragraphs = self.chunk_document_into_paragraphs(document_text)
        final_term_json = {}
        final_clause_json = {}
        final_obligation_json = {}

        for i, para in enumerate(paragraphs, start=0):
            # Remove single and double quotes from the paragraph
            para = para.replace("'", "").replace('"', '')

            llm_response_terms = self.invokeBedRockTerm(para)
            llm_response_clauses = self.invokeBedRockClause(para)
            llm_response_obligations = self.invokeBedRockObligation(para)
            # llm_response_contract_type = self.invokeBedRockContractType(para)

            try:
                output_term_json = self.extract_json_from_response(llm_response_terms)
                output_clause_json = self.extract_json_from_response(llm_response_clauses)
                output_obligation_json = self.extract_json_from_response(llm_response_obligations)
                
                # Handle output JSON extraction
                output_term_dict = None
                output_clause_dict = None
                output_obligation_dict = None

                if output_term_json:
                    try:
                        output_term_dict = json.loads(output_term_json)
                    except json.JSONDecodeError:
                        pass
                
                if output_clause_json:
                    try:
                        output_clause_dict = json.loads(output_clause_json)
                    except json.JSONDecodeError:
                        pass

                if output_obligation_json:
                    try:
                        output_obligation_dict = json.loads(output_obligation_json)
                    except json.JSONDecodeError:
                        pass
                
                # Add the paragraph to the output JSON
                if isinstance(output_term_dict, dict):
                    output_term_dict['paragraph'] = para  # Add paragraph to extracted JSON
                
                if isinstance(output_clause_dict, dict):
                    output_clause_dict['paragraph'] = para  # Add paragraph to extracted JSON
 
                if isinstance(output_obligation_dict, dict):
                    output_obligation_dict['paragraph'] = para  # Add paragraph to extracted JSON
 
                # Update the final JSON
                final_term_json[i] = output_term_dict if output_term_dict else {}
                final_obligation_json[i] = output_obligation_dict if output_obligation_dict else {}
                final_clause_json[i] = output_clause_dict if output_clause_dict else {}
                
            
            except Exception as e:
                pass

        return final_term_json, final_clause_json, final_obligation_json

    def format_obligation(self, final_json):
        new_json = {'obligations':[]}
        id = 0

        # OBLIGATION CATEG
        # Iterating through the final_json
        for key, value in final_json.items():
            if 'obligations' in value and 'paragraph' in value:
                for obl in value['obligations']:
                    # Create a new structure for each obligation
                    id += 1
                    obligation_data = {
                        'id': id,
                        'obligation_category': obl.get('obligation_category', 'NA'),
                        'risk_percentage': obl.get('risk_percentage', 'NA'),
                        'reason': obl.get('risk_reason', 'NA'),
                        'paragraph': value['paragraph'],
                        'risk_value': obl.get('risk_value', 'NA'),
                        'penalty': obl.get('penalty', 'NA'),
                        'due_date': obl.get('due_date', 'NA'),
                        'responsible_party': obl.get('responsible_party', 'NA'),
                    }

                    # Add the obligation name and value to the new structure
                    for obl_name, obl_value in obl.items():
                        if obl_name not in ['risk_percentage', 'risk_reason', 'obligation_category', 'responsible_party', 'due_date', 'penalty', 'risk_value']:
                            obligation_data[obl_name] = obl_value

                    # Append the transformed obligation to new_json
                    new_json['obligations'].append(obligation_data)

        # Display the transformed JSON structure
        print(new_json)
        return new_json
    
    def format_clause(self, final_json):
        new_json = {'clauses':[]}

        # Iterating through the final_json
        for key, value in final_json.items():
            if 'clauses' in value and 'paragraph' in value:
                for obl in value['clauses']:
                    # Create a new structure for each obligation
                    obligation_data = {
                        'risk_percentage': obl.get('risk_percentage', 'NA'),
                        'reason': obl.get('risk_reason', 'NA'),
                        'paragraph': value['paragraph']
                    }

                    # Add the obligation name and value to the new structure
                    for obl_name, obl_value in obl.items():
                        if obl_name not in ['risk_percentage', 'risk_reason']:
                            obligation_data[obl_name] = obl_value

                    # Append the transformed obligation to new_json
                    new_json['clauses'].append(obligation_data)

        # Display the transformed JSON structure
        print(new_json)
        return new_json
    
    def format_term(self, final_json):
        new_json = {'terms':[]}

        # Iterating through the final_json
        for key, value in final_json.items():
            if 'terms' in value and 'paragraph' in value:
                for obl in value['terms']:
                    # Create a new structure for each obligation
                    obligation_data = {
                        'paragraph': value['paragraph']
                    }

                    # Add the obligation name and value to the new structure
                    for obl_name, obl_value in obl.items():
                        if obl_name not in ['risk_percentage', 'risk_reason']:
                            obligation_data[obl_name] = obl_value

                    # Append the transformed obligation to new_json
                    new_json['terms'].append(obligation_data)

        # Display the transformed JSON structure
        print(new_json)
        return new_json
    
    def extract_contract_type_from_response(self, response_text):
    
        contract_type_pattern = r'["\']contract_type["\']\s*:\s*["\']([^"\']*)["\']'


        contract_type_value = None

    # Extract contract_type
        contract_type_match = re.search(contract_type_pattern, response_text, re.DOTALL)
        if contract_type_match:
            # Extract the value of contract_type
            contract_type_value = contract_type_match.group(1)

        return contract_type_value

    def extract_contract_type(self, document_id):
        document_text = self.extract_text_from_uploaded_document(document_id)
        paragraphs = self.chunk_document_into_paragraphs(document_text)

        for i, para in enumerate(paragraphs, start=0):
            
            # Remove single and double quotes from the paragraph
            para = para.replace("'", "").replace('"', '')
            
            llm_response = self.invokeBedRockContractType(para)
            # Print the raw response for debugging
            # print(f"Raw LLM Response for paragraph {i}: {llm_response}")

            # Extract JSON from LLM response
            try:
                contract_type = self.extract_contract_type_from_response(llm_response)
                if contract_type != 'NA' or contract_type is not None:
                    break
            except Exception as e:
                pass
                # print(f"An error occurred while processing paragraph {i}: {str(e)}")

        # Final JSON result
        print(contract_type)
        return contract_type

    def extract_json_structure(self, raw_responses):
        # Regex to extract JSON
        pattern = r'({.*?})(?=\s*$)'
        
        # Find all matches
        output_match = re.search(pattern, raw_responses, re.DOTALL)

        output_json = None

        if output_match:
            output_json = output_match.group()
        
        return output_json

    def format_json_structure(self, final_json):
        output_dict = None
        if final_json:
            try:
                output_dict = json.loads(final_json)
            except json.JSONDecodeError:
                pass
        return output_dict
        

@shared_task
def extract_data_from_contract(data):
    try:
        extractor = Extractor()
        
        term, clause, obligation = extractor.extract(data['document_id'])
        contract_type = extractor.extract_contract_type(data['document_id'])
        term_json = extractor.format_term(term)
        clause_json = extractor.format_clause(clause)
        obligation_json = extractor.format_obligation(obligation)

        res = DocumentResponse(
                    name = data['name'],
                    extracted_terms = term_json,
                    extracted_clauses = clause_json,
                    extracted_obligations = obligation_json,
                    extracted_contract_type = contract_type,
            )

        res.save()
        return "Completed"
    
    except Exception as e:
        print(e)
        return 'Error'


@shared_task
def extract_metadata_from_obligation(data):
    try:
        extractor = Extractor()
        doc_id = data['document_id']
        obligation_id = data['obligation_id']  # Fixed typo here
        document = Document.objects.filter(id=doc_id).first()

        if not document:
            print(f"Document with ID {doc_id} not found.")
            return "Error: Document not found"

        document_response = DocumentResponse.objects.filter(name=document.name).first()
        if not document_response:
            print(f"DocumentResponse with name {document.name} not found.")
            return "Error: DocumentResponse not found"
        
        paragraph = None
        print("Document Name:", document.name)

        for obligation in document_response.extracted_obligations.get('obligations', []):
            if obligation and obligation['id'] == obligation_id:
                paragraph = obligation['paragraph']
                break
        
        if paragraph:
            print("Paragraph:", paragraph)
            paragraph = paragraph.replace("'", "").replace('"', '')
            llm_response = extractor.invokeBedRockObligationMetadata(paragraph)
            metadata_json = extractor.extract_json_structure(llm_response)
            print("json:", metadata_json)
            metadata_dict = extractor.format_json_structure(metadata_json)
            print("dict:", metadata_dict)
            metadata_dict['paragraph'] = paragraph
            metadata_dict['obligation_id'] = obligation_id  # Use corrected variable name

            # Create and save ObligationMetadata instance
            res = ObligationMetadata(
                obligation_id=obligation_id,
                document_id=doc_id,
                metadata=metadata_dict,
            )
            res.save()

            print("Metadata saved successfully.")
        else:
            print(f"No matching paragraph found for obligation_id {obligation_id}.")
            return "Error: Obligation paragraph not found"

        return "Completed"

    except Exception as e:
        print("Exception occurred:", e)
        return "Error"


@shared_task
def extract_risk_neutralization_suggestion_from_obligation(data):
    try:
        extractor = Extractor()
        doc_id = data['document_id']
        obligation_id = data['obligation_id']  # Fixed typo here
        document = Document.objects.filter(id=doc_id).first()

        if not document:
            print(f"Document with ID {doc_id} not found.")
            return "Error: Document not found"

        document_response = DocumentResponse.objects.filter(name=document.name).first()
        if not document_response:
            print(f"DocumentResponse with name {document.name} not found.")
            return "Error: DocumentResponse not found"
        
        main_obligation = None
        print("Document Name:", document.name)

        for obligation in document_response.extracted_obligations.get('obligations', []):
            if obligation and obligation['id'] == obligation_id:
                main_obligation = obligation
                break
        
        if main_obligation:
            print("obligation:", main_obligation)
            
            llm_response = extractor.invokeBedRockRiskNeutralization(str(main_obligation))
            print("llm_res:", llm_response)
            suggestion_json = extractor.extract_json_structure(llm_response)
            print("json:", suggestion_json)
            suggestion_dict = extractor.format_json_structure(suggestion_json)
            print("dict:", suggestion_dict)
            # metadata_dict['paragraph'] = paragraph
            # metadata_dict['obligation_id'] = obligation_id  # Use corrected variable name

            # Create and save ObligationMetadata instance
            res = ObligationMetadata(
                obligation_id=obligation_id,
                document_id=doc_id,
                suggestions=suggestion_dict,
            )
            res.save()

            print("Metadata saved successfully.")
        else:
            print(f"No matching paragraph found for obligation_id {obligation_id}.")
            return "Error: Obligation paragraph not found"

        return "Completed"

    except Exception as e:
        print("Exception occurred:", e)
        return "Error"
