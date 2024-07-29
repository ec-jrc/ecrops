from ecrops.graphbuilders.AbstractGraphBuilder import AbstractGraphBuilder


class TextualGraphBuilder(AbstractGraphBuilder):
    """
    Example implementation of AbstractGraphBuilder.
    This builder writes in textual from the structure of the steps and their connections.
    In the constructor the user should provide the path to the output file. If output file is None (default behaviour) the builder prints the text to the console
    """

    def __init__(self, output_file=None):
        """
         Initialize the textual graph builder
        :param output_file: the path to the output file. If output file is None (default behaviour) the builder prints the text to the console
        """
        self.output_file = output_file

    def initialize(self):
        self.graph = {}  # Initialize an empty dictionary to store the graph

    def addStepNode(self, step_name, step_class_instance, step_parameters_dict, step_description):
        self.graph[step_name] = {"inputs": dict(), "outputs": dict(), "instance": step_class_instance,"parameters": step_parameters_dict,"description":step_description}

    def addEdge(self, to_step_name, from_step_name, common_variables):
        self.graph[to_step_name]["outputs"][from_step_name] = set()
        self.graph[to_step_name]["outputs"][from_step_name].add(' - '.join([c.getname() for c in common_variables]))
        self.graph[from_step_name]["inputs"][to_step_name] = set()
        self.graph[from_step_name]["inputs"][to_step_name].add(' - '.join([c.getname() for c in common_variables]))

    def finalize(self,config_file, runMode):
        if self.output_file is None:
            print("Input-Output Graph for workflow '"+config_file+"' (runmode '"+runMode+"'):")
            for class_name, s in self.graph.items():
                print(f"Step:{class_name}:")
                print(f"Description:{s['description']}:")
                print(f"  Parameters: {', '.join(str(k[0]) + ' ' + str(k[1]) for k in s['parameters'].items())}")
                print(f"  Inputs: {', '.join(str(k[0]) + ' ' + str(k[1]) for k in s['inputs'].items())}")
                print(f"  Outputs: {', '.join(str(k[0]) + ' ' + str(k[1]) for k in s['outputs'].items())}")
                print()
        else:
            with open(self.output_file, "w", encoding="utf-8") as text_file:
                text_file.write("Input-Output Graph for workflow '"+config_file+"' (runmode '"+runMode+"'):")
                for class_name, s in self.graph.items():
                    text_file.write(f"Step:{class_name}:")
                    text_file.write(f"Description:{s['description']}:")
                    text_file.write(f"  Parameters: {', '.join(str(k[0]) + ' ' + str(k[1]) for k in s['parameters'].items())}")
                    text_file.write(f"  Inputs: {', '.join(str(k[0]) + ' ' + str(k[1]) for k in s['inputs'].items())}")
                    text_file.write(f"  Outputs: {', '.join(str(k[0]) + ' ' + str(k[1]) for k in s['outputs'].items())}")
                    text_file.write("")


