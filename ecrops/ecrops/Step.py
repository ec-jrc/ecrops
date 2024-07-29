from abc import ABC, abstractmethod


class Step(ABC):
    """Abstract class that rapresents a generic step of the model workflow"""
    @abstractmethod
    def getparameterslist(self):
        """Return the list of the parameters of the steps"""
        pass

    @abstractmethod
    def getinputslist(self):
        """Return the list of the inputs of the step"""
        pass

    @abstractmethod
    def getoutputslist(self):
        """Return the list of the outputs of the step"""
        pass

    @abstractmethod
    def setparameters(self, status):
        """Prepare the parameters necessary for the step run (it is called only before executing the step for the first time)"""
        pass

    @abstractmethod
    def initialize(self, status):
        """Initialize the step data, for example the status variables used in the step (it is called only before executing the step for the first time)"""
        pass

    @abstractmethod
    def runstep(self, status):
        """Execute all the step’s operations"""
        pass

    @abstractmethod
    def integrate(self, status):
        """Merge the values of the previous time interval before the calculation of the current time interval step operations"""
        pass
