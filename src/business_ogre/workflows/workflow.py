"""
Example usage of Workflow and WorkflowBlock classes:

# Define some example WorkflowBlocks
class MakeTextUppercase(WorkflowBlock):
    input_type = (str,)
    output_type = (str,)

    def action(self, input_data: str) -> str:
        return input_data.upper()

class AddExclamation(WorkflowBlock):
    input_type = (str,)
    output_type = (str,)

    def action(self, input_data: str) -> str:
        return input_data + '!'

# Instantiating each block:
make_uppercase_step = MakeTextUppercase('Uppercase')
add_exclamation_step = AddExclamation('Add Exclamation')

# Using the >> operator joins the blocks into a workflow
excited_workflow = MakeTextUppercase('Uppercase') >> AddExclamation('Add Exclamation')

# excited_workflow is callable, inputs will consecutively pass through the blocks:
excited_workflow('A piece of test text')
>>> 'A PIECE OF TEST TEXT!'

str(excited_workflow)
>>> "Workflow(steps='Uppercase >> Add Exclamation')"

# Check that the output type of each step matches the input type of the next step.
# Raises an error if there is a mismatch, otherwise returns True.
excited_workflow.validate()
>>> True
"""

from typing import Callable, Any

class Workflow:
    ''' 
    Class representing a workflow, which is a sequence of WorkflowBlocks. The workflow is callable,
    and when called, it executes each block in sequence, passing the output of one block as the input
    to the next block. The workflow also has a name that is generated based on the names of the blocks
    it contains.
    '''
    def __init__(self) -> None:
        self.blocks: list["WorkflowBlock"] = []
        self._generate_name()

    def add_block(self, block: "WorkflowBlock") -> None:
        ''' Adds a WorkflowBlock to the workflow and updates the workflow name. '''
        self.blocks.append(block)
        self._generate_name()

    def _generate_name(self) -> None:
        block_names = [block.name for block in self.blocks]
        self.name = " >> ".join(block_names)

    def __call__(self, initial_data=None):
        ''' Executes the workflow by passing the initial data through each block in sequence. '''
        data = initial_data
        for block in self.blocks:
            data = block(data)
        return data
    
    def validate(self) -> bool:
        ''' Validates that the output type of each block matches the input type of the next block. '''
        for i in range(len(self.blocks) - 1):
            current_block = self.blocks[i]
            next_block = self.blocks[i + 1]

            if not any(issubclass(t, current_block.output_type) for t in next_block.input_type):
                raise TypeError(f"Output type of block '{current_block.name}' does not match input type of block '{next_block.name}'.")
            
        return True

    def __rshift__(self, other: "WorkflowBlock | Workflow") -> "Workflow":
        wf = Workflow()
        for block in self.blocks:
            wf.add_block(block)

        if isinstance(other, WorkflowBlock):
            wf.add_block(other)
            return wf
        
        elif isinstance(other, Workflow):
            for block in other.blocks:
                wf.add_block(block)
            return wf
        
        else:
            return NotImplemented
    
    def __repr__(self) -> str:
        return f"Workflow(steps='{self.name}')"

class WorkflowBlock:
    '''
    Base class for workflow blocks. Each block has a name, an optional description,
    and defines an action that transforms input data to output data. The input and
    output types can be specified as class attributes.

    Things to define when inheriting from WorkflowBlock:
    - input_type: A tuple of types that the block can accept as input.
    - output_type: A tuple of types that the block can produce as output.
    - action: A method that takes input data and returns output data.

    Arguments:
    - name: A string name for the block.
    - description: An optional string description for the block.

    Example usage:
        class MakeTextUppercase(WorkflowBlock):
            input_type = (str,)
            output_type = (str,)

            def action(self, input_data: str) -> str:
                return input_data.upper()

        make_uppercase_step = MakeTextUppercase('Uppercase')

        class AddExclamation(WorkflowBlock):
            input_type = (str,)
            output_type = (str,)

            def action(self, input_data: str) -> str:
                return input_data + '!'

        add_exclamation_step = AddExclamation('Add Exclamation')

        # Each block is callable, and applies its action to the input data:
        add_exclamation_step('Hello')
        >>> 'Hello!'

        # Using the >> operator joins the blocks into a workflow
        excited_workflow = MakeTextUppercase('Uppercase') >> AddExclamation('Add Exclamation')

        # excited_workflow is callable, inputs will consecutively pass through each blocks:
        excited_workflow('A piece of test text')
        >>> 'A PIECE OF TEST TEXT!'

        excited_workflow
        >>> Workflow(steps='Uppercase >> Add Exclamation')

        # Check that the output type of each step matches the input type of the next step.
        # Raises an error if there is a mismatch, otherwise returns True.
        excited_workflow.validate()
        >>> True
    '''
    input_type: tuple[Any, ...] = ()
    output_type: tuple[Any, ...] = ()

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description

    def action(self, input_data: Any) -> Any:
        raise NotImplementedError("Subclasses must implement the action method.")

    def __call__(self, data: Any) -> Any:
        data = self.action(data)
        return data

    def __rshift__(self, other):

        if isinstance(other, WorkflowBlock):
            wf = Workflow()
            wf.add_block(self)
            wf.add_block(other)
        
        elif isinstance(other, Workflow):
            wf = Workflow()
            wf.add_block(self)
            for block in other.blocks:
                wf.add_block(block)

        else:
            return NotImplemented

        return wf
    
    def __lshift__(self, other):
        return other >> self
    
    def __repr__(self):
        return f"WorkflowBlock(name='{self.name}')"