from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from app.services.pdf_service import PdfService

router = APIRouter(prefix="/tools", tags=["Tools"])

@router.post("/split-pdf")
async def split_pdf(
    file: UploadFile = File(...), 
    chunk_size: int = Form(...)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
        
    try:
        content = await file.read()
        zip_bytes = PdfService.split_pdf(content, chunk_size)
        
        return Response(
            content=zip_bytes,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=split_files.zip"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
