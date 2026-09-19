from .lexer import Lexer
from .ast import *

class ParseError(Exception): pass

class Parser:
    def __init__(self,text): self.t=list(Lexer(text).tokenize()); self.i=0
    @property
    def cur(self): return self.t[self.i]
    def take(self, kind=None, value=None):
        x=self.cur
        if kind and x.kind!=kind: raise ParseError(f"attendu {kind}, trouvé {x.value!r} ligne {x.line}")
        if value and x.value!=value: raise ParseError(f"attendu {value!r}, trouvé {x.value!r} ligne {x.line}")
        self.i+=1; return x
    def accept(self,value):
        if self.cur.value==value: self.i+=1; return True
        return False
    def block(self): self.take("OP","{")
    def endblock(self): self.take("OP","}")
    def string(self): return self.take("STRING").value
    def ident(self): return self.take("ID").value
    def parse(self):
        self.take(value="Cours"); name=self.ident(); self.block()
        md=None; sec=None; acts=[]; exp=None
        while self.cur.value!="}":
            if self.cur.value=="metadata": md=self.metadata()
            elif self.cur.value=="securite": sec=self.security()
            elif self.cur.value=="activite": acts.append(self.activity())
            elif self.cur.value=="export": exp=self.export()
            else: raise ParseError(f"élément inattendu {self.cur.value!r} ligne {self.cur.line}")
        self.endblock(); self.take(value="FinCours"); self.take("EOF")
        if md is None: raise ParseError("metadata est obligatoire")
        return Course(name,md,sec,acts,exp)
    def metadata(self):
        self.take(value="metadata"); self.block(); vals={}
        while self.cur.value!="}":
            k=self.take("ID").value; self.take("OP","="); vals[k]=self.string()
        self.endblock()
        for k in ("objectif","niveau","auteur"):
            if k not in vals: raise ParseError(f"metadata.{k} manquant")
        return Metadata(vals["objectif"],vals["niveau"],vals["auteur"])
    def security(self):
        self.take(value="securite"); self.block(); s=Security()
        while self.cur.value!="}":
            if self.cur.value=="secureEndpoint": self.take(); s.endpoint=self.string()
            elif self.cur.value=="encryptedTrace":
                self.take(); self.take(value="xapi"); self.block(); self.take(value="pseudonymize"); self.take(value="actor"); self.endblock(); s.encrypted_trace=True; s.pseudonymize=True
            elif self.cur.value=="oauth2":
                self.take(); self.take(value="clientId"); self.take("OP","="); s.oauth_client_id=self.string(); self.take(value="scope"); self.take("OP","="); s.oauth_scope=self.string()
            else: raise ParseError(f"sécurité inattendue {self.cur.value!r}")
        self.endblock(); return s
    def activity(self):
        self.take(value="activite"); kind=self.ident(); name=self.ident(); self.block()
        if kind=="quiz":
            qs=[]
            while self.cur.value!="}": qs.append(self.question())
            self.endblock(); return Activity("quiz",name,Quiz(name,qs))
        raise ParseError(f"type d'activité non supporté: {kind}")
    def question(self):
        self.take(value="question"); text=self.string(); self.block(); opts=[]
        while self.cur.value!="}":
            self.take(value="option"); txt=self.string(); correct=self.accept("correct"); opts.append(Option(txt,correct))
        self.endblock(); return Question(text,opts)
    def export(self):
        self.take(value="export"); self.block(); e=Export()
        while self.cur.value!="}":
            k=self.take("ID").value
            if k=="scorm": e.scorm=self.string()
            elif k=="lti": e.lti=self.string()
            elif k=="xapi": e.xapi=True
            elif k=="cmi5": e.cmi5=True
            else: raise ParseError(f"export inconnu: {k}")
        self.endblock(); return e
