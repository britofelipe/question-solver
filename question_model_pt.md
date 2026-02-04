# Prompt para Geração de Questões (Português)

Por favor, gere questões de múltipla escolha ou verdadeiro/falso com base no conteúdo anexo (ou no tópico fornecido).
A saída DEVE ser um objeto JSON válido contendo uma lista de questões sob a chave "questions".

Requisitos de Formato:
- `content`: O texto da questão.
- `type`: "multiple_choice" ou "true_false".
- `language`: "pt"
- `options`: Uma lista de strings. Para Verdadeiro/Falso, use ["Verdadeiro", "Falso"]. Para Múltipla Escolha, forneça 4 opções.
- `correct_answer`: A string exata da lista de opções que é a correta.
- `explanation`: Uma explicação detalhada de por que a resposta está correta.

Exemplo JSON:
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
