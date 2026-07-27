# Prompt Lab — Findings

## Challenge 1

The system message controls the assistant's behavior, personality, and permanent instructions. The user message contains the user's specific request or question.

When the villain instruction is placed in the system message, the assistant keeps the same villain personality for different questions because the behavior is defined at the assistant level.

When the villain instruction is placed in the user message, the assistant can still follow it, but the personality becomes part of that individual request instead of the assistant's default behavior.

Instructions about the assistant's identity, role, or general behavior should be placed in the system message. Instructions about a specific task or request should be placed in the user message.

## Challenge 2

## Challenge 3

## Challenge 4

## Stretch Challenge