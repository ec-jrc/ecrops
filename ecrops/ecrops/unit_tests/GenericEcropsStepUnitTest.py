import xml.etree.ElementTree as ET
from ecrops import Step, ModelEngine
from ecrops.Printable import Printable
import datetime

from ecrops.waterbalance.Layer import Layer
from ecrops.wofost.Partitioning import PartioningFactors
from ecrops.wofost_util.Afgen import Afgen


class GenericEcropsStepUnitTest:
    """
    Generic unit test of an ecrops Step.
    """

    def run_test(self, xml_file):
        """
        Runs the test(s) defined in the provided xml file.
        In case a test fails, an AssertionError is raised.

        The provided xml file contains one or more test sets. A test set is composed by the inputs and the parameters needed to run the step for a particular time step (usually 1 day).
        The test set contains also the expected output variables values at the end of the execution of the time step.
        This method:
        - creates an instance of the step
        - sets the inputs and the parameters in the step
        - calls the step's setparameters method
        - calls the step's initialize method
        - calls the step's integrate method
        - calls the step's runstep method
        - checks all the outputs variables, by comparing the calculated values and the expected values. If one value does not match, an AssertionError is raised.

        Note: in the chack phase, not all the possible output types are managed. At the moment the check is performed on:
         - strings
         - numbers (by using a margin of 0.01, to avoid approximation issues)
         - dates (datetime.datetime)

        :param xml_file: the file containing the test sets
        :return: this method returns the "Ok" string if all the tests succeeded, otherwise an AssertionError is raised
        """

        # Parse the XML
        root = ET.parse(xml_file)

        stepmodule = root._root.attrib['StepModule']
        stepname = root._root.attrib['Step']
        fullStep = stepmodule + '.' + stepname

        testsets = root.findall(".//TestSets/TestSet")

        i=0
        for testset in testsets:
            parameters = {}
            inputs = {}
            outputs = {}
            i+=1
            # Extract parameters
            for param in testset.findall(".//Parameters/Parameter"):
                name = param.get("Name")
                value = parse_value(param.get("Value"))
                parameters[name] = value

            # Extract inputs
            for input_elem in testset.findall(".//Inputs/Input"):
                name = input_elem.get("Name")
                value = parse_value(input_elem.get("Value"))
                inputs[name] = value

            # Extract outputs
            for output in testset.findall(".//Outputs/Output"):
                name = output.get("Name")
                value = parse_value(output.get("Value"))
                outputs[name] = value

            status = Printable()
            status.rates = Printable()
            status.states = Printable()
            status.allparameters = {}

            #create instance
            step_instance = ModelEngine.create_instance(stepmodule, stepname)


            status.allparameters.update(parameters)

            #set input values before setparameters and initialize, because these two methods may need some of the input values
            for key, value in inputs.items():
                path = key.split('.')
                obj = status
                for part in path[1:-1]:  # exclude the first token, which is always status
                    if not hasattr(obj, part):
                        setattr(obj, part, Printable())
                    obj = getattr(obj, part)
                setattr(obj, path[-1], value)

            try:
                # set the parameters
                status = step_instance.setparameters(status)
                # initialize the model
                status = step_instance.initialize(status)
            except Exception as e:
                print('Error on initialize of class ' + stepname+' '+str(e))

            # set again the input values after the initialization, to avoid the states is full of zeros but there are the correct initial values
            for key, value in inputs.items():
                path = key.split('.')
                obj = status
                for part in path[1:-1]:  # exclude the first token, which is always status
                    if not hasattr(obj, part):
                        setattr(obj, part, Printable())
                    obj = getattr(obj, part)
                setattr(obj, path[-1], value)

            status = step_instance.integrate(status)
            status = step_instance.runstep(status)


            for key, expected_value in outputs.items():
                path = key.split('.')
                obj = status
                for part in path[1:-1]:  # exclude the first token, which is always status
                    obj = getattr(obj, part)
                try:
                    calc_value = getattr(obj, path[-1])
                    if calc_value is None and expected_value is None:#if both values are None => ok
                        continue
                    if calc_value is None and expected_value is not None:  # if calc value is none and expected value is not none => problem
                        raise Exception("Error in unit test #"+str(i)+" for step '" + fullStep + "'. Output '" + '.'.join(path) + "' has value None but should be '" + str(expected_value) + "'")
                    if type(calc_value).__name__=='deque' or isinstance(calc_value,list): #deque and lists
                        continue #TODO: check deque and list values!
                    if isinstance(calc_value, datetime.datetime) and isinstance(expected_value, datetime.datetime): #datetimes
                        assert calc_value==expected_value,"Error in unit test #"+str(i)+" for step '" + fullStep + "'. Output '" + '.'.join(path) + "' has value '" + str(calc_value) + "' but should be '" + str(expected_value) + "'"
                    else:
                        if isinstance(calc_value, str) and isinstance(expected_value, str): #strings
                            assert calc_value == expected_value, "Error in unit test #" + str(i) + " for step '" + fullStep + "'. Output '" + '.'.join(path) + "' has value '" + str(calc_value) + "' but should be '" + str(expected_value) + "'"
                        else:
                            if isinstance(calc_value, PartioningFactors) : #partitioning factors
                                continue #TODO: check PartioningFactors values!
                            else: #numeric
                                assert abs(calc_value - expected_value)<0.01, "Error in unit test #"+str(i)+" for step '" + fullStep + "'. Output '" + '.'.join(path) + "' has value '" + str(calc_value) + "' but should be '" + str(expected_value) + "'"
                except AssertionError as ae:
                    print(("Error in unit test #"+str(i)+" for step '" + fullStep + "'"))
                    raise
        print(("End of tests for step '" + fullStep + "'"))
        return "Ok"

def parse_value(value):
    """
    Auxiliary method to parse the values read from the xml files
    Managed types: lists, arrays, dictionaries, numbers (int or float), strings, dates (datetime.datetime in format '%Y-%m-%d %H:%M:%S'), 'None' string (converted to None), 'True' string (converted to True), 'False' string (converted to False)
    """
    # Attempt to evaluate the value if it looks like a list or tuple
    layer = Layer()
    af = Afgen([])
    if (value.startswith("[") and value.endswith("]"))or (value.startswith("{") and value.endswith("}")) or (value.startswith("(") and value.endswith(")")) or value.startswith("deque("):
        try:
            return eval(value)
        except:
            pass
    # Attempt to convert the value to an integer or a float or a date
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            try:
                return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except:
                if value =='None': # manage the none value
                    return None
                if value == 'True': # manage the 'True'and 'False' strings as they were booleans
                    return True
                if value == 'False':
                    return False
                return value  # Return as a string if it's not an int or float or date


if __name__ == '__main__':
    t = GenericEcropsStepUnitTest()
    """Run this script to execute the unit tests for the listed steps"""
   
    #frostkill steps
    t.run_test('frostkill\CeresRitchie_unittest_dataset_example.xml')
    t.run_test('frostkill\FROSTOL_unittest_dataset_example.xml')
    t.run_test('frostkill\WCSMModel_unittest_dataset_example.xml')

    #grassland steps
    t.run_test('grassland\Modvege1_unittest_dataset_example.xml') #this has to be fixed yet
    t.run_test('grassland\Lingra1_unittest_dataset_example.xml')

    #warm steps
    t.run_test('warm\HeatInducedSterilityWARM_unittest_dataset_example.xml')
    t.run_test('warm\ColdInducedSterilityWARM_unittest_dataset_example.xml')
    t.run_test('warm\GrowingDegreesDaysTemperature_unittest_dataset_example.xml')
    #t.run_test('warm\PotentialPhenology_unittest_dataset_example.xml')# this cannot work because the DOs cannot be correcly catch without running all the days consecutively
    t.run_test('warm\PanicleHeight_unittest_dataset_example.xml')
    t.run_test('warm\SaturationRue_unittest_dataset_example.xml')
    t.run_test('warm\SenescenceRue_unittest_dataset_example.xml')
    t.run_test('warm\TemperatureRue_unittest_dataset_example.xml')
    t.run_test('warm\ActualRue_unittest_dataset_example.xml')
    t.run_test('warm\InterceptedAbsorbedRadiation_unittest_dataset_example.xml')
    t.run_test('warm\RueBaseBiomassAccumulation_unittest_dataset_example.xml')
    t.run_test('warm\PartitioningWarm_unittest_dataset_example.xml')
    t.run_test('warm\SpecificLeafAreaWarm_unittest_dataset_example.xml')
    #t.run_test('warm\LeafLife_unittest_dataset_example.xml')#this cannot be run because at the moment we cant manage complex input data (GAIAge objects)
    t.run_test('warm\RootDepth_unittest_dataset_example.xml')
    t.run_test('warm\PotentialWaterUptake_unittest_dataset_example.xml')
    t.run_test('warm\PotentialTranspiration_unittest_dataset_example.xml')

    #wofost steps
    t.run_test('wofost\LinkWeatherToLayeredWaterBalance_unittest_dataset_example.xml')
    t.run_test('wofost\LinkWofostToLayeredWaterBalance_unittest_dataset_example.xml')
    t.run_test('wofost\EvapotranspirationPotential_unittest_dataset_example.xml')
    t.run_test('wofost\WOFOST_Leaf_Dynamics_unittest_dataset_example.xml')
    t.run_test('wofost\PlantHeight_unittest_dataset_example.xml')
    t.run_test('wofost\LinkSoilToWofost_unittest_dataset_example.xml')
    t.run_test('wofost\WOFOST_Root_Dynamics_unittest_dataset_example.xml')
    t.run_test('wofost\WaterbalanceFD_unittest_dataset_example.xml')
    t.run_test('wofost\Evapotranspiration_unittest_dataset_example.xml')
    t.run_test('wofost\Weather_unittest_dataset_example.xml')
    t.run_test('wofost\DVS_Partitioning_unittest_dataset_example.xml')
    t.run_test('wofost\LinkWeatherToWaterbalance_unittest_dataset_example.xml')
    t.run_test('wofost\LinkWeatherToWofost_unittest_dataset_example.xml')
    t.run_test('wofost\DVS_Phenology_unittest_dataset_example.xml')
    t.run_test('wofost\WOFOST_Assimilation_unittest_dataset_example.xml')
    t.run_test('wofost\WOFOST_Maintenance_Respiration_unittest_dataset_example.xml')
    t.run_test('wofost\LinkWaterbalanceToWofost_unittest_dataset_example.xml')
    t.run_test('wofost\LinkWofostToWaterbalance_unittest_dataset_example.xml')
    t.run_test('wofost\WOFOST_GrowthRespiration_unittest_dataset_example.xml')
    t.run_test('wofost\WOFOST_Stem_Dynamics_unittest_dataset_example.xml')
    t.run_test('wofost\WOFOST_Storage_Organ_Dynamics_unittest_dataset_example.xml')
    t.run_test('wofost\WaterbalanceLayered_unittest_dataset_example.xml')
    t.run_test('wofost\Vernalisation_unittest_dataset_example.xml')  # this cannot work because the DOV cannot be correcly catch without running all the days consecutively






