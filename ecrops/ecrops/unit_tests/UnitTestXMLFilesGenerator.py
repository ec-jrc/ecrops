import xml.etree.ElementTree as ET
from ecrops import ModelEngine


class UnitTestXMLFilesGenerator():
    """Tool to generate the XML for the unit tests of the steps. The values of the variables are generated empty"""

    def generateXml(self, stepModule, stepClass):
        """
        Generates a blank (=without values) XML for the unit tests of the provided step.
        The XML is created below folder './blank_unittests/'
        The previous file will be overwritten.
        This method creates an instance of the step, calls its methods to retrieve the list of inputs, outputs, parameters, and uses these lists to create the XML
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
            parameter.set('Value', '')  # You can set default values or leave it empty

        # Add Inputs to the TestSet
        inputs = ET.SubElement(test_set, 'Inputs')
        for name, attributes in step_instance.getinputslist().items():
            input_elem = ET.SubElement(inputs, 'Input')
            input_elem.set('Name', attributes['StatusVariable'])
            input_elem.set('Value', '')  # You can set default values or leave it empty

        # Add Outputs to the TestSet
        outputs = ET.SubElement(test_set, 'Outputs')
        for name, attributes in step_instance.getoutputslist().items():
            output = ET.SubElement(outputs, 'Output')
            output.set('Name', attributes['StatusVariable'])
            output.set('Value', '')  # You can set default values or leave it empty

        # Write the XML tree to a file
        indent(root)
        tree = ET.ElementTree(root)
        tree.write('./blank_unittests/'+stepClass+'_unittest_dataset.xml', encoding='UTF-8', xml_declaration=True)

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

def round_and_string(obj, n):
    if hasattr(obj, '__round__'):
        return str(round(obj, n))
    else:
        return str(obj)

if __name__ == '__main__':
    """Run this script to generate the XML of the unit tests for the listed steps"""
    g = UnitTestXMLFilesGenerator()

    # Wofost steps
    g.generateXml('ecrops.waterbalance.LayeredWaterBalance', 'WaterbalanceLayered')
    g.generateXml('ecrops.waterbalance.LinkWofostToLayeredWaterBalance', 'LinkWofostToLayeredWaterBalance')
    g.generateXml('ecrops.waterbalance.LinkWeatherToLayeredWaterBalance', 'LinkWeatherToLayeredWaterBalance')
    g.generateXml('ecrops.wofost.PlantHeight', 'PlantHeight')
    g.generateXml('ecrops.wofost.evapotranspirationPotential','EvapotranspirationPotential')
    g.generateXml('ecrops.wofost.LinkSoilToWofost','LinkSoilToWofost')
    g.generateXml('ecrops.weather.Weather','Weather')
    g.generateXml('ecrops.wofost.LinkWeatherToWofost','LinkWeatherToWofost')
    g.generateXml('ecrops.waterbalance.LinkWaterbalanceToWofost','LinkWaterbalanceToWofost')
    g.generateXml('ecrops.wofost.vernalisation','Vernalisation')
    g.generateXml('ecrops.wofost.Phenology','DVS_Phenology')
    g.generateXml('ecrops.wofost.Partitioning','DVS_Partitioning')
    g.generateXml('ecrops.wofost.WOFOST_Assimilation','WOFOST_Assimilation')
    g.generateXml('ecrops.waterbalance.evapotranspiration','Evapotranspiration')
    g.generateXml('ecrops.wofost.maintenancerespiration','WOFOST_Maintenance_Respiration')
    g.generateXml('ecrops.wofost.growthrespiration','WOFOST_GrowthRespiration')
    g.generateXml('ecrops.wofost.stemdynamics','WOFOST_Stem_Dynamics')
    g.generateXml('ecrops.wofost.rootdynamics','WOFOST_Root_Dynamics')
    g.generateXml('ecrops.wofost.storageorgandynamics','WOFOST_Storage_Organ_Dynamics')
    g.generateXml('ecrops.wofost.leafdinamics','WOFOST_Leaf_Dynamics')
    g.generateXml('ecrops.waterbalance.LinkWeatherToWaterbalance','LinkWeatherToWaterbalance')
    g.generateXml('ecrops.waterbalance.LinkWofostToWaterbalance','LinkWofostToWaterbalance')
    g.generateXml('ecrops.waterbalance.ClassicWaterBalance','WaterbalanceFD')



    # Warm steps
    g.generateXml('ecrops.FPWarm.HeatInducedSterilityWARM','HeatInducedSterilityWARM')
    g.generateXml('ecrops.FPWarm.ColdInducedSterilityWARM','ColdInducedSterilityWARM')
    g.generateXml('ecrops.FPWarm.GrowingDegreesDaysTemperature','GrowingDegreesDaysTemperature')
    g.generateXml('ecrops.FPWarm.PotentialPhenology','PotentialPhenology')
    g.generateXml('ecrops.FPWarm.PanicleHeight','PanicleHeight')
    g.generateXml('ecrops.FPWarm.SaturationRue','SaturationRue')
    g.generateXml('ecrops.FPWarm.SenescenceRue','SenescenceRue')
    g.generateXml('ecrops.FPWarm.TemperatureRue','TemperatureRue')
    g.generateXml('ecrops.FPWarm.ActualRue','ActualRue')
    g.generateXml('ecrops.FPWarm.InterceptedAbsorbedRadiation','InterceptedAbsorbedRadiation')
    g.generateXml('ecrops.FPWarm.RueBaseBiomassAccumulation','RueBaseBiomassAccumulation')
    g.generateXml('ecrops.FPWarm.PartitioningWarm','PartitioningWarm')
    g.generateXml('ecrops.FPWarm.SpecificLeafAreaWarm','SpecificLeafAreaWarm')
    g.generateXml('ecrops.FPWarm.LeafLife','LeafLife')
    g.generateXml('ecrops.FPWarm.RootDepth','RootDepth')
    g.generateXml('ecrops.FPWarm.PotentialWaterUptake','PotentialWaterUptake')
    g.generateXml('ecrops.FPWarm.PotentialTranspiration','PotentialTranspiration')

    #grassland models steps
    g.generateXml('ecrops_grassland.modvege.modvege1', 'Modvege1')
    g.generateXml('ecrops_grassland.lingra.lingra1', 'Lingra1')

    #frostkill models steps
    g.generateXml('ritchie.CeresRitchie', 'CeresRitchie')
    g.generateXml('wcsm.WCSMModel', 'WCSMModel')
    g.generateXml('ecrops_frostol.FROSTOL', 'FROSTOL')