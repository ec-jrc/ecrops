"""ModelLibrary package contains definitions of models (AbstractModel) and data loader (AbstractDataLoader) to be
used by the ModelLauncher (or other similar programs) to run ecrops models. The program should instantiate a model
and a data launcher: the model launches an Ecrops workflow and launches it, the data provider retrieves
the input data to feed the model.
This package also contains some implementation of model and data provider:

- EcropsWofostCGMSModel and WofostCGMSDataLoader are used for the CGMS operational system to feed and run the Wofost model (25km system using SMU/STu soil data)

- EcropsWARMCGMSModel and WARMCGMSDataLoader are used for the CGMS operational system to feed and run the WARM model (no soil data needed)

- EcropsWofostCGMSMedoidModel and WofostCGMSMedoidsDataLoader are used for the CGMS operational system to feed and run the Wofost model (10km system using ''medoids'' Soilgrids soil data)

- EcropsWofostPesetaModel and WofostPesetaDataLoader are used for the Peseta system, using Cordex grid data, to feed and run the Wofost model

- DummyModel and DummyDataLoader are trivial empty implementations to be used as template to create others
"""
