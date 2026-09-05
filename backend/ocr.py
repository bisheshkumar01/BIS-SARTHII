import easyocr

# Load OCR model
reader = easyocr.Reader(['en'])

def extract_text(image_path):
    results = reader.readtext(image_path)

    extracted_text = []

    for result in results:
        text = result[1]
        confidence = result[2]

        if confidence > 0.4:
            extracted_text.append(text)

    return extracted_text