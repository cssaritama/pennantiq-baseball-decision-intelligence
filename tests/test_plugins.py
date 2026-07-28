from src.pennantiq.plugins import DecisionPolicyPlugin, TeamEvidencePlugin


def test_plugin_protocols_are_runtime_checkable():
    assert hasattr(TeamEvidencePlugin, "_is_runtime_protocol")
    assert hasattr(DecisionPolicyPlugin, "_is_runtime_protocol")
