from abc import ABC, abstractmethod


class AbstractGraphBuilder(ABC):
    """
    Abstract class to provide a definition for creating a graph builder class, to create/plot graphs of the ECroPS workflow structure. This definition is used by ModelWorkflowReader class.
    An example of implementation is given by class TextualGraphBuilder.
    """
    def __init__(self):
        pass

    @abstractmethod
    def initialize(self):
        """
        Initialize the graph builder
        :return:
        """
        pass

    @abstractmethod
    def addStepNode(self, step_name, step_class_instance, step_parameters_dict, step_description):
        """
        Adds a step to the graph
        :param step_name: step name
        :param step_class_instance: instance of the step class
        :param step_parameters_dict: the dictionary containing the step's parameters
        :param step_description: step's description
        :return:
        """
        pass

    @abstractmethod
    def addEdge(self, to_step_name, from_step_name, common_variables):
        """
        Adds an edge between two steps
        :param to_step_name: inbound step name
        :param from_step_name: outbound step name
        :param common_variables: list of common variables that link the two steps
        :return:
        """
        pass

    @abstractmethod
    def finalize(self, config_file, runMode):
        """
        Create/display/plot the graph
        :param config_file : path to the workflow configuration file
        :param runMode : selected runmode
        :return:
        """
        pass

