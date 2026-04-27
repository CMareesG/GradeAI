from pdf2image import convert_from_bytes

def convert_pdf_to_images(file_bytes, poppler_path):
    return convert_from_bytes(file_bytes)