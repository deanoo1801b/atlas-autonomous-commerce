from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class Stage(IntEnum):
    RESEARCH = 1
    BRIEF = 2
    CONCEPT_APPROVAL = 3
    ASSET_PRODUCTION = 4
    ASSET_VALIDATION = 5
    PDF_ASSEMBLY = 6
    PAGE_RENDER = 7
    TECHNICAL_QA = 8
    VISUAL_QA = 9
    CORRECTION = 10
    LICENSING_REVIEW = 11
    LISTING_PREPARATION = 12
    CATALOGUE = 13
    FINAL_APPROVAL = 14
    PUBLISH = 15


ACCEPTANCE_CRITERIA: dict[Stage, tuple[str, ...]] = {
    Stage.RESEARCH: ("evidence recorded", "facts separated from assumptions", "audience and differentiation recorded"),
    Stage.BRIEF: ("product format defined", "audience and age range defined where relevant", "page plan and trim size defined"),
    Stage.CONCEPT_APPROVAL: ("explicit human approval reference recorded"),
    Stage.ASSET_PRODUCTION: ("all required source assets generated or supplied", "asset provenance recorded"),
    Stage.ASSET_VALIDATION: ("all required assets present", "asset dimensions and format validated", "licence/source recorded"),
    Stage.PDF_ASSEMBLY: ("PDF generated from approved assets", "source files retained", "page order manifest generated"),
    Stage.PAGE_RENDER: ("all PDF pages rendered", "render manifest matches PDF page count"),
    Stage.TECHNICAL_QA: ("PDF parser passes", "page count and dimensions match brief", "metadata and fonts reviewed"),
    Stage.VISUAL_QA: ("every rendered page inspected", "no unresolved clipping, blank or duplicate pages", "colouring pages meet line-art requirements where applicable"),
    Stage.CORRECTION: ("all failed pages corrected", "PDF rebuilt", "technical and visual QA rerun"),
    Stage.LICENSING_REVIEW: ("originality and rights review recorded", "third-party assets cleared or removed"),
    Stage.LISTING_PREPARATION: ("title, description, keywords and cover prepared", "claims and price checked"),
    Stage.CATALOGUE: ("catalogue entry and version stored", "final file paths verified"),
    Stage.FINAL_APPROVAL: ("explicit final approval reference recorded"),
    Stage.PUBLISH: ("publication explicitly authorized", "target channel and final artifact verified"),
}


@dataclass
class ProductionTask:
    product_id: str
    stage: Stage = Stage.RESEARCH
    status: str = "pending"
    stage_outputs: dict[str, dict[str, Any]] = field(default_factory=dict)
    failure_log: list[dict[str, str]] = field(default_factory=list)
    approval_references: dict[str, str] = field(default_factory=dict)


class GateError(ValueError):
    pass


def complete_stage(
    task: ProductionTask,
    stage: Stage,
    *,
    outputs: dict[str, Any],
    passed_criteria: list[str],
    approval_reference: str | None = None,
) -> ProductionTask:
    if stage != task.stage:
        raise GateError(f"Stage order violation: expected {task.stage.name}, got {stage.name}.")
    required = set(ACCEPTANCE_CRITERIA[stage])
    passed = set(passed_criteria)
    missing = sorted(required - passed)
    if missing:
        task.status = "blocked"
        task.failure_log.append({"stage": stage.name, "reason": "Missing acceptance criteria: " + "; ".join(missing)})
        raise GateError("Stage failed acceptance criteria: " + "; ".join(missing))
    if stage in (Stage.CONCEPT_APPROVAL, Stage.FINAL_APPROVAL, Stage.PUBLISH) and not (approval_reference or "").strip():
        task.status = "blocked"
        task.failure_log.append({"stage": stage.name, "reason": "Explicit approval reference missing."})
        raise GateError(f"{stage.name} requires an explicit approval reference.")
    task.stage_outputs[stage.name] = dict(outputs)
    if approval_reference:
        task.approval_references[stage.name] = approval_reference
    if stage == Stage.PUBLISH:
        task.status = "published"
    else:
        task.stage = Stage(stage + 1)
        task.status = "ready"
    return task


def record_failure(task: ProductionTask, reason: str) -> ProductionTask:
    task.status = "blocked"
    task.failure_log.append({"stage": task.stage.name, "reason": reason})
    return task
