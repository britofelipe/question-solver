# Prompt de Génération de Questions (Français)

Veuillez générer des questions à choix multiples ou vrai/faux basées sur le contenu joint (ou le sujet fourni).
La sortie DOIT être un objet JSON valide contenant une liste de questions sous la clé "questions".

Exigences de Format:
- `content`: Le texte de la question.
- `type`: Soit "multiple_choice" soit "true_false".
- `language`: "fr"
- `options`: Une liste de chaînes. Pour Vrai/Faux, utilisez ["Vrai", "Faux"]. Pour Choix Multiples, fournissez 4 options.
- `correct_answer`: La chaîne exacte de la liste des options qui est correcte.
- `explanation`: Une explication détaillée de pourquoi la réponse est correcte.

Exemple JSON:
```json
{
  "questions": [
    {
      "content": "",
      "type": "",
      "language": "",
      "options": [],
      "correct_answer": "",
      "explanation": ""
    },
    {
      "content": "",
      "type": "",
      "language": "",
      "options": [],
      "correct_answer": "",
      "explanation": ""
    }
  ]
}
```
