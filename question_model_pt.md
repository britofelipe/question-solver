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
      "content": "Qual é a capital da França?",
      "type": "multiple_choice",
      "language": "pt",
      "options": ["Londres", "Berlim", "Paris", "Madri"],
      "correct_answer": "Paris",
      "explanation": "Paris é a capital da França."
    },
    {
      "content": "A água ferve a 100 graus Celsius ao nível do mar.",
      "type": "true_false",
      "language": "pt",
      "options": ["Verdadeiro", "Falso"],
      "correct_answer": "Verdadeiro",
      "explanation": "Na pressão atmosférica padrão, o ponto de ebulição da água é 100°C."
    }
  ]
}
```
