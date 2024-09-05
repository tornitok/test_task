import pdfplumber

from constants import FIELDS


class PDFParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.text = self._extract_text()

    def _extract_text(self):
        with pdfplumber.open(self.file_path) as pdf:
            return ''.join([page.extract_text() for page in pdf.pages])

    def parse_to_dict(self):
        fields = FIELDS

        extracted_data = {}
        for field_name, start, end in fields:
            extracted_data[field_name] = self._find_between(start, end)

        return extracted_data

    def _find_between(self, start, end):
        try:
            return self.text.split(start)[1].split(end)[0].strip()
        except (IndexError, AttributeError):
            return None


class PDFValidator:
    def __init__(self, reference_data):
        self.reference_data = reference_data

    def validate(self, test_pdf_path):
        parser = PDFParser(test_pdf_path)
        test_data = parser.parse_to_dict()

        differences = self._compare_data(test_data)

        self._print_differences(differences)

        return differences

    def _compare_data(self, test_data):
        differences = {}
        for key, value in self.reference_data.items():
            if key not in test_data or test_data[key] != value:
                differences[key] = {'expected': value, 'found': test_data.get(key, None)}
        return differences

    def _print_differences(self, differences):
        if not differences:
            print("PDF соответствует структуре эталонного шаблона.")
        else:
            print('PDF имеет следующие отличия по сравнению с эталоном:')
            for key, diff in differences.items():
                expected = diff['expected'] if diff['expected'] is not None else 'не указано'
                found = diff['found'] if diff['found'] is not None else 'не найдено'
                print(f'Поле "{key}": Ожидаемое значение "{expected}", Найдено "{found}"')


test_pdf_path = './data/test_task.pdf'

parser = PDFParser(test_pdf_path)
reference_data = parser.parse_to_dict()

validator = PDFValidator(reference_data)
differences = validator.validate(test_pdf_path)
