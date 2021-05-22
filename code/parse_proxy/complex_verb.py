from parse_proxy import ParseProxy


class ComplexVerb:
    def __init__(self, modal: ParseProxy, infinitive: ParseProxy):
        self.modal = modal
        self.infinitive = infinitive

    def inflect(self, required_grammemes):
        new_modal = self.modal.inflect(required_grammemes)
        return ComplexVerb(new_modal, self.infinitive)

    @property
    def word(self):
        return f'{self.modal.word} {self.infinitive.word}'

    @property
    def tag(self):
        return self.modal.tag

    @property
    def normal_form(self):
        return f'{self.modal.normal_form} {self.infinitive.word}'

    @property
    def normalized(self):
        return ComplexVerb(self.modal.normalized, self.infinitive)

    @property
    def _morph(self):
        return self.modal._morph  # noqa
