from _common import *  # noqa
import re
from og_oip import config

BA = config.ROOT / "business-analysis"


def test_every_story_is_in_rtm_and_frs_reference_valid_brs():
    rtm = (BA / "requirements_traceability_matrix.md").read_text()
    stories = re.findall(r"^## (US-\d+)", (BA / "user_stories.md").read_text(), re.M)
    assert len(stories) >= 25 and all(s in rtm for s in stories)
    brs = set(re.findall(r"\| (BR-\d+) \|", (BA / "BRD.md").read_text()))
    used = set(re.findall(r"BR-\d+", (BA / "FRD.md").read_text()))
    assert used <= brs


def test_required_documents_exist():
    for f in ["BRD.md", "FRD.md", "stakeholder_analysis.md", "business_process_as_is.md", "business_process_to_be.md", "user_stories.md", "acceptance_criteria.md",
              "requirements_traceability_matrix.md", "kpi_dictionary.md", "data_requirements.md", "assumptions_and_constraints.md", "risk_register.md", "uat_test_cases.md"]:
        assert (BA / f).exists(), f
    for f in ["README.md", "data_model.md", "dax_measures.dax", "power_query_m_code.txt", "dashboard_specification.md"] + [f"page_0{i}" for i in ()]:
        assert (config.ROOT / "powerbi" / f).exists(), f
    assert len(list((config.ROOT / "powerbi").glob("page_0*.md"))) == 7
    for f in ["README.md", "dashboard_specification.md", "calculated_fields.md", "data_source_schema.md"]:
        assert (config.ROOT / "tableau" / f).exists(), f
    assert not list(config.ROOT.rglob("*.pbix")) and not list(config.ROOT.rglob("*.twb*"))
