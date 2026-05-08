# Workflow Build Prompts
These are short prompts you can paste into your coding assistant when you need to assemble a workflow fast.

Use the standard import style in generated code:
```text
import business_ogre as ogr
```

## Strategy 1: Start from block contracts
Use this when you know the business steps, but not the implementation details yet.

Prompt:
```text
Build a business workflow file with 3-5 WorkflowBlock classes for this process: <describe process>. 
Each block must define clear input_type and output_type, and each class should have a short action method.
Then compose them into one final workflow named <workflow_name>.
Keep class and variable names stakeholder-readable.
Use import business_ogre as ogr.
```

Why this works:
- It forces strong typing between steps.
- It keeps naming business-first instead of framework-first.
- It gives you a usable draft you can iterate on quickly.

## Strategy 2: Ask for one concrete happy-path demo
Use this right after generation to prove the file is usable.

Prompt:
```text
Add a tiny runnable example at the bottom of the business file that executes the workflow on one realistic input and prints the result.
Do not add test frameworks or extra scaffolding.
Keep the demo under 12 lines.
```

Why this works:
- You verify end-to-end behavior immediately.
- You get a copy-paste demo for teammates.
- You catch obvious naming or wiring mistakes early.

Related docs:
- `../Best Practices/Neat Business Layer.md`
- `../Best Practices/AI Coding.md`
