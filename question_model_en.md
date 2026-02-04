# Question Generation Prompt (English)

Please generate multiple-choice or true/false questions based on the attached content (or the topic provided).
The output MUST be a valid JSON object containing a list of questions under the key "questions".

Format Requirements:
- `content`: The question text.
- `type`: Either "multiple_choice" or "true_false".
- `language`: "en"
- `options`: A list of strings. For True/False, use ["True", "False"]. For Multiple Choice, provide 4 options.
- `correct_answer`: The exact string from the options list that is correct.
- `explanation`: A detailed explanation of why the answer is correct.

Example JSON:
```json
{
  "questions": [
    {
      "content": "What is the capital of France?",
      "type": "multiple_choice",
      "language": "en",
      "options": ["London", "Berlin", "Paris", "Madrid"],
      "correct_answer": "Paris",
      "explanation": "Paris is the capital city of France."
    },
    {
      "content": "Water boils at 100 degrees Celsius at sea level.",
      "type": "true_false",
      "language": "en",
      "options": ["True", "False"],
      "correct_answer": "True",
      "explanation": "At standard atmospheric pressure, the boiling point of water is 100°C."
    }
  ]
}
```
