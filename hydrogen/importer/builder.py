from .models.sadface import Sadface

class SadfaceBuilder:
    def __init__(self):
        self.sadface = Sadface()

    def with_existing_document(self, document):
        self.sadface = Sadface(document)
        return self

    def with_meta_core(self, key, value):
        self.sadface.set_core_metadata(key, value)
        return self

    def with_meta_other(self, option, key, value):
        self.sadface.set_other_metadata(option, key, value)
        return self

    def with_node(self, node):
        self.sadface.add_node(node)
        return self

    def with_edge(self, edge):
        self.sadface.add_edge(edge)
        return self

    def with_resource(self, resource):
        self.sadface.add_resource(resource)
        return self

    def validate(self):
        return self.sadface.validate()

    def build(self):
        return self.sadface.document
