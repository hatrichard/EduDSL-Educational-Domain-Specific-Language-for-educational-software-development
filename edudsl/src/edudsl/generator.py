from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from html import escape
import json, hashlib, secrets
from .semantic import validate

def pseudonymize(actor_id: str) -> str:
    return hashlib.sha256(actor_id.encode()).hexdigest()[:16]

def html_app(c):
    quiz_blocks=[]
    answer_map={}
    for a in c.activities:
        if a.kind=="quiz":
            qhtml=[]
            answer_map[a.name]=[]
            for i,q in enumerate(a.payload.questions):
                opts=[]
                answer_index=0
                for j,o in enumerate(q.options):
                    opts.append(f'<label><input type="radio" name="{escape(a.name)}-q{i}" value="{j}"> {escape(o.text)}</label>')
                    if o.correct: answer_index=j
                answer_map[a.name].append(answer_index)
                qhtml.append(f'<fieldset><legend>{i+1}. {escape(q.text)}</legend>'+"<br>".join(opts)+"</fieldset>")
            quiz_blocks.append('<section class="activity"><h2>'+escape(a.name)+'</h2>'+''.join(qhtml)+'<button onclick="grade(\''+escape(a.name)+'\')">Évaluer</button><p id="feedback-'+escape(a.name)+'"></p></section>')
    answers_json=json.dumps(answer_map,ensure_ascii=False)
    body=''.join(quiz_blocks)
    script="""<script>const answers=ANSWERS; function grade(name){const expected=answers[name];let score=0;expected.forEach((a,i)=>{const x=document.querySelector('input[name="'+name+'-q'+i+'"]:checked');if(x&&Number(x.value)===a)score++;});const pct=Math.round(score*100/expected.length);document.getElementById('feedback-'+name).textContent='Score : '+pct+'% — '+(pct>=50?'Réussite':'Remédiation recommandée');}</script>""".replace('ANSWERS',answers_json)
    return '<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(c.name)+'</title><link rel="stylesheet" href="style.css"></head><body><main><header><h1>'+escape(c.name)+'</h1><p>'+escape(c.metadata.objectif)+' — Niveau : '+escape(c.metadata.niveau)+'</p></header>'+body+'</main>'+script+'</body></html>'

def generate(c, out: Path):
    validate(c); out.mkdir(parents=True,exist_ok=True)
    (out/'index.html').write_text(html_app(c),encoding='utf-8')
    (out/'style.css').write_text('body{font-family:system-ui;max-width:900px;margin:40px auto;padding:0 20px}.activity{border:1px solid #ddd;padding:20px;margin:20px 0}fieldset{margin:15px 0}button{padding:10px 16px}',encoding='utf-8')
    if c.security:
        sec={'endpoint':c.security.endpoint,'encryptedTrace':c.security.encrypted_trace,'pseudonymizeActor':c.security.pseudonymize,'oauth2':{'clientId':c.security.oauth_client_id,'scope':c.security.oauth_scope}}
    else: sec={'defaultsApplied':True,'tls':'1.3','pseudonymizeActor':True}
    (out/'security.json').write_text(json.dumps(sec,indent=2,ensure_ascii=False),encoding='utf-8')
    if c.export:
        if c.export.xapi: generate_xapi(c,out/'xapi-statement.json')
        if c.export.lti: generate_lti(c,out/'lti-config.json')
        if c.export.cmi5: generate_cmi5(c,out/'cmi5.xml')
        if c.export.scorm: generate_scorm(c,out/'scorm.zip')
    (out/'manifest-edudsl.json').write_text(json.dumps({'name':c.name,'version':'0.1.0','generator':'EduDSL','metadata':c.metadata.__dict__},indent=2,ensure_ascii=False),encoding='utf-8')

def generate_xapi(c,path):
    actor={'objectType':'Agent','account':{'homePage':'https://example.org','name':'anonymous-'+pseudonymize('demo-actor')}}
    stmt={'actor':actor,'verb':{'id':'http://adlnet.gov/expapi/verbs/initialized','display':{'fr-FR':'a commencé'}},'object':{'id':'https://example.org/edudsl/'+c.name,'definition':{'name':{'fr-FR':c.name}}},'context':{'platform':'EduDSL','language':'fr-FR'}}
    path.write_text(json.dumps(stmt,indent=2,ensure_ascii=False),encoding='utf-8')

def generate_lti(c,path):
    data={'specification':'LTI 1.3 / LTI Advantage','issuer':'https://example.org','deploymentId':'CHANGE_ME','clientId':c.security.oauth_client_id if c.security else 'CHANGE_ME','authorizationEndpoint':'https://lms.example.org/oauth2/authorize','jwksEndpoint':'https://lms.example.org/.well-known/jwks.json','note':'Configurer les valeurs avec le LMS cible; EduDSL ne génère pas de secrets privés.'}
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')

def generate_cmi5(c,path):
    xml=f'''<?xml version="1.0" encoding="UTF-8"?><courseStructure xmlns="https://w3id.org/xapi/profiles/cmi5/v1/CourseStructure.xsd" id="{escape_id(c.name)}"><title>{escape_id(c.name)}</title><description>{escape_id(c.metadata.objectif)}</description></courseStructure>'''
    path.write_text(xml,encoding='utf-8')

def escape_id(s): return ''.join(ch if ch.isalnum() or ch in '-_.' else '-' for ch in s)

def generate_scorm(c,path):
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); (root/'index.html').write_text(html_app(c),encoding='utf-8'); (root/'style.css').write_text('body{font-family:Arial;max-width:900px;margin:auto;padding:20px}',encoding='utf-8')
        manifest=f'''<?xml version="1.0" encoding="UTF-8"?><manifest identifier="EduDSL-{escape_id(c.name)}" version="1.0" xmlns="http://www.imsglobal.org/xsd/imscp_v1p1" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_v1p3" xmlns:adlseq="http://www.adlnet.org/xsd/adlseq_v1p3"><metadata><schema>ADL SCORM</schema><schemaversion>CAM 2004 4th Edition</schemaversion></metadata><organizations default="ORG1"><organization identifier="ORG1"><title>{escape_id(c.name)}</title><item identifier="ITEM1" identifierref="RES1"><title>{escape_id(c.name)}</title></item></organization></organizations><resources><resource identifier="RES1" type="webcontent" adlcp:scormType="sco" href="index.html"><file href="index.html"/><file href="style.css"/></resource></resources></manifest>'''
        (root/'imsmanifest.xml').write_text(manifest,encoding='utf-8')
        with ZipFile(path,'w',ZIP_DEFLATED) as z:
            for f in root.rglob('*'):
                if f.is_file(): z.write(f,f.relative_to(root))
