class VirtueFlaw:
    def __init__(self, name: str, cost: int, description: str, is_virtue: bool = True):
        self.name = name
        self.cost = cost
        self.points = -cost if is_virtue else cost  # For flaws, points are positive
        self.description = description

    @classmethod
    def get_virtues(cls) -> list['VirtueFlaw']:
        return []

    @classmethod
    def get_flaws(cls) -> list['VirtueFlaw']:
        return []

    @classmethod
    def get_virtue(cls, name: str) -> 'VirtueFlaw | None':
        return next((v for v in cls.get_virtues() if v.name == name), None)

    @classmethod
    def get_flaw(cls, name: str) -> 'VirtueFlaw | None':
        return next((f for f in cls.get_flaws() if f.name == name), None) 