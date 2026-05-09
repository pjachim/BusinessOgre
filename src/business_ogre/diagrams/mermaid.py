import base64, gc, json, zlib
import business_ogre as ogr

class MermaidDiagram:
    RELEVANT_CLASSES = [ogr.workflow.Workflow, ogr.workflow.WorkflowBlock]

    def __init__(self, components):
        if components is None:
            components = self._list_all_possible_components()
        self.component_blocks = self.collect_blocks(components)
        self.component_flows = [c for c in components if isinstance(c, ogr.workflow.Workflow)]
        self._alias_cache = {}
        self._used_aliases = set()

    def _list_all_possible_components(self):
        return [o for o in gc.get_objects() if isinstance(o, tuple(self.RELEVANT_CLASSES))]

    def collect_blocks(self, components):
        component_set = set()
        for component in components:
            if isinstance(component, ogr.workflow.Workflow):
                component_set.update(component.blocks)
            elif isinstance(component, ogr.workflow.WorkflowBlock):
                component_set.add(component)
        return list(component_set)

    def _generate_alias_mappings(self, block):
        if block in self._alias_cache:
            return self._alias_cache[block]

        name = str(getattr(block, "name", block.__class__.__name__))
        normalized = "".join(ch for ch in name.lower() if ch.isalnum())
        if not normalized:
            normalized = block.__class__.__name__.lower()

        base = normalized[:3]
        if len(base) < 3:
            base = (base + "blk")[:3]

        alias = base
        index = 2
        while alias in self._used_aliases:
            alias = f"{base}{index}"
            index += 1

        self._used_aliases.add(alias)

        safe_name = name.replace('"', "'")
        block_type = block.__class__.__name__.replace('"', "'")
        label = f"{safe_name}<br/><i>{block_type}</i>"

        result = {"alias": alias, "label": label}
        self._alias_cache[block] = result
        return result

    def generate_mermaid(self, orientation="LR", output_path=None, create_url=False):
        lines = [f"flowchart {orientation}"]

        ordered_blocks = sorted(
            self.component_blocks,
            key=lambda b: (getattr(b, "name", ""), b.__class__.__name__, id(b)),
        )

        for block in ordered_blocks:
            mapping = self._generate_alias_mappings(block)
            lines.append(f"    {mapping['alias']}(\"{mapping['label']}\")")

        added_edges = set()
        for flow in self.component_flows:
            flow_blocks = list(getattr(flow, "blocks", []))
            if len(flow_blocks) < 2:
                continue

            #flow_label = str(getattr(flow, "name", "")).replace('"', "'")
            flow_label = None
            for left, right in zip(flow_blocks, flow_blocks[1:]):
                left_alias = self._generate_alias_mappings(left)["alias"]
                right_alias = self._generate_alias_mappings(right)["alias"]
                edge = (left_alias, right_alias, flow_label)
                if edge in added_edges:
                    continue
                added_edges.add(edge)

                if flow_label:
                    lines.append(f"    {left_alias} -->|{flow_label}| {right_alias}")
                else:
                    lines.append(f"    {left_alias} --> {right_alias}")

        mermaid_text = "\n".join(lines)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(mermaid_text)

        if create_url:
            return self._get_mermaid_url(mermaid_text)
        return mermaid_text
    
    def _get_mermaid_url(self, mermaid_code: str) -> str:
        # 1. Define the 'state' the Live Editor expects
        state = {
            "code": mermaid_code,
            "mermaid": '{"theme":"default"}',
            "updateEditor": False,
            "autoSync": True,
            "updateDiagram": False
        }
        
        # 2. Compress and Encode
        json_bytes = json.dumps(state).encode('utf-8')
        compressed = zlib.compress(json_bytes, level=9)
        encoded = base64.b64encode(compressed).decode('utf-8')
        
        # 3. Build the final URL
        return f"https://mermaid.live/edit#pako:{encoded}"