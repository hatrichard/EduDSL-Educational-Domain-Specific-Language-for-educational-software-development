# EduDSL — Educational Domain-Specific Language

Prototype exécutable du langage **EduDSL (Educational Domain-Specific Language)** proposé dans le mémoire de Master 2 « Proposition d’un langage spécifique pour le développement des logiciels éducatifs ».

## Objectif

EduDSL est conçu comme un DSL hybride orienté vers la création de ressources éducatives :

- primitives pédagogiques : `quiz`, `question`, `feedback`, `path`, `exercice`, `lecture`, `analytics` ;
- sécurité by design : `secureEndpoint`, `encryptedTrace`, `oauth2` ;
- génération d'artefacts : HTML5/CSS/JavaScript, paquet SCORM 2004, configuration LTI 1.3, statement xAPI et manifeste cmi5 ;
- validation sémantique : quiz non vide, réponse correcte, références de parcours, endpoints HTTPS.

Le mémoire décrit une architecture syntaxique, sémantique, interopérabilité, sécurité et persistance, avec ANTLR4 comme technologie de parsing. Cette version GitHub fournit une **implémentation de référence légère et autonome en Python** pour rendre le prototype immédiatement exécutable. Le fichier ANTLR est également fourni dans `grammar/EduDSL.g4` pour permettre une migration directe vers un parser ANTLR4.

> Important : ce dépôt constitue un prototype de recherche. La génération des artefacts d'interopérabilité est volontairement minimale et doit être validée contre les spécifications et l'environnement LMS/LRS cible avant une utilisation en production.

## Prérequis

- Python 3.10+
- aucune dépendance externe pour exécuter le prototype de base

## Exécution

```bash
python main.py examples/demo.edudsl --out generated/demo
```

Puis ouvrir :

```text
generated/demo/index.html
```

Pour vérifier le script sans générer :

```bash
python main.py examples/demo.edudsl --validate-only
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## Structure

```text
EduDSL/
├── main.py
├── grammar/
│   ├── EduDSL.ebnf
│   └── EduDSL.g4
├── src/edudsl/
│   ├── lexer.py
│   ├── parser.py
│   ├── ast.py
│   ├── semantic.py
│   └── generator.py
├── examples/demo.edudsl
├── tests/test_edudsl.py
└── docs/ANNEXE_EBNF.md
```

## Exemple minimal

```edudsl
Cours IntroductionPython {
  metadata {
    objectif = "Comprendre les variables"
    niveau = "Débutant"
    auteur = "Enseignant"
  }

  securite {
    secureEndpoint "https://lms.example.org/xapi"
    encryptedTrace xapi { pseudonymize actor }
    oauth2 clientId = "demo-client" scope = "xapi.write"
  }

  activite quiz Diagnostic {
    question "Que signifie une variable ?" {
      option "Une valeur nommée" correct
      option "Une image"
    }
    feedback if score >= 50 {
      message = "Bravo !"
    }
  }

  export {
    scorm "2004"
    lti "1.3"
    xapi
    cmi5
  }
}
FinCours
```
