import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import QAHistory, User

router = APIRouter(prefix='/history', tags=['history'])


@router.get('')
def list_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(QAHistory)
        .filter(QAHistory.user_id == user.id)
        .order_by(QAHistory.created_at.desc())
        .limit(200)
        .all()
    )

    items = []
    for r in rows:
        try:
            citations = json.loads(r.citations_json or '[]')
            if not isinstance(citations, list):
                citations = []
        except Exception:
            citations = []

        items.append(
            {
                'id': r.id,
                'question': r.question,
                'answer': r.answer,
                'citations': citations,
                'created_at': r.created_at.isoformat(sep=' ', timespec='seconds'),
            }
        )

    return items