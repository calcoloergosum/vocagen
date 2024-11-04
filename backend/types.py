import dataclasses

@dataclasses.dataclass
class User:
    email: str
    is_authenticated: bool = False
    is_active: bool = True
    is_anonymous: bool = False
    
    def get_id(self) -> str:
        return self.email


@dataclasses.dataclass
class LanguagePairStatistics:
    L1: str
    L2: str
    total_seconds: float
    n_sentences: int

    def to_dict(self) -> dict:
        return {
            "L1": self.L1,
            "L2": self.L2,
            "total_seconds": self.total_seconds,
            "n_sentences": self.n_sentences,
        }

    @classmethod
    def from_dict(cls, d: dict, L1: str, L2: str) -> "LanguagePairStatistics":
        return cls(d.get("L1", L1), d.get("L2", L2), d.get("total_seconds", 0), d.get("n_sentences", 0))


@dataclasses.dataclass
class Statistics:
    email: str
    n_reports: int
    per_language_pair: dict[str, dict[str, LanguagePairStatistics]]
    achievements: list[str]

    @classmethod
    def new(cls, email: str) -> "Statistics":
        return cls(email, 0, {}, [])

    def to_dict(self) -> dict:
        return {
            "email": self.email,
            "n_reports": self.n_reports,
            "per_language_pair": {k: {k2: v2.to_dict() for k2, v2 in v.items()} for k, v in self.per_language_pair.items()},
            "achievements": self.achievements,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Statistics":
        return cls(d["email"], d["n_reports"], {k: {k2: LanguagePairStatistics.from_dict(v2, k, k2) for k2, v2 in v.items()} for k, v in d["per_language_pair"].items()}, d["achievements"])
