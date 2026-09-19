from urllib.parse import urlparse
from .ast import Course
class SemanticError(Exception): pass

def validate(c: Course):
    if not c.activities: raise SemanticError("Le cours doit contenir au moins une activité")
    for a in c.activities:
        if a.kind=="quiz":
            if not a.payload.questions: raise SemanticError(f"quiz {a.name}: aucune question")
            for qi,q in enumerate(a.payload.questions,1):
                if not q.options: raise SemanticError(f"quiz {a.name}, question {qi}: aucune option")
                if not any(o.correct for o in q.options): raise SemanticError(f"quiz {a.name}, question {qi}: aucune réponse correcte")
    if c.security and c.security.endpoint:
        p=urlparse(c.security.endpoint)
        if p.scheme!="https": raise SemanticError("secureEndpoint doit utiliser https://")
    return True
