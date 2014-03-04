class MachCommandBase:
    def __init__(*args, **kwargs):
        pass

class MachCommandConditions:
    @staticmethod
    def is_b2g(cls):
        return False
