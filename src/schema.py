"""Load the entity and relation definitions and derive what the extractor and validator need."""
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENTITIES = ROOT / "entity_definition.yaml"
DEFAULT_RELATIONS = ROOT / "relation_definition.yaml"


@dataclass(frozen=True)
class Schema:
    entity_text: str  # raw YAML, sent to the model verbatim
    relation_text: str
    entity_types: tuple[str, ...]
    relation_types: tuple[str, ...]
    non_node_types: frozenset[str]  # labeled but not graph nodes (filler)
    edge_optional: frozenset[str]  # may have no outgoing edge
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
        relation = {
            "type": "object",
            "properties": {
                "from": {"type": "integer"},
                "to": {"type": "integer"},
                "type": {"type": "string", "enum": list(self.relation_types)},
            },
            "required": ["from", "to", "type"],
            "additionalProperties": False,
        }
        return {
            "type": "object",
            "properties": {
                "entities": {"type": "array", "items": entity},
                "relations": {"type": "array", "items": relation},
                "implicit_main": {"type": "boolean"},
            },
            "required": ["entities", "relations", "implicit_main"],
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
    edge_optional = set(rel.get("edge_optional") or [])
    unknown = edge_optional - set(entities)
    if unknown:
        raise ValueError(f"edge_optional names unknown entity types: {sorted(unknown)}")

    return Schema(
        entity_text=entity_text,
        relation_text=relation_text,
        entity_types=tuple(entities),
        relation_types=tuple(rel["relations"]),
        non_node_types=frozenset(non_node),
        edge_optional=frozenset(edge_optional),
        evidence_kinds=kinds,
    )


def read_yaml(path: Path):
    return yaml.safe_load(Path(path).read_text())


def write_yaml(path: Path, data) -> None:
    """Readable YAML: keep key order, keep unicode, never wrap long text."""
    Path(path).write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=10**9))
