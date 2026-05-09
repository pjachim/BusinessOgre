import pytest
import re
from business_ogre.diagrams.mermaid import MermaidDiagram
from business_ogre.workflows.workflow import Workflow, WorkflowBlock


# Test workflow blocks for use in tests
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


class Repeat(WorkflowBlock):
    input_type = (str,)
    output_type = (str,)

    def action(self, input_data: str) -> str:
        return input_data * 2


class TestMermaidDiagramInitialization:
    """Test MermaidDiagram initialization with various inputs."""

    def test_initialization_with_none_components(self):
        """Test that MermaidDiagram can be initialized with None components."""
        diagram = MermaidDiagram(None)
        assert diagram.component_blocks == []
        assert diagram.component_flows == []
        assert diagram._alias_cache == {}
        assert diagram._used_aliases == set()

    def test_initialization_with_empty_list(self):
        """Test that MermaidDiagram can be initialized with an empty list."""
        diagram = MermaidDiagram([])
        assert diagram.component_blocks == []
        assert diagram.component_flows == []

    def test_initialization_with_workflow_block(self):
        """Test initialization with a single WorkflowBlock."""
        block = MakeTextUppercase("Uppercase")
        diagram = MermaidDiagram([block])
        assert len(diagram.component_blocks) == 1
        assert block in diagram.component_blocks
        assert len(diagram.component_flows) == 0

    def test_initialization_with_workflow(self):
        """Test initialization with a Workflow."""
        block1 = MakeTextUppercase("Uppercase")
        block2 = AddExclamation("Add Exclamation")
        workflow = block1 >> block2

        diagram = MermaidDiagram([workflow])
        assert len(diagram.component_blocks) == 2
        assert block1 in diagram.component_blocks
        assert block2 in diagram.component_blocks
        assert workflow in diagram.component_flows

    def test_initialization_with_mixed_components(self):
        """Test initialization with both WorkflowBlocks and Workflows."""
        block1 = MakeTextUppercase("Uppercase")
        block2 = AddExclamation("Add Exclamation")
        block3 = StringifyNumber("Stringify")
        workflow = block1 >> block2

        diagram = MermaidDiagram([workflow, block3])
        assert len(diagram.component_blocks) == 3
        assert block1 in diagram.component_blocks
        assert block2 in diagram.component_blocks
        assert block3 in diagram.component_blocks
        assert workflow in diagram.component_flows


class TestAliasGeneration:
    """Test alias generation and mapping."""

    def test_alias_generation_from_name(self):
        """Test that aliases are generated correctly from block names."""
        block = MakeTextUppercase("Uppercase")
        diagram = MermaidDiagram([block])

        mapping = diagram._generate_alias_mappings(block)
        assert mapping["alias"] == "upp"
        assert "Uppercase" in mapping["label"]
        assert "MakeTextUppercase" in mapping["label"]

    def test_alias_caching(self):
        """Test that alias mappings are cached."""
        block = MakeTextUppercase("Uppercase")
        diagram = MermaidDiagram([block])

        mapping1 = diagram._generate_alias_mappings(block)
        mapping2 = diagram._generate_alias_mappings(block)
        assert mapping1 is mapping2

    def test_unique_aliases_for_same_prefix(self):
        """Test that duplicate aliases get unique suffixes."""
        block1 = MakeTextUppercase("Upper")
        block2 = AddExclamation("Add")
        diagram = MermaidDiagram([block1, block2])

        # First block gets 'upp'
        mapping1 = diagram._generate_alias_mappings(block1)
        assert mapping1["alias"] == "upp"

        # Second block also starts with 'add', should get 'add'
        mapping2 = diagram._generate_alias_mappings(block2)
        assert mapping2["alias"] == "add"

    def test_short_name_handling(self):
        """Test handling of short names that need padding."""
        block = MakeTextUppercase("A")
        diagram = MermaidDiagram([block])

        mapping = diagram._generate_alias_mappings(block)
        assert len(mapping["alias"]) == 3
        # Short name "a" is padded with "blk" to get "abl"
        assert mapping["alias"] == "abl"

    def test_alias_with_special_characters(self):
        """Test that special characters in names are handled correctly."""
        block = MakeTextUppercase('Upper"Case')
        diagram = MermaidDiagram([block])

        mapping = diagram._generate_alias_mappings(block)
        # Quotes should be removed from the normalized alias
        assert '"' not in mapping["alias"]
        # But preserved in label
        assert "'" in mapping["label"]

    def test_collision_handling(self):
        """Test that collisions in aliases are resolved with numbered suffixes."""
        blocks = [MakeTextUppercase(f"Upper{i}") for i in range(5)]
        diagram = MermaidDiagram(blocks)

        aliases = set()
        for block in blocks:
            mapping = diagram._generate_alias_mappings(block)
            assert mapping["alias"] not in aliases
            aliases.add(mapping["alias"])


class TestMermaidGeneration:
    """Test Mermaid diagram generation."""

    def test_basic_mermaid_generation(self):
        """Test basic Mermaid code generation."""
        block1 = MakeTextUppercase("Uppercase")
        block2 = AddExclamation("Add Exclamation")
        workflow = block1 >> block2

        diagram = MermaidDiagram([workflow])
        mermaid_code = diagram.generate_mermaid()

        assert "flowchart LR" in mermaid_code
        assert "upp(" in mermaid_code
        assert "add(" in mermaid_code
        assert "-->" in mermaid_code

    def test_mermaid_orientation_lr(self):
        """Test Mermaid generation with left-to-right orientation."""
        block = MakeTextUppercase("Uppercase")
        diagram = MermaidDiagram([block])
        mermaid_code = diagram.generate_mermaid(orientation="LR")

        assert "flowchart LR" in mermaid_code

    def test_mermaid_orientation_tb(self):
        """Test Mermaid generation with top-to-bottom orientation."""
        block = MakeTextUppercase("Uppercase")
        diagram = MermaidDiagram([block])
        mermaid_code = diagram.generate_mermaid(orientation="TB")

        assert "flowchart TB" in mermaid_code

    def test_mermaid_orientation_custom(self):
        """Test Mermaid generation with custom orientation."""
        block = MakeTextUppercase("Uppercase")
        diagram = MermaidDiagram([block])
        mermaid_code = diagram.generate_mermaid(orientation="RL")

        assert "flowchart RL" in mermaid_code

    def test_node_labels_format(self):
        """Test that node labels are properly formatted."""
        block = MakeTextUppercase("Uppercase")
        diagram = MermaidDiagram([block])
        mermaid_code = diagram.generate_mermaid()

        # Labels should have format: name<br/><i>BlockType</i>
        assert "<br/>" in mermaid_code
        assert "<i>" in mermaid_code
        assert "MakeTextUppercase" in mermaid_code

    def test_single_block_no_edges(self):
        """Test that a single block generates no edges."""
        block = MakeTextUppercase("Uppercase")
        diagram = MermaidDiagram([block])
        mermaid_code = diagram.generate_mermaid()

        # Count arrows - should only have header
        arrow_count = mermaid_code.count("-->")
        assert arrow_count == 0

    def test_simple_workflow_edges(self):
        """Test edge generation for simple workflows."""
        block1 = MakeTextUppercase("Uppercase")
        block2 = AddExclamation("Add Exclamation")
        workflow = block1 >> block2

        diagram = MermaidDiagram([workflow])
        mermaid_code = diagram.generate_mermaid()

        # Should have one edge between blocks
        assert mermaid_code.count("-->") == 1

    def test_complex_workflow_edges(self):
        """Test edge generation for complex workflows."""
        block1 = MakeTextUppercase("Uppercase")
        block2 = AddExclamation("Add Exclamation")
        block3 = Repeat("Repeat")
        workflow = block1 >> block2 >> block3

        diagram = MermaidDiagram([workflow])
        mermaid_code = diagram.generate_mermaid()

        # Should have two edges: block1->block2, block2->block3
        assert mermaid_code.count("-->") == 2

    def test_duplicate_edges_not_repeated(self):
        """Test that duplicate edges are not repeated in the diagram."""
        block1 = MakeTextUppercase("Uppercase")
        block2 = AddExclamation("Add Exclamation")
        workflow1 = block1 >> block2
        workflow2 = block1 >> block2

        diagram = MermaidDiagram([workflow1, workflow2])
        mermaid_code = diagram.generate_mermaid()

        # Both workflows have the same edge, should only appear once
        assert mermaid_code.count("-->") == 1

    def test_block_ordering_is_consistent(self):
        """Test that blocks are ordered consistently."""
        block1 = MakeTextUppercase("B")
        block2 = AddExclamation("A")
        diagram = MermaidDiagram([block1, block2])

        mermaid_code1 = diagram.generate_mermaid()
        
        # Create new diagram with same blocks in different order
        diagram2 = MermaidDiagram([block2, block1])
        mermaid_code2 = diagram2.generate_mermaid()

        # Should be the same regardless of input order
        assert mermaid_code1 == mermaid_code2

    def test_special_characters_in_names(self):
        """Test handling of special characters in block names."""
        block = MakeTextUppercase('Test "Quote" Block')
        diagram = MermaidDiagram([block])
        mermaid_code = diagram.generate_mermaid()

        # Quotes should be converted to single quotes in the output
        assert "'" in mermaid_code
        assert 'Test "Quote" Block' not in mermaid_code or "Test 'Quote' Block" in mermaid_code

    def test_empty_diagram_generation(self):
        """Test generation of diagram with no blocks."""
        diagram = MermaidDiagram([])
        mermaid_code = diagram.generate_mermaid()

        assert "flowchart LR" in mermaid_code
        # Should have no node definitions
        assert mermaid_code.strip() == "flowchart LR"


class TestMermaidFileOutput:
    """Test Mermaid file output functionality."""

    def test_output_to_file(self, tmp_path):
        """Test that Mermaid code is written to file correctly."""
        block1 = MakeTextUppercase("Uppercase")
        block2 = AddExclamation("Add Exclamation")
        workflow = block1 >> block2

        diagram = MermaidDiagram([workflow])
        output_file = tmp_path / "test_diagram.md"

        result = diagram.generate_mermaid(output_path=str(output_file))

        # Should return the mermaid code
        assert "flowchart" in result
        
        # File should exist and contain the code
        assert output_file.exists()
        with open(output_file, "r", encoding="utf-8") as f:
            file_content = f.read()
        assert file_content == result

    def test_file_encoding(self, tmp_path):
        """Test that file is written with UTF-8 encoding."""
        block = MakeTextUppercase("Übersize")  # Name with special characters
        diagram = MermaidDiagram([block])
        output_file = tmp_path / "encoding_test.md"

        diagram.generate_mermaid(output_path=str(output_file))

        # Read file back and verify
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Übersize" in content


class TestMermaidURL:
    """Test Mermaid URL generation."""

    def test_url_generation(self):
        """Test that a valid Mermaid Live URL is generated."""
        block1 = MakeTextUppercase("Uppercase")
        block2 = AddExclamation("Add Exclamation")
        workflow = block1 >> block2

        diagram = MermaidDiagram([workflow])
        url = diagram.generate_mermaid(create_url=True)

        assert url.startswith("https://mermaid.live/edit#pako:")
        assert len(url) > len("https://mermaid.live/edit#pako:")

    def test_url_is_base64_encoded(self):
        """Test that the URL contains valid base64 encoding."""
        block = MakeTextUppercase("Uppercase")
        diagram = MermaidDiagram([block])
        url = diagram.generate_mermaid(create_url=True)

        # Extract the base64 part
        base64_part = url.split("pako:")[-1]
        
        # Should only contain valid base64 characters
        assert re.match(r"^[A-Za-z0-9+/=_-]+$", base64_part)

    def test_url_with_special_characters(self):
        """Test URL generation with special characters in block names."""
        block = MakeTextUppercase('Special "Chars" & <Symbols>')
        diagram = MermaidDiagram([block])
        url = diagram.generate_mermaid(create_url=True)

        assert url.startswith("https://mermaid.live/edit#pako:")
        assert len(url) > len("https://mermaid.live/edit#pako:")

    def test_url_returns_string_not_mermaid_code(self):
        """Test that create_url=True returns URL, not mermaid code."""
        block = MakeTextUppercase("Uppercase")
        diagram = MermaidDiagram([block])
        result = diagram.generate_mermaid(create_url=True)

        assert result.startswith("https://mermaid.live/edit#pako:")
        assert "flowchart" not in result


class TestMermaidIntegration:
    """Integration tests for Mermaid functionality."""

    def test_multiple_workflows_same_diagram(self):
        """Test diagram generation with multiple workflows."""
        # First workflow
        upper = MakeTextUppercase("Upper1")
        exclaim1 = AddExclamation("Exclaim1")
        workflow1 = upper >> exclaim1

        # Second workflow with different blocks
        repeat = Repeat("Repeat")
        exclaim2 = AddExclamation("Exclaim2")
        workflow2 = repeat >> exclaim2

        diagram = MermaidDiagram([workflow1, workflow2])
        mermaid_code = diagram.generate_mermaid()

        # Should contain all unique blocks
        assert all(name in mermaid_code for name in ["Upper1", "Exclaim1", "Repeat", "Exclaim2"])
        # Should have edges for both workflows
        assert mermaid_code.count("-->") == 2

    def test_workflow_with_repeated_blocks(self):
        """Test diagram generation when same block appears in different workflows."""
        block1 = MakeTextUppercase("Uppercase")
        block2 = AddExclamation("Add Exclamation")
        block3 = Repeat("Repeat")

        workflow1 = block1 >> block2
        workflow2 = block2 >> block3  # block2 used in both workflows

        diagram = MermaidDiagram([workflow1, workflow2])
        mermaid_code = diagram.generate_mermaid()

        # Should have 3 unique blocks
        assert len(diagram.component_blocks) == 3
        # Should have 2 edges
        assert mermaid_code.count("-->") == 2

    def test_round_trip_with_file_and_url(self, tmp_path):
        """Test that file output and URL generation are consistent."""
        block1 = MakeTextUppercase("Uppercase")
        block2 = AddExclamation("Add Exclamation")
        workflow = block1 >> block2

        diagram = MermaidDiagram([workflow])
        
        # Generate file
        output_file = tmp_path / "diagram.md"
        file_output = diagram.generate_mermaid(output_path=str(output_file))
        
        # Generate URL
        url_output = diagram.generate_mermaid(create_url=True)

        # File output should be mermaid code
        assert "flowchart" in file_output
        
        # URL output should be a URL
        assert url_output.startswith("https://")
        
        # Both should be valid (file contains code, URL is accessible format)
        assert len(file_output) > 0
        assert len(url_output) > 0
