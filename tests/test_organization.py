from src.pennantiq.organization import get_organization, organization_profiles


def test_organization_profiles_exist():
    profiles = organization_profiles()
    assert {"demo-generic", "demo-nyy", "demo-nym", "demo-lad"}.issubset(profiles)
    assert get_organization("demo-nyy")["hero_case"] is True
