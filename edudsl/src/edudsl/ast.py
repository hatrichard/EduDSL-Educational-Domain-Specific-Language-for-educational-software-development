from dataclasses import dataclass, field
from typing import Any

@dataclass
class Metadata:
    objectif: str
    niveau: str
    auteur: str

@dataclass
class Option:
    text: str
    correct: bool=False

@dataclass
class Question:
    text: str
    options: list[Option] = field(default_factory=list)

@dataclass
class Quiz:
    name: str
    questions: list[Question] = field(default_factory=list)

@dataclass
class Feedback:
    operator: str
    value: float
    message: str

@dataclass
class Security:
    endpoint: str|None=None
    encrypted_trace: bool=False
    pseudonymize: bool=False
    oauth_client_id: str|None=None
    oauth_scope: str|None=None

@dataclass
class Export:
    scorm: str|None=None
    lti: str|None=None
    xapi: bool=False
    cmi5: bool=False

@dataclass
class Activity:
    kind: str
    name: str
    payload: Any

@dataclass
class Course:
    name: str
    metadata: Metadata
    security: Security|None
    activities: list[Activity]
    export: Export|None
