from pypdf import PdfReader, PdfWriter
import io
import zipfile

class PdfService:
    @staticmethod
    def split_pdf(file_bytes: bytes, chunk_size: int) -> bytes:
        reader = PdfReader(io.BytesIO(file_bytes))
        total_pages = len(reader.pages)
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for start in range(0, total_pages, chunk_size):
                end = min(start + chunk_size, total_pages)
                
                writer = PdfWriter()
                for i in range(start, end):
                    writer.add_page(reader.pages[i])
                
                pdf_buffer = io.BytesIO()
                writer.write(pdf_buffer)
                
                file_name = f"split_{start+1}-{end}.pdf"
                zip_file.writestr(file_name, pdf_buffer.getvalue())
        
        return zip_buffer.getvalue()
