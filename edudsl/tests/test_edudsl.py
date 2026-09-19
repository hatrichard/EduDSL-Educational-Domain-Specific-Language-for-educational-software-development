import unittest, tempfile
from pathlib import Path
from src.edudsl.parser import Parser
from src.edudsl.semantic import SemanticError, validate
from src.edudsl.generator import generate
DEMO=Path(__file__).parents[1]/'examples/demo.edudsl'
class EduDSLTests(unittest.TestCase):
    def test_parse_and_validate(self):
        c=Parser(DEMO.read_text(encoding='utf-8')).parse(); validate(c)
        self.assertEqual(c.name,'IntroductionPython'); self.assertEqual(len(c.activities),1); self.assertEqual(len(c.activities[0].payload.questions),2)
    def test_https_required(self):
        s=DEMO.read_text(encoding='utf-8').replace('https://lrs.example.org/xapi','http://lrs.example.org/xapi'); c=Parser(s).parse()
        with self.assertRaises(SemanticError): validate(c)
    def test_generation(self):
        c=Parser(DEMO.read_text(encoding='utf-8')).parse()
        with tempfile.TemporaryDirectory() as td:
            out=Path(td); generate(c,out)
            for f in ['index.html','style.css','security.json','xapi-statement.json','lti-config.json','cmi5.xml','scorm.zip','manifest-edudsl.json']: self.assertTrue((out/f).exists(),f)
if __name__=='__main__': unittest.main()
