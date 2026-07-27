# Prompt Lab — Findings

## Challenge 1

The system message controls the assistant's behavior, personality, and permanent instructions. The user message contains the user's specific request or question.

When the villain instruction is placed in the system message, the assistant keeps the same villain personality for different questions because the behavior is defined at the assistant level.

When the villain instruction is placed in the user message, the assistant can still follow it, but the personality becomes part of that individual request instead of the assistant's default behavior.

Instructions about the assistant's identity, role, or general behavior should be placed in the system message. Instructions about a specific task or request should be placed in the user message.

## Challenge 2

The setting changed was called `temperature`. It controls how random or creative the model's responses are. The full range of values is from 0 to 2.

A temperature value of 0 made the answers identical or almost identical every time because the model became more predictable. A temperature value of 2 made the answers more varied because the model had more freedom to choose different outputs.

A real-world example where a temperature of 0 is useful is a customer support assistant that needs to give consistent answers to common questions. A real-world example where a higher temperature is useful is a brainstorming tool that needs to generate many creative ideas, such as product names or story ideas.

## Challenge 3

The setting used to make the response stop early was `max_tokens`. It controls the maximum number of tokens the model is allowed to generate. A token is a small piece of text that the AI reads and produces; it can be a part of a word, a complete word, or punctuation.

The field that shows why the model stopped is called `finish_reason`. During testing, two values were seen: `length`, which means the response stopped because it reached the max_tokens limit, and `stop`, which means the model finished its answer normally.

Setting a limit on max_tokens is useful in real applications because it helps control API costs and makes responses faster. It also prevents the assistant from generating unnecessarily long answers when a shorter response is enough.

## Challenge 4

The format was taught by providing example conversations before the actual user request. The examples were placed in the messages as user and assistant exchanges, showing the model what kind of response pattern to follow.

Showing examples helps the model recognize the pattern and apply it to new inputs without needing a written explanation of the rules.

This technique is called few-shot prompting. It is different from zero-shot prompting because zero-shot gives the model a task without examples, while few-shot provides examples that guide the expected output.

## Stretch Challenge

The flashcard generator uses all five concepts:

- System message: sets the teacher persona and voice.
- User message: contains the topic word that needs to become a flashcard.
- Temperature: set to 0 so the same topic produces consistent results.
- Max tokens: limits the response length so flashcards do not become too long.
- Few-shot prompting: examples teach the assistant the exact flashcard format without explaining it.