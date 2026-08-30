from storage.database import SessionLocal
from storage.models import Entity, Relationship

def get_related_entities(entity_name: str, relation_type: str = ""):
    db = SessionLocal()
    entity = db.query(Entity).filter(Entity.name == entity_name).first()
    if not entity:
        return []
    query = db.query(Relationship).filter(
        (Relationship.source_id == entity.id) | (Relationship.target_id == entity.id)
    )
    if relation_type:
        query = query.filter(Relationship.relation_type == relation_type)
    rels = query.all()
    result = []
    for rel in rels:
        if rel.source_id == entity.id:
            other = db.query(Entity).filter(Entity.id == rel.target_id).first()
        else:
            other = db.query(Entity).filter(Entity.id == rel.source_id).first()
        if other:
            result.append({"entity": other.name, "relation": rel.relation_type})
    db.close()
    return result