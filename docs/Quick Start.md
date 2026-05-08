# Quick Start
## What is BusinessOgre?
Business Ogre is a business abstraction layer that neatens workflows in your code, forces self-documentation, and simplifies interaction with stakeholders.

BusinessOgre accomplishes the following:
 1. It provides an easy to use way to organize and structure your code.
 2. Used properly, it allows you to create a business layer on your code base that is so readable that you can share the .py directly with your shareholders.
 3. When vibecoding, or using other coding assistants, it provides a super readable structure that very quickly allows you to see what is going on with your code. This allows you to catch logical errors faster, and makes it easier to know where to go to find bugs.
 4. Workflows act like functions, making them super ergonomic when connecting the business layer. This makes it easy to pass one clean callable into other parts of your app.

## Before you start
Install BusinessOgre first:
```text
pip install business_ogre
```

## Example usage of Workflow and WorkflowBlock classes:
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

# You can also summarize the steps by passing it to str.
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

## Common workflow pattern
If you are building a business file, a good default is:
1. Keep one class per business step.
2. Give each class a short business-readable name.
3. Compose one final workflow variable that represents the end result.

For larger examples and file-structure guidance, see `Best Practices/Neat Business Layer.md`.