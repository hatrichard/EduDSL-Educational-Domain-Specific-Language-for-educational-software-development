#!/usr/bin/env python3
import argparse
from pathlib import Path
from src.edudsl.lexer import LexerError
from src.edudsl.parser import Parser, ParseError
from src.edudsl.semantic import SemanticError
from src.edudsl.generator import generate


def main():
    ap = argparse.ArgumentParser(description="EduDSL compiler/generator")
    ap.add_argument("source", help="fichier .edudsl")
    ap.add_argument("--out", default="generated/output", help="répertoire de sortie")
    ap.add_argument("--validate-only", action="store_true")
    args = ap.parse_args()
    source = Path(args.source)
    try:
        text = source.read_text(encoding="utf-8")
        program = Parser(text).parse()
        if args.validate_only:
            print("EduDSL: validation syntaxique et sémantique OK")
            return 0
        out = Path(args.out)
        generate(program, out)
        print(f"EduDSL: génération terminée dans {out.resolve()}")
        return 0
    except (LexerError, ParseError, SemanticError) as exc:
        print(f"EduDSL: erreur: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
