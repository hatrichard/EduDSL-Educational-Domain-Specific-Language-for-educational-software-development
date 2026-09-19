import re
from dataclasses import dataclass

KEYWORDS = {
    "Cours", "FinCours", "metadata", "objectif", "niveau", "auteur", "securite",
    "secureEndpoint", "encryptedTrace", "xapi", "pseudonymize", "actor", "oauth2",
    "clientId", "scope", "activite", "quiz", "question", "option", "correct",
    "feedback", "if", "message", "path", "exercice", "consigne", "lecture",
    "contenu", "analytics", "export", "scorm", "lti", "cmi5", "true", "false"
}

@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    col: int

class LexerError(Exception): pass

class Lexer:
    token_re = re.compile(r'''(?P<WS>[ \t\r\n]+)|(?P<COMMENT>//[^\n]*|#[^\n]*)|(?P<STRING>"(?:\\.|[^"\\])*")|(?P<NUMBER>\d+(?:\.\d+)?)|(?P<OP>>=|<=|==|!=|->|[{}=<>])|(?P<ID>[A-Za-z_][A-Za-z0-9_]*)|(?P<PERCENT>%)''')
    def __init__(self, text): self.text=text
    def tokenize(self):
        pos=0; line=1; col=1
        while pos < len(self.text):
            m=self.token_re.match(self.text,pos)
            if not m: raise LexerError(f"caractère inattendu ligne {line}, colonne {col}: {self.text[pos]!r}")
            raw=m.group(0); kind=m.lastgroup
            if kind not in ("WS","COMMENT"):
                val=raw[1:-1] if kind=="STRING" else raw
                yield Token(kind,val,line,col)
            nls=raw.count("\n")
            if nls: line += nls; col = len(raw.rsplit("\n",1)[1])+1
            else: col += len(raw)
            pos=m.end()
        yield Token("EOF","",line,col)
