from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

class ArgumentComponent(ABC):
    """
    The base class for all components in the argument structure.
    """

    @abstractmethod
    def display(self) -> str:
        """
        Display the component information.
        """
        pass

class Node(ArgumentComponent):
    """
    Represents a leaf in the argument structure, such as an individual node.
    """

    def __init__(self, text: str):
        self.text = text

    def display(self) -> str:
        return f"Node: {self.text}"

class Edge(ArgumentComponent):
    """
    Represents an edge connecting nodes, a leaf in the argument structure.
    """

    def __init__(self, connection_info: str):
        self.connection_info = connection_info

    def display(self) -> str:
        return f"Edge: {self.connection_info}"

class CompositeArgumentComponent(ArgumentComponent):
    """
    Represents a composite component that can contain other components.
    """

    def __init__(self):
        self.children: List[ArgumentComponent] = []

    def add(self, component: ArgumentComponent):
        self.children.append(component)

    def remove(self, component: ArgumentComponent):
        self.children.remove(component)

    def display(self) -> str:
        return f"{self.__class__.__name__} containing: " + ", ".join(child.display() for child in self.children)

class Nodes(CompositeArgumentComponent):
    """
    A composite of Node objects.
    """
    pass

class Edges(CompositeArgumentComponent):
    """
    A composite of Edge objects.
    """
    pass

class MetadataItem(ArgumentComponent):
    """
    Represents a single piece of metadata, a leaf in the argument structure.
    """

    def __init__(self, data: str):
        self.data = data

    def display(self) -> str:
        return f"MetadataItem: {self.data}"

class Metadata(CompositeArgumentComponent):
    """
    A composite of MetadataItem objects.
    """
    pass

class Resource(ArgumentComponent):
    """
    Represents a resource, a leaf in the argument structure.
    """

    def __init__(self, resource_info: str):
        self.resource_info = resource_info

    def display(self) -> str:
        return f"Resource: {self.resource_info}"

class Resources(CompositeArgumentComponent):
    """
    A composite of Resource objects.
    """
    pass

# Example Usage
if __name__ == "__main__":
    # Creating leaf objects
    node1 = Node("Node 1")
    node2 = Node("Node 2")
    edge1 = Edge("Node 1 -> Node 2")

    # Creating a composite for nodes
    nodes = Nodes()
    nodes.add(node1)
    nodes.add(node2)

    # Creating a composite for edges
    edges = Edges()
    edges.add(edge1)

    # Displaying the composites
    print(nodes.display())
    print(edges.display())
