# BusinessOgre
Business Ogre is a business abstraction layer that neatens workflows in your code, forces self-documentation, and simplifies interaction with stakeholders.

If you are new, start with `docs/Installation.md` and then `docs/Quick Start.md`.

### Example usage of Workflow and WorkflowBlock classes:
The key to using business ogre is defining the code blocks. These are classes that inherit from the WorkflowBlock class, and add some cool functionality.

Standard import style used in this project:

```{python}
import business_ogre as ogr

# Define some example WorkflowBlocks
class MakeTextUppercase(ogr.WorkflowBlock):
    input_type = (str,)  # Required for validation
    output_type = (str,) # Required for validation

    # This is the actual action that is happening in your block.
    def action(self, input_data: str) -> str:
        return input_data.upper()

# Creating one more:
class AddExclamation(ogr.WorkflowBlock):
    input_type = (str,)
    output_type = (str,)

    def action(self, input_data: str) -> str:
        return input_data + '!'
```

Next you need to instantiate the blocks:
```{python}
# Instantiating each block:
make_uppercase_step = MakeTextUppercase('Uppercase')
add_exclamation_step = AddExclamation('Add Exclamation')
```

Now that the blocks are instantiated, you can create pipelines using the `>>` operator.
```{python}
# Using the >> operator joins the blocks into a workflow
excited_workflow = MakeTextUppercase('Uppercase') >> AddExclamation('Add Exclamation')
```

You can treat `excited_workflow` like you would a function.
```{python}
# excited_workflow is callable, inputs will consecutively pass through the blocks:
excited_workflow('A piece of test text')
>>> 'A PIECE OF TEST TEXT!'

str(excited_workflow)
>>> "Workflow(steps='Uppercase >> Add Exclamation')"
```

Here is how you check that all the blocks match up:
```{python}
# Check that the output type of each step matches the input type of the next step.
# Raises an error if there is a mismatch, otherwise returns True.
excited_workflow.validate()
>>> True
```

Because the flows are callable, they can easily be passed to frontend code that requires a single, neat callable.

For prompt patterns that help generate cleaner workflow files with coding assistants, see:
- `docs/Prompt Strategies/Workflow Build Prompts.md`
- `docs/Prompt Strategies/Usable Business File Prompts.md`