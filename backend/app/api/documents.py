import os
import shutil

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.db import get_db
from app.models import Document, Chunk, User
from app.services.doc_processing import simple_read_text, chunk_text

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    docs = (
        db.query(Document)
        .filter(Document.owner_id == user.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return [
        {
            "id": d.id,
            "name": d.name,
            "type": d.doc_type,
            "status": d.status,
            "created_at": d.created_at.isoformat(sep=" ", timespec="seconds"),
        }
        for d in docs
    ]


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)

    filename = file.filename or "upload.bin"
    ext = os.path.splitext(filename)[1].lower()
    doc_type = ext.lstrip(".") or "bin"

    storage_name = f"u{user.id}_" + filename
    storage_path = os.path.join(settings.STORAGE_DIR, storage_name)

    with open(storage_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    doc = Document(
        name=filename,
        doc_type=doc_type,
        status="uploaded",
        storage_path=storage_path,
        owner_id=user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {"id": doc.id}


@router.post("/{doc_id}/process")
def process_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id, Document.owner_id == user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Clear old chunks (idempotent)
    db.query(Chunk).filter(Chunk.document_id == doc.id).delete()
    db.commit()

    doc.status = "processing"
    db.commit()

    text = simple_read_text(doc.storage_path)
    chunks = list(chunk_text(text))

    if not chunks:
        doc.status = "failed"
        db.commit()
        raise HTTPException(status_code=400, detail="No text extracted; upload .txt/.md or implement parsers")

    for i, ch in enumerate(chunks):
        db.add(Chunk(document_id=doc.id, chunk_index=i, page=None, text=ch))

    doc.status = "indexed"
    db.commit()

    return {"ok": True, "chunks": len(chunks)}


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == doc_id, Document.owner_id == user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # delete chunks
    db.query(Chunk).filter(Chunk.document_id == doc.id).delete()

    # delete file
    try:
        if doc.storage_path and os.path.exists(doc.storage_path):
            os.remove(doc.storage_path)
    except OSError:
        pass

    db.delete(doc)
    db.commit()

    return {"ok": True}
