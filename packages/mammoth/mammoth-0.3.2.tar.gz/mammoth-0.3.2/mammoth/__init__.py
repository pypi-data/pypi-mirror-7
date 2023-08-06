from .results import Result
from . import docx, conversion, options, documents


def convert_to_html(fileobj, transform_document=None, **kwargs):
    if transform_document is None:
        transform_document = lambda x: x
    return docx.read(fileobj).map(transform_document).bind(lambda document: 
        conversion.convert_document_element_to_html(
            document,
            **options.read_options(kwargs)
        )
    )


def extract_raw_text(fileobj):
    return docx.read(fileobj).map(extract_raw_text_from_element)


def extract_raw_text_from_element(element):
    if isinstance(element, documents.Text):
        return element.value
    else:
        text = "".join(map(extract_raw_text_from_element, element.children))
        if isinstance(element, documents.Paragraph):
            return text + "\n\n"
        else:
            return text
