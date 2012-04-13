


class LanguageConfigController:
    def __init__(self, interface):
        self.interface = interface
        self.parent = interface.parent
        self.deck = interface.deck

        