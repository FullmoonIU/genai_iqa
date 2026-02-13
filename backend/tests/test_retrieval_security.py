from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.db import Base
from app.models import Chunk, Document, User
from app.services.retrieval import retrieve_chunks


def _seed(db: Session):
    u1 = User(username='u1', password_hash='x')
    u2 = User(username='u2', password_hash='y')
    db.add_all([u1, u2])
    db.commit()
    db.refresh(u1)
    db.refresh(u2)

    d1 = Document(name='u1_doc.txt', doc_type='txt', status='indexed', storage_path='a', owner_id=u1.id)
    d2 = Document(name='u2_doc.txt', doc_type='txt', status='indexed', storage_path='b', owner_id=u2.id)
    db.add_all([d1, d2])
    db.commit()
    db.refresh(d1)
    db.refresh(d2)

    db.add_all(
        [
            Chunk(document_id=d1.id, chunk_index=0, page=None, text='binary search tree insert algorithm'),
            Chunk(document_id=d2.id, chunk_index=0, page=None, text='secret notes from another user'),
        ]
    )
    db.commit()

    return u1, u2


def test_retrieve_chunks_filters_by_owner():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        u1, _ = _seed(db)
        results = retrieve_chunks(db, question='binary search tree', owner_id=u1.id, top_k=5)

    assert results
    assert all(r['source_name'] == 'u1_doc.txt' for r in results)