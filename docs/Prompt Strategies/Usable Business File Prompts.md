# Usable Business File Prompts
These prompts keep business files small, readable, and ready for real use.

Use the standard import style in generated code:
```text
import business_ogre as ogr
```

## Strategy 1: Generate only the business layer
Use this when assistants keep adding too much architecture.

Prompt:
```text
Create only a business file for this use case: <use case>.
Do not generate API routes, database models, or UI code.
Return only WorkflowBlock classes plus one final composed workflow.
Keep the output in one file.
Use import business_ogre as ogr.
```

Why this works:
- It prevents scope creep.
- It preserves the purpose of the business layer.
- It gives you clean code that is easy to hand to stakeholders.

## Strategy 2: Enforce short, useful block docstrings
Use this when code runs but is hard to read.

Prompt:
```text
For each WorkflowBlock class, add a 1-2 line docstring that explains the business intent in plain language.
Avoid technical jargon.
Then return the full updated file.
```

Why this works:
- It improves handoff quality.
- It helps non-engineers review logic.
- It keeps documentation close to the execution path.

Related docs:
- `../Best Practices/Neat Business Layer.md`
- `../Best Practices/AI Coding.md`
