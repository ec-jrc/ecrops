import xml.etree.ElementTree as ET
from ecrops import ModelEngine


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def round_and_string(obj,n):
    if hasattr(obj, '__round__'):
        return str(round(obj,n))
    else:
        return str(obj)

class UnitTestXMLFilesGeneratorWithValues():
    """Tool to generate the XML for the unit tests of the steps. This version of the tool creates an XML that could be used to capture the values of the variables during a run, and so helps in generating an XML with the variables values inside"""



    def generateXmlWithValues(self, stepModule, stepClass):
        """
        Generates a blank (=without values) XML for the unit tests of the provided step.
        The XML is created below folder './blank_unittests/'
        The previous file will be overwritten.
        The methods creates an instance of the step, calls its methods to retrieve the list of inputs, outputs, parameters, and uses these lists to create the XML
        """

        #create an instance of the step to retrieve its inputs, outputs and parameters from the steps' methods
        step_instance = ModelEngine.create_instance(stepModule, stepClass)

        # Create the root element
        root = ET.Element('UnitTest')
        root.set('Step', stepClass)
        root.set('StepModule', stepModule)

        # Create the TestSets element
        test_sets = ET.SubElement(root, 'TestSets')

        # Create a TestSet element
        test_set = ET.SubElement(test_sets, 'TestSet')
        test_set.set('Description', '')

        # Add Parameters to the TestSet
        parameters = ET.SubElement(test_set, 'Parameters')
        for name, attributes in step_instance.getparameterslist().items():
            parameter = ET.SubElement(parameters, 'Parameter')
            parameter.set('Name', name)
            parameter.set('Value', 'p.'+name)  # You can set default values or leave it empty

        # Add Inputs to the TestSet
        inputs = ET.SubElement(test_set, 'Inputs')
        for name, attributes in step_instance.getinputslist().items():
            input_elem = ET.SubElement(inputs, 'Input')
            input_elem.set('Name', attributes['StatusVariable'])
            input_elem.set('Value',attributes['StatusVariable'])  # You can set default values or leave it empty

        # Add Outputs to the TestSet
        outputs = ET.SubElement(test_set, 'Outputs')
        for name, attributes in step_instance.getoutputslist().items():
            output = ET.SubElement(outputs, 'Output')
            output.set('Name', attributes['StatusVariable'])
            output.set('Value', attributes['StatusVariable'])  # You can set default values or leave it empty

        # Write the XML tree to a file

        tree = ET.ElementTree(root)
        tree.write('./blank_unittests/'+stepClass+'_unittest_dataset_values.xml', encoding='UTF-8', xml_declaration=False)
        reader = open('./blank_unittests/'+stepClass+'_unittest_dataset_values.xml','r')
        try:

            l = reader.read()
            l = l.replace("\"", "\\\"")
            import re
            # Use a regular expression to find the Outputs section and replace the values
            l = re.sub(
                r'(<Outputs>.*?</Outputs>)',
                self.replace_output_values,
                l,
                flags=re.DOTALL
            )
            l = re.sub(
                r'(<Inputs>.*?</Inputs>)',
                self.replace_input_values,
                l,
                flags=re.DOTALL
            )
            l = re.sub(
                r'(<Parameters>.*?</Parameters>)',
                self.replace_parameters_values,
                l,
                flags=re.DOTALL
            )
        #    l = l.replace("\"", "\\\"")
        #    l = l.replace("Value=\\\"","Value=\\\"\"+UnitTestXMLFilesGenerator.round_and_string(")
        #    l = l.replace("\\\" />", ",3)+\"\\\" />")

            l = "\""+l+"\""

        finally:
            reader.close()
        writer = open('X:/tmp/unittests/' + stepClass + '_unittest_dataset_values.xml', 'w')
        try:
            writer.write(l)
        finally:
            writer.close()

    # Function to replace the values in the Outputs section
    def replace_output_values(self,match):
        l = match.group(0)
        l = l.replace("Value=\\\"", "Value=\\\"\"+UnitTestXMLFilesGenerator.round_and_string(")
        l = l.replace("\\\" />", ",3)+\"\\\" />")
        return l
    def replace_input_values(self,match):
        l = match.group(0)
        l = l.replace("Value=\\\"", "Value=\\\"\"+str(")
        l = l.replace("\\\" />", ")+\"\\\" />")
        return l
    def replace_parameters_values(self,match):
        l = match.group(0)
        l = l.replace("Value=\\\"", "Value=\\\"\"+str(")
        l = l.replace("\\\" />", ")+\"\\\" />")
        return l




if __name__ == '__main__':
    g = UnitTestXMLFilesGeneratorWithValues()
    #quelli commentati son quellu gia apposto!


    #Wofost
    #g.generateXmlWithValues('ecrops.waterbalance.LayeredWaterBalance', 'WaterbalanceLayered')
    #g.generateXmlWithValues('ecrops.waterbalance.LinkWofostToLayeredWaterBalance', 'LinkWofostToLayeredWaterBalance')
    #g.generateXmlWithValues('ecrops.waterbalance.LinkWeatherToLayeredWaterBalance', 'LinkWeatherToLayeredWaterBalance')
    #g.generateXmlWithValues('ecrops.wofost.PlantHeight', 'PlantHeight')
    #g.generateXmlWithValues('ecrops.wofost.evapotranspirationPotential','EvapotranspirationPotential')
    #g.generateXmlWithValues('ecrops.wofost.LinkSoilToWofost','LinkSoilToWofost')
    #g.generateXmlWithValues('ecrops.weather.Weather','Weather')
    #g.generateXmlWithValues('ecrops.wofost.LinkWeatherToWofost','LinkWeatherToWofost')
    #g.generateXmlWithValues('ecrops.waterbalance.LinkWaterbalanceToWofost','LinkWaterbalanceToWofost')
    #g.generateXmlWithValues('ecrops.wofost.vernalisation','Vernalisation')
    #g.generateXmlWithValues('ecrops.wofost.Phenology','DVS_Phenology')
    #g.generateXmlWithValues('ecrops.wofost.Partitioning','DVS_Partitioning')
    #g.generateXmlWithValues('ecrops.wofost.WOFOST_Assimilation','WOFOST_Assimilation')
    #g.generateXmlWithValues('ecrops.waterbalance.evapotranspiration','Evapotranspiration')
    #g.generateXmlWithValues('ecrops.wofost.maintenancerespiration','WOFOST_Maintenance_Respiration')
    #g.generateXmlWithValues('ecrops.wofost.growthrespiration','WOFOST_GrowthRespiration')
    #g.generateXmlWithValues('ecrops.wofost.stemdynamics','WOFOST_Stem_Dynamics')
    #g.generateXmlWithValues('ecrops.wofost.rootdynamics','WOFOST_Root_Dynamics')
    #g.generateXmlWithValues('ecrops.wofost.storageorgandynamics','WOFOST_Storage_Organ_Dynamics')
    #g.generateXmlWithValues('ecrops.wofost.leafdinamics','WOFOST_Leaf_Dynamics')
    #g.generateXmlWithValues('ecrops.waterbalance.LinkWeatherToWaterbalance','LinkWeatherToWaterbalance')
    #g.generateXmlWithValues('ecrops.waterbalance.LinkWofostToWaterbalance','LinkWofostToWaterbalance')
    #g.generateXmlWithValues('ecrops.waterbalance.ClassicWaterBalance','WaterbalanceFD')

    #Warm
    #g.generateXmlWithValues('blast.Blast','Blast')
    #g.generateXmlWithValues('ecrops.FPWarm.HeatInducedSterilityWARM','HeatInducedSterilityWARM')
    #g.generateXmlWithValues('ecrops.FPWarm.ColdInducedSterilityWARM','ColdInducedSterilityWARM')
    #g.generateXmlWithValues('ecrops.FPWarm.GrowingDegreesDaysTemperature','GrowingDegreesDaysTemperature')
    #g.generateXmlWithValues('ecrops.FPWarm.PotentialPhenology','PotentialPhenology')
    #g.generateXmlWithValues('ecrops.FPWarm.PanicleHeight','PanicleHeight')
    #g.generateXmlWithValues('ecrops.FPWarm.SaturationRue','SaturationRue')
    #g.generateXmlWithValues('ecrops.FPWarm.SenescenceRue','SenescenceRue')
    #g.generateXmlWithValues('ecrops.FPWarm.TemperatureRue','TemperatureRue')
    #g.generateXmlWithValues('ecrops.FPWarm.ActualRue','ActualRue')
    #g.generateXmlWithValues('ecrops.FPWarm.InterceptedAbsorbedRadiation','InterceptedAbsorbedRadiation')
    #g.generateXmlWithValues('ecrops.FPWarm.RueBaseBiomassAccumulation','RueBaseBiomassAccumulation')
    #g.generateXmlWithValues('ecrops.FPWarm.PartitioningWarm','PartitioningWarm')
    #g.generateXmlWithValues('ecrops.FPWarm.SpecificLeafAreaWarm','SpecificLeafAreaWarm')
    #g.generateXmlWithValues('ecrops.FPWarm.LeafLife','LeafLife')
    #g.generateXmlWithValues('ecrops.FPWarm.RootDepth','RootDepth')
    #g.generateXmlWithValues('ecrops.FPWarm.PotentialWaterUptake','PotentialWaterUptake')
    #g.generateXmlWithValues('ecrops.FPWarm.PotentialTranspiration','PotentialTranspiration')

    #grassland
    #g.generateXmlWithValues('ecrops_grassland.modvege.modvege1', 'Modvege1')
    #g.generateXmlWithValues('ecrops_grassland.lingra.lingra1', 'Lingra1')

    #frostkill
    #g.generateXmlWithValues('ritchie.CeresRitchie', 'CeresRitchie')
    #g.generateXmlWithValues('wcsm.WCSMModel', 'WCSMModel')
    #g.generateXmlWithValues('ecrops_frostol.FROSTOL', 'FROSTOL')


