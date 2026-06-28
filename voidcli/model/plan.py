from dataclasses import dataclass, field


@dataclass
class PlanStep:

    id: int

    title: str

    agent: str

    tool: str

    action: str

    args: dict

    completed: bool = False


@dataclass
class Plan:

    steps: list[PlanStep] = field(default_factory=list)

    current_step: int = 0