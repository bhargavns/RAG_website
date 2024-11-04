class PDF_Loader:
    def __init__(self, file_path, PdfFileReader):
        self.file_path = file_path
        self.PdfFileReader = PdfFileReader

    def load(self):
        with open(self.file_path, 'rb') as file:
            pdf = self.PdfFileReader(file)
            return pdf