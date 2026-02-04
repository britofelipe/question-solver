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
      "content": "Quelle est la capitale de la France ?",
      "type": "multiple_choice",
      "language": "fr",
      "options": ["Londres", "Berlin", "Paris", "Madrid"],
      "correct_answer": "Paris",
      "explanation": "Paris est la capitale de la France."
    },
    {
      "content": "L'eau bout à 100 degrés Celsius au niveau de la mer.",
      "type": "true_false",
      "language": "fr",
      "options": ["Vrai", "Faux"],
      "correct_answer": "Vrai",
      "explanation": "À la pression atmosphérique standard, le point d'ébullition de l'eau est de 100°C."
    }
  ]
}
```
