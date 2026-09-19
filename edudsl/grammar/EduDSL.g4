grammar EduDSL;

program      : 'Cours' ID '{' metadata security? activity+ exportBlock? '}' 'FinCours' EOF ;
metadata     : 'metadata' '{' 'objectif' '=' STRING 'niveau' '=' STRING 'auteur' '=' STRING '}' ;
security     : 'securite' '{' (secureEndpoint | encryptedTrace | oauth2)+ '}' ;
secureEndpoint : 'secureEndpoint' STRING ;
encryptedTrace : 'encryptedTrace' 'xapi' '{' 'pseudonymize' 'actor' '}' ;
oauth2       : 'oauth2' 'clientId' '=' STRING 'scope' '=' STRING ;
activity     : 'activite' 'quiz' ID '{' question+ '}' ;
question     : 'question' STRING '{' option+ '}' ;
option       : 'option' STRING 'correct'? ;
exportBlock  : 'export' '{' (scorm | lti | 'xapi' | 'cmi5')+ '}' ;
scorm        : 'scorm' STRING ;
lti          : 'lti' STRING ;
ID           : [a-zA-Z_] [a-zA-Z_0-9]* ;
STRING       : '"' ( '\\' . | ~['"','\\'] )* '"' ;
WS            : [ \t\r\n]+ -> skip ;
COMMENT      : ('//' ~[\r\n]* | '#' ~[\r\n]*) -> skip ;
