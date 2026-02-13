import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import QAHistory, User
from app.schemas.qa import AskIn, AskOut, Citation
from app.services.qa import build_answer
from app.services.retrieval import retrieve_chunks

router = APIRouter(prefix='/qa', tags=['qa'])


@router.post('/ask', response_model=AskOut)
def ask(payload: AskIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    evidences = retrieve_chunks(db, payload.question, owner_id=user.id, top_k=payload.top_k)
    answer, citations = build_answer(payload.question, evidences)

    h = QAHistory(
        user_id=user.id,
        question=payload.question,
        answer=answer,
        citations_json=json.dumps(citations, ensure_ascii=False),
    )
    db.add(h)
    db.commit()

    return AskOut(
        answer=answer,
        citations=[Citation(**c) for c in citations],
    )