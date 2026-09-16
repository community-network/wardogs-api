from dataclasses import dataclass, field


@dataclass
class RoleStats:
    level: int = 0
    xp: int = 0


@dataclass
class UnlockInfo:
    node_id: str
    level: int


@dataclass
class PlayerStats:
    player_data_version: int | None = None

    infantry: RoleStats = field(default_factory=RoleStats)
    medic: RoleStats = field(default_factory=RoleStats)
    recon: RoleStats = field(default_factory=RoleStats)
    support: RoleStats = field(default_factory=RoleStats)
    driver: RoleStats = field(default_factory=RoleStats)
    pilot: RoleStats = field(default_factory=RoleStats)

    cash: int = 0
    gold: int = 0

    unlocks: list[UnlockInfo] = field(default_factory=list)

    @property
    def wardog_level(self) -> int:
        """
        Current WARDOGS overall level.

        The live account we tested showed that the in-game Wardog level
        matched the sum of the six role levels.
        """
        return (
            self.infantry.level
            + self.medic.level
            + self.recon.level
            + self.support.level
            + self.driver.level
            + self.pilot.level
        )
