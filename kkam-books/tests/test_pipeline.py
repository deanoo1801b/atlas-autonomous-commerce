import unittest

from kkam_pdf_factory.pipeline import (
    GateError, ProductionTask, Stage, complete_stage, record_failure,
)


class PipelineTests(unittest.TestCase):
    def test_cannot_skip_stage(self):
        task = ProductionTask("KKAM-0001")
        with self.assertRaises(GateError):
            complete_stage(task, Stage.BRIEF, outputs={}, passed_criteria=[])
        self.assertEqual(task.stage, Stage.RESEARCH)

    def test_failed_criteria_blocks_task(self):
        task = ProductionTask("KKAM-0001")
        with self.assertRaises(GateError):
            complete_stage(task, Stage.RESEARCH, outputs={}, passed_criteria=[])
        self.assertEqual(task.status, "blocked")
        self.assertEqual(len(task.failure_log), 1)

    def test_concept_approval_requires_reference(self):
        task = ProductionTask("KKAM-0001", stage=Stage.CONCEPT_APPROVAL)
        criteria = [
            "explicit human approval reference recorded",
        ]
        with self.assertRaises(GateError):
            complete_stage(task, Stage.CONCEPT_APPROVAL, outputs={}, passed_criteria=criteria)
        self.assertEqual(task.status, "blocked")

    def test_publish_requires_approval_reference(self):
        task = ProductionTask("KKAM-0001", stage=Stage.PUBLISH)
        criteria = ["publication explicitly authorized", "target channel and final artifact verified"]
        with self.assertRaises(GateError):
            complete_stage(task, Stage.PUBLISH, outputs={}, passed_criteria=criteria)
        self.assertNotEqual(task.status, "published")

    def test_record_failure_is_persistent_in_task(self):
        task = record_failure(ProductionTask("KKAM-0001"), "missing cover")
        self.assertEqual(task.status, "blocked")
        self.assertEqual(task.failure_log[0]["reason"], "missing cover")


if __name__ == "__main__":
    unittest.main()
