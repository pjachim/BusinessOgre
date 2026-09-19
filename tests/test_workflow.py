import pytest

from business_ogre.workflows.workflow import ForEach, ForEachResult, Workflow, WorkflowBlock


class MakeTextUppercase(WorkflowBlock):
    input_type = (str,)
    output_type = (str,)

    def action(self, input_data: str) -> str:
        return input_data.upper()


class AddExclamation(WorkflowBlock):
    input_type = (str,)
    output_type = (str,)

    def action(self, input_data: str) -> str:
        return input_data + "!"


class StringifyNumber(WorkflowBlock):
    input_type = (int,)
    output_type = (str,)

    def action(self, input_data: int) -> str:
        return str(input_data)


class SplitWords(WorkflowBlock):
    input_type = (str,)
    output_type = (list,)

    def action(self, input_data: str) -> list:
        return input_data.split()


class RaiseOnBad(WorkflowBlock):
    input_type = (str,)
    output_type = (str,)

    def action(self, input_data: str) -> str:
        if input_data == "bad":
            raise ValueError("bad word")
        return input_data.upper()


class TestWorkflowBlock:
    def test_call_executes_action(self):
        block = MakeTextUppercase("Uppercase")

        assert block("hello") == "HELLO"

    def test_repr_includes_name(self):
        block = AddExclamation("Add Exclamation")

        assert repr(block) == "WorkflowBlock(name='Add Exclamation')"

    def test_rshift_with_block_creates_workflow(self):
        workflow = MakeTextUppercase("Uppercase") >> AddExclamation("Add Exclamation")

        assert isinstance(workflow, Workflow)
        assert [block.name for block in workflow.blocks] == ["Uppercase", "Add Exclamation"]

    def test_lshift_composes_in_reverse(self):
        workflow = AddExclamation("Add Exclamation") << MakeTextUppercase("Uppercase")

        assert isinstance(workflow, Workflow)
        assert [block.name for block in workflow.blocks] == ["Uppercase", "Add Exclamation"]


class TestWorkflow:
    def test_add_block_updates_name(self):
        workflow = Workflow()
        workflow.add_block(MakeTextUppercase("Uppercase"))
        workflow.add_block(AddExclamation("Add Exclamation"))

        assert workflow.name == "Uppercase >> Add Exclamation"

    def test_call_runs_blocks_in_sequence(self):
        workflow = MakeTextUppercase("Uppercase") >> AddExclamation("Add Exclamation")

        assert workflow("hello") == "HELLO!"

    def test_validate_returns_true_for_compatible_steps(self):
        workflow = MakeTextUppercase("Uppercase") >> AddExclamation("Add Exclamation")

        assert workflow.validate() is True

    def test_validate_raises_for_incompatible_steps(self):
        workflow = MakeTextUppercase("Uppercase") >> StringifyNumber("Stringify")

        with pytest.raises(TypeError, match="Output type of block 'Uppercase' does not match"):
            workflow.validate()

    def test_workflow_rshift_with_block_appends_block(self):
        base = MakeTextUppercase("Uppercase") >> AddExclamation("Add Exclamation")
        extended = base >> AddExclamation("Again")

        assert [block.name for block in extended.blocks] == ["Uppercase", "Add Exclamation", "Again"]

    def test_workflow_rshift_with_workflow_concatenates_blocks(self):
        left = MakeTextUppercase("Uppercase") >> AddExclamation("Add Exclamation")
        right = AddExclamation("Again") >> AddExclamation("Twice")

        combined = left >> right

        assert [block.name for block in combined.blocks] == [
            "Uppercase",
            "Add Exclamation",
            "Again",
            "Twice",
        ]

    def test_repr_shows_step_names(self):
        workflow = MakeTextUppercase("Uppercase") >> AddExclamation("Add Exclamation")

        assert repr(workflow) == "Workflow(steps='Uppercase >> Add Exclamation')"


class TestForEach:
    def test_rejects_incompatible_item_type(self):
        with pytest.raises(TypeError, match="item_type"):
            ForEach("Uppercase Each", MakeTextUppercase("Uppercase"), item_type=int)

    def test_action_collects_results_in_order(self):
        each = ForEach("Uppercase Each", MakeTextUppercase("Uppercase"), item_type=str)

        results = each.action(["a", "b"])

        assert results == [
            ForEachResult(item="a", value="A", error=None),
            ForEachResult(item="b", value="B", error=None),
        ]

    def test_action_captures_per_item_errors(self):
        each = ForEach("Raise On Bad", RaiseOnBad("Raise On Bad"), item_type=str)

        results = each.action(["good", "bad"])

        assert results[0] == ForEachResult(item="good", value="GOOD", error=None)
        assert results[1].item == "bad"
        assert results[1].value is None
        assert isinstance(results[1].error, ValueError)

    def test_composes_via_rshift_mid_chain(self):
        pipeline = SplitWords("Split Words") >> ForEach(
            "Uppercase Each", MakeTextUppercase("Uppercase"), item_type=str
        )

        results = pipeline("hello world")

        assert results == [
            ForEachResult(item="hello", value="HELLO", error=None),
            ForEachResult(item="world", value="WORLD", error=None),
        ]

    def test_validate_skips_check_for_foreach_input(self):
        pipeline = SplitWords("Split Words") >> ForEach(
            "Uppercase Each", MakeTextUppercase("Uppercase"), item_type=str
        )

        assert pipeline.validate() is True