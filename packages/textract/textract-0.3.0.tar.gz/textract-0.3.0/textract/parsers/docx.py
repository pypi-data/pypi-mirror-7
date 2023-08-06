from ..utils import non_local_import


def extract(filename, **kwargs):
    """Extract text from docx file using python-docx.
    """
    docx = non_local_import('docx')
    document = docx.Document(filename)
    return '\n\n'.join([
        paragraph.text.encode('utf-8') for paragraph in document.paragraphs
    ])
