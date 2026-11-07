"""Load the entity and relation definitions and derive what the extractor and validator need."""
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENTITIES = ROOT / "entity_definition.yaml"
DEFAULT_RELATIONS = ROOT / "relation.yaml"


@dataclass(frozen=True)
class Schema:
    entity_text: str  # raw YAML, sent to the model verbatim
    relation_text: str
    entity_types: tuple[str, ...]
    relation_types: tuple[str, ...]
    non_node_types: frozenset[str]  # labeled but not graph nodes (filler)
    never_primary: frozenset[str]  # relations that are always extra edges (conflicts)
    evidence_kinds: tuple[str, ...]

    def output_json_schema(self) -> dict:
        """JSON Schema for the model's structured output."""
        nullable_str = {"anyOf": [{"type": "string"}, {"type": "null"}]}
        entity = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "type": {"type": "string", "enum": list(self.entity_types)},
                "text": {"type": "string"},
                "main": {"type": "boolean"},
                "hedged": {"type": "boolean"},
                "kind": {"anyOf": [{"type": "string", "enum": list(self.evidence_kinds)}, {"type": "null"}]},
                "note": nullable_str,
            },
            "required": ["id", "type", "text", "main", "hedged", "kind", "note"],
            "additionalProperties": False,
        }
        edge = {
            "type": "object",
            "properties": {
                "from": {"type": "integer"},
                "to": {"type": "integer"},
                "type": {"type": "string", "enum": list(self.relation_types)},
                "primary": {"type": "boolean"},
            },
            "required": ["from", "to", "type", "primary"],
            "additionalProperties": False,
        }
        return {
            "type": "object",
            "properties": {
                "nodes": {"type": "array", "items": entity},
                "edges": {"type": "array", "items": edge},
                "implicit_main": {"type": "boolean"},
            },
            "required": ["nodes", "edges", "implicit_main"],
            "additionalProperties": False,
        }


def load_schema(entities_path: Path = DEFAULT_ENTITIES, relations_path: Path = DEFAULT_RELATIONS) -> Schema:
    entity_text = Path(entities_path).read_text()
    relation_text = Path(relations_path).read_text()
    ent = yaml.safe_load(entity_text)
    rel = yaml.safe_load(relation_text)

    entities = ent["entities"]
    non_node = {name for name, spec in entities.items() if str(spec.get("graph", "")).startswith("not a node")}
    kinds = tuple(entities.get("evidence", {}).get("attributes", {}).get("kind", {}).keys())
    relations = rel["relations"]
    never_primary = {name for name, spec in relations.items()
                     if str(spec.get("primary", "")).lower().startswith("never")}

    return Schema(
        entity_text=entity_text,
        relation_text=relation_text,
        entity_types=tuple(entities),
        relation_types=tuple(relations),
        non_node_types=frozenset(non_node),
        never_primary=frozenset(never_primary),
        evidence_kinds=kinds,
    )


def read_yaml(path: Path):
    return yaml.safe_load(Path(path).read_text())


def write_yaml(path: Path, data) -> None:
    """Readable YAML: keep key order, keep unicode, never wrap long text."""
    Path(path).write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=10**9))
