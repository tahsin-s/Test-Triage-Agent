---
name: tag-description-store
description: "Use when: you need to describe a BDD tag, map an unknown tag to a short human-readable description, or persist a new tag definition in the repo."
---

# Tag Description Store

## Goal

When a Playwright BDD tag is not already known, generate a concise description and store it in the canonical tag description registry so the same tag can be reused without repeating the reasoning.

## Workflow

1. Read the tag list from the feature suite or the caller-provided tags file.
2. Check the known catalog in [src/qe_agent/tagging/describe_tags.py](src/qe_agent/tagging/describe_tags.py).
3. If the tag already exists, reuse the stored description.
4. If the tag is unknown:
   - infer its meaning from the tag name, feature name, and scenario names
   - keep it to one sentence
   - prefer plain English over speculation
   - avoid long explanations or multiple candidate descriptions
5. Store the new tag and description in the canonical dictionary.
6. Emit the final tag-to-description mapping in a short, human-readable format.
7. Stop after the first successful save and output; do not broaden the task or continue exploring unrelated scenarios.

## Decision Points

- Known tag -> return the existing description.
- Unknown tag -> generate a short description and persist it.
- Ambiguous tag -> choose the safest concise interpretation, then store it as a provisional description.
- Missing file or invalid input -> fail fast with a short error instead of looping.

## Quality Checks

- The description is understandable by a human reviewer.
- The output stays short and CLI-friendly.
- The description is stored in the canonical registry, not only printed once.
- The workflow is bounded to one generated description per unknown tag.

## Scope

This skill is intended for the slice-3 tag-description flow and for later reuse in the CLI tooling that reads Playwright BDD tags from the feature suite.

## Example

If the tag list contains `@CreatesData` and `@UnknownTag`, the workflow should:

- return the known description for `@CreatesData`
- generate a brief one-line definition for `@UnknownTag`
- save that mapping into the canonical tag-description registry
- emit the final short list without extra chatter
