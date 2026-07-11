from aquatwin.engine.feeding_engine import FeedingEngine


def test_calculate_organic_n() -> None:
    result = FeedingEngine.calculate_organic_n(
        food_mass_g=2.0,
        protein_fraction=0.4,
        nitrogen_conversion_factor=0.16,
    )

    assert result == 128.0