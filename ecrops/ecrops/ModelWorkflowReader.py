import itertools


class ModelWorkflowReader():
    """
    This class explores the workflow of the model and pass the informations of the workflow structure to the provided graph builders.
    The list of configured graph builders is provided in the init method.
    The graph builders should be valid implementations of the ecrops.graphbuilders.AbstractGraphBuilder abstract class.

    Each step of the workflow is transfomed in a node of the resulting graph.
    The edges (connections) between the nodes are the built considering the information between the inputs and the outputs of the steps:
    if an input variable X of a step A is an output of a step B, then a directed edge between the two steps is built. The direction of the edge is from B to A, and the label of the step is X, the name of the variable.

    The equality of the variables is based on the property 'StatusVariable' defined in each step's getinputslist and getoutputslist methods.

    The display_graph method triggers the creation of the graph by the configured graph builders. The nature of final graph depends on the builder implementation.
    """

    def __init__(self, abstractGraphBuilders):
        """
        Set the list of graph builders and calls the initialize method for each one
        :param abstractGraphBuilders:
        """
        self.keys = dict()
        self.abstractGraphBuilders = abstractGraphBuilders
        print('Start creation of workflow graph. Initialization of configured graph builders:' + str(
            abstractGraphBuilders))
        for gb in self.abstractGraphBuilders:
            gb.initialize()

    def get_unique_pairs(self, lst):
        return list(itertools.combinations(lst, 2))

    def add_class(self, step_instance):
        """
        Adds a step to the graph.

        Args:
            step_instance: An instance of the step.
        """
        class_name = type(step_instance).__name__
        self.keys[class_name] = step_instance

        # Get parameters from class instances if the class implements the required method
        step_parameters_dict = {}
        if hasattr(step_instance, 'getparameterslist'):
            step_parameters_dict = step_instance.getparameterslist()

        #step description, from docstring
        step_description = step_instance.__doc__

        print('Adding node ' + class_name + " to workflow graph")
        for gb in self.abstractGraphBuilders:
            gb.addStepNode(class_name, step_instance, step_parameters_dict, step_description)

    def add_all_connections(self):
        """
        Adds all the connections between the steps
        :return:
        """
        print('Adding connections between nodes to workflow graph')
        my_list = self.keys
        couples = self.get_unique_pairs(my_list)
        for c in couples:
            self.add_connection(c[0], c[1])
        for k in my_list.keys():
            self.add_connection(k, k, selfConnection=True)

    def add_connection(self, from_step, to_step, reverse=True, selfConnection=False):
        """
        Add a connection between two nodes
        :param from_step: the outboud step
        :param to_step: the inbound step
        :param reverse: true is the reverse connection should be applied too
        :param selfConnection: true if is is a connection between a node and itself
        :return:
        """

        if from_step in self.keys and to_step in self.keys:
            from_instance = self.keys[from_step]
            to_instance = self.keys[to_step]

            # Get inputs and outputs from class instances if both of them implement the required methods
            if hasattr(from_instance, 'getinputslist') and hasattr(to_instance, 'getoutputslist'):
                from_inputs = from_instance.getinputslist()
                to_outputs = to_instance.getoutputslist()
                if from_inputs is None or to_outputs is None:
                    return

                # Add connections based on common inputs and outputs. The equality of two variables is based on the 'StatusVariable' attribute
                class Element:
                    def __init__(self, v):
                        self.v = v
                        if len(self.v) < 2 or 'StatusVariable' not in self.v[1]:
                            raise Exception('Variable ' + str(
                                self.v[0]) + ' does not have the StatusVariable attribute properly set')

                    def __eq__(self, other):
                        return self.v[1]['StatusVariable'] == other.v[1]['StatusVariable']

                    def __hash__(self):
                        return hash(self.v[1]['StatusVariable'])

                    def getname(self):
                        return self.v[0]

                i = [Element(myob) for myob in list(from_inputs.items())]
                o = [Element(myob) for myob in list(to_outputs.items())]

                # intersect the two lists
                common_variables = set(i) & set(o)

                if common_variables:
                    for gb in self.abstractGraphBuilders:
                        gb.addEdge(to_step, from_step, common_variables)

                # else:
                # print(f"Warning: No common inputs found between '{from_class}' and '{to_class}'.")
            else:
                print(
                    f"Warning: at least one step among '{from_step}' and '{to_step}' does not implement the required methods 'getinputslist' and 'getoutputslist'.")
            # explore the reverse connection (if it is not a self connection link)
            if selfConnection == False and reverse:
                self.add_connection(to_step, from_step, reverse=False)
        else:
            print(f"Error: Class '{from_step}' or '{to_step}' not found in the graph.")

    def display_graph(self, config_file, runMode):
        """
        Displays the input-output connections graph.

        :param config_file : path to the workflow configuration file
        :param runMode : selected runmode
        """
        print('Start displaying workflow graph using the configured graph builders')
        for gb in self.abstractGraphBuilders:
            gb.finalize(config_file,runMode)
