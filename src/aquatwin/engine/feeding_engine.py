from aquatwin.configuration.constants import MG_PER_G


class FeedingEngine:
    """Converts feed mass into Organic Nitrogen (mg-N)."""

    @staticmethod
    def calculate_organic_n(
        food_mass_g: float,
        protein_fraction: float,
        nitrogen_conversion_factor: float,
    ) -> float:
        protein_g = food_mass_g * protein_fraction
        nitrogen_g = protein_g * nitrogen_conversion_factor
        organic_n_mg = nitrogen_g * MG_PER_G

        return organic_n_mg