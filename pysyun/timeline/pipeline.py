import time

from compute.graph.structure import Node
from compute.graph.structure import Synapse
from compute.graph.profile import ProfileNode

class PipelineNode(Node):

    def __init__(self, processor):
        self.__processor = processor
        super().__init__()

    def __str__(self):
        return self.__processor.__str__()

    def add(self, neighbor):
        if isinstance(neighbor, Synapse):
            super().add(neighbor)
        else:
            super().add(Synapse().add(neighbor))
        return self

    def activate(self):

        super().activate()

        # Write profiling data
        synapses = self.synapses()
        for i in range(len(synapses)):
            neighborNode = synapses[i].node()
            if isinstance(neighborNode, ProfileNode):
                neighborNode.write([self.delta])        
        
    def process(self):
        data = self.read()
        startAmount = len(data) if None != data else 0
        startTime = time.time()
        data = self.__processor.process(data)
        endTime = time.time()
        endAmount = len(data) if None != data else 0
        self.delta = {
            "amount": endAmount - startAmount,
            "time": endTime - startTime
        }
        self.write(data)
