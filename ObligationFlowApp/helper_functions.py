import base64


def get_base64(file):
    """
    Convert an uploaded file to a base64-encoded string.
    """
    file.seek(0)  # Ensure the file pointer is at the beginning
    return base64.b64encode(file.read()).decode('utf-8')


def get_extension(file_name):
    """
    Get the file extension for the provided file name.
    """
    if file_name.endswith('.pdf'):
        return 'pdf'
    if file_name.endswith('.docx'):
        return 'docx'
    return None
