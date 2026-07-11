"""Repository for reusable simulation profiles."""

from aquatwin.domain.simulation_profile import SimulationProfile


class SimulationProfileRepository:
    """Store and retrieve simulation profiles by identifier."""

    def __init__(
        self,
        profiles: tuple[SimulationProfile, ...] = (),
    ) -> None:
        """Initialize the repository with simulation profiles."""
        self._profiles = profiles
        self._profiles_by_id = {
            profile.profile_id: profile
            for profile in profiles
        }

    def get(self, profile_id: str) -> SimulationProfile:
        """Return a simulation profile by identifier."""
        try:
            return self._profiles_by_id[profile_id]
        except KeyError as error:
            raise KeyError(
                f"Unknown simulation profile: {profile_id}",
            ) from error

    def exists(self, profile_id: str) -> bool:
        """Return whether a simulation profile exists."""
        return profile_id in self._profiles_by_id

    def all(self) -> tuple[SimulationProfile, ...]:
        """Return all profiles in insertion order."""
        return self._profiles