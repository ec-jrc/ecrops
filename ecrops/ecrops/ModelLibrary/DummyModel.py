from ecrops.ModelLibrary.AbstractModel import AbstractModel


class DummyModel(AbstractModel):
    """trivial implementation of AbstractModel"""
    def __init__(self, args=None, Name='DummyModel'):
        self.Name=Name
        self.args=args



    def runCycle(self, dailyData, dailyDataVariables, locationData, cropLocationData, soilData,  otherVariables, cropLocationDataOrder,
                 locationDataOrder, soilDataOrder,cropParameters):
        print('Dummy model RunCycle')

    def getOutputFileName(self,args):
        return "output_file_dummy_model.nc"

    def saveFinalOutput(self, data, outputFilePath):
        print('Dummy model save output file')

    def isValidLocation(self, dailyData, locationData, locationDataOrder,cropparameters,crop):
        print('Dummy model check valid location')
        return True

    def save_daily_details(self, dailydetails, add_header, daily_details_file_path, daily_details_header_file_path):
        return self.save_daily_details(dailydetails, add_header, daily_details_file_path, daily_details_header_file_path,['IDSEASON', 'CROP', 'DAY'])

    def transform_to_dekadal_and_save_dekadal_details(self, dailydetails, add_header, dekadal_details_file_path, dekadal_details_header_file_path):
        return super(DummyModel,self).transform_to_dekadal_and_save_dekadal_details(dailydetails, add_header, dekadal_details_file_path, dekadal_details_header_file_path, ['IDSEASON', 'CROP', 'DAY'])

