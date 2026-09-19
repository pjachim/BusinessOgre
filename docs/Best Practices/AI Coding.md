# AI Coding
BusinessOgre works really well with coding assistants, but only if your prompt is specific enough to keep output clean.

## Keep prompts scoped to the business layer
If you ask for "the whole feature", assistants usually add too much architecture. Ask for one business file first.

Good prompt:
```text
Create one business file for <use case> using WorkflowBlock classes only.
Return only the classes and one final composed workflow variable.
```

## Ask for type contracts explicitly
If you want reusable workflows, do not leave this implicit.

Good prompt:
```text
For each block, define input_type and output_type clearly.
Make sure adjacent blocks are type-compatible.
```

## Require readable business names
Readable naming is the whole point of the business layer.

Good prompt:
```text
Name classes and workflow variables for stakeholders, not infrastructure.
Avoid abbreviations unless they are obvious in the business domain.
```

## Always request a tiny runnable demo
This catches a lot of bad generations quickly.

Good prompt:
```text
Add a tiny happy-path example at the bottom that runs the final workflow once and prints output.
Keep it under 12 lines.
```

## Quick review checklist
Before merging AI-generated business code, check:
1. Each step is one clear business action.
2. The final workflow name says what the pipeline does.
3. `validate()` passes for the composed flow.
4. The file is still easy to hand to a non-engineer for review.
