""" Class ModelEngine and its utility classes """
import importlib
import json
import sys
import traceback
from datetime import timedelta
import datetime  # do not remove!
from xml.dom import minidom
import numpy as np
import pickle
from ecrops.Printable import Printable
import time

class ModelEngine:
    """
    This class is the engine of the ecrops model.

    Class to implement the engine workflow: when the instance of this class is created, the configuration is read
    from the provided configuration file. The reading of the workflow file is done at the beginning of the workflow,
    since that files defines the structure of the model execution in terms of steps to execute, input data and output
    variables. The configuration file contains:
    - the declarations of the driving variables (= all the inputs except
    the model parameters). All the driving variables declared are mandatory to run the model. (property drivingVariables)
    - the instructions to initialize the status variables  (property initVariables) - the steps to run (property Workflows)
    - the variables to return as output (property Workflows)


    The simulation cycle is divided in 3 parts: - initialize method checks the driving variables are present,
    initializes the status variable from the property initVariables and the provided input data - executeStep method
    performs the simulation by calling the steps in the correct order for every day in the cycle. For every day
    between simulation_start_day and simulation_end_day, if requested, populates a dailydetails array with the daily
    value of the output variables - finalize method returns an array with output variables calculated after the last
    time interval executed

    The model’s status and variables are all contained in a variable called “status”, which is modified by every
    model method. The status variable is NOT contained in the ModelEngine class: it is created by the initialize
    method and returned to the caller. The status is a required input of both executeStep and finalize methods. Every
    call to the executeStep method updates the status with the variable values calculated inside the step. It is duty
    of the caller to manage the status variable properly. This approach allow the caller to have a full control of
    the status variable to perform specific tasks.

    Here the generic workflow of the caller:

    model = ModelEngine(config_file)
    status=model.initialize(timedependantvariables, drivingVariables, allparameters, first_day, simulation_start_day,
                   simulation_end_day)
    for simulation cycle:
        status=model.executeStep(status)
    result=model.finalize(status)

    The reading of the workflow is done in the constructor method of the ModelEngine class. Example: model =
    ModelEngine(“my_workflow_file.xml”) The workflow can be executed on more than one “run mode”. A “run mode”
    defines the steps to execute and can be used when the same model should be executed in slightly different ways,
    as, for example, adding or not adding a specific step.
    """

    Workflows = None
    """This object, once configured in the class constructor, contains the elements of the simulation: the list of 
    active workflows and, for each of them, the list of steps to run and the variables to returns as output """

    XmlWorkflowConfig = ''
    """ XML Configuration file """

    initVariables = None
    """ Variable initialization configuration """

    drivingVariables = None
    """ Driving variables declaration configuration """

    PrintDailyDetails = False
    """boolean property used to trigger the print to console of the daily status variables. Set it to true to print 
    the daily values of all the output columns (defined in the configuration file) """

    ReturnDailyDetails = False
    """boolean property  used to add the daily details dictionary in the status variable, so that it can be retrieved 
    at the end of the simulation. Set it to true to save the daily value of each of the output columns (defined in 
    the configuration file) in a dictionary: status.dailydetails """

    def __init__(self, config_file):
        """Constructor: sets the path of the workflow configuration file, reads the file and populates the properties
        Workflows, drivingVariables and initVariables
        """
        self.XmlWorkflowConfig = config_file
        self.readWorkflowConfigurationFromXML()
        d = datetime.datetime(1999,1,1)# do not remove!

    debug_timing_mode = False  # set to true to enable component time tracing
    debug_timing_runstep_time = {}
    debug_timing_initialize_time = {}
    debug_timing_integrate_time = {}

    def getParametersList(self):
        """
        Collect the parameters of all the steps
        """
        allTheParameters = {}
        for workflow in self.Workflows:
            for step in workflow.steps:
                stepParameters = step.getparameterslist()
                for parameter in stepParameters:
                    classParts = str(step.__class__).split('.')
                    className = classParts[len(classParts) - 1]
                    if not (className in allTheParameters):  # dubbio se usare step.__module__ o step.__name__ ???
                        allTheParameters[className] = {}
                    if not (parameter in allTheParameters[className]):
                        allTheParameters[className][parameter] = stepParameters[parameter]
        return allTheParameters

    def getParametersListAsJson(self):
        """
        Collects the parameters of all the steps and return them as a JSON file
        """
        allTheParameters = self.getParametersList()
        return json.dumps(allTheParameters)

    def initialize(self, timedependantvariables, timeDependantVariableColumn, drivingVariables, allparameters, first_day, simulation_start_day,
                   simulation_end_day):
        """
        It checks that all the DrivingVariables defined in the configuration file are set. In case one is missing an
        exception is thrown.

        Initializes the status variable, by using all the inputs defined in the “Init” section of the workflow file,
        and reading values from the six arguments.

        For example, if in the “Init” section is present this line
        <Variable    name="LAT" source="drivingVariables['LAT']" />
        then the engine executes this line of code
        status.LAT=drivingVariables['LAT']
        so it instantiates a new variable called "LAT" in “status” and sets its
        value to the result of the execution of the instruction “drivingVariables['LAT']” (drivingVariables is one of
        the arguments of the “initialize” method).
        Arguments:
        timedependantvariables: contains all the time dependant variables (e.g. weather data)
        timeDependantVariableColumn: contains the position in the array of the timedependantvariables
        drivingVariables: contains all the driving variables (e.g. the year and the crop to simulate, the soil data,...)
        allparameters: contains the model's parameters
        first_day: first value for status.day variable
        simulation_start_day: the simulation of the steps is performed only when simulation_start_day >= status.day
        simulation_end_day: the simulation of the steps is performed only when simulation_start_day <= status.day


        Returns the status variable.
        """

        status = Printable()
        status.model_initialized = False
        status.day = first_day
        status.first_day = first_day
        status.simulation_start_day = simulation_start_day
        status.simulation_end_day = simulation_end_day

        #verify all the driving variables are present
        if self.drivingVariables is not None:
            for dVar in self.drivingVariables:
                if dVar.name not in drivingVariables:
                    msg="Error during ModelEngine initialization. Driving variable '" + dVar.name + "' not found!. "
                    print(msg)
                    traceback.print_exc(limit=20, file=sys.stdout)
                    raise Exception(msg)

        command = None
        try:
            # year = int(drivingVariables['YEAR'])
            for iVar in self.initVariables:
                # execute a line code that will define a new variable
                command = 'status.' + iVar.name + " = " + iVar.source.replace('&gt;', '>').replace('&lt;', '<')
                exec(command)

        except ValueError as exc:
            print((
                    "\nError executing the ModelEngine initialization. Error executing command '" + command + "' . "
                                                                                                              "Error:" + str(
                exc)))
            traceback.print_exc(limit=20, file=sys.stdout)
        except TypeError as exc:
            print((
                    "\nError executing the ModelEngine initialization. Error executing command '" + command + "' . "
                                                                                                              "Error:" + str(
                exc)))
            traceback.print_exc(limit=20, file=sys.stdout)
        except KeyError as exc:
            print((
                    "\nError executing the ModelEngine initialization. Error executing command '" + command + "' . "
                                                                                                              "Error:" + str(
                exc)))
            traceback.print_exc(limit=20, file=sys.stdout)
        except IndexError as exc:
            print((
                    "\nError executing the ModelEngine initialization. Error executing command '" + command + "' . "
                                                                                                              "Error:" + str(
                exc)))
            traceback.print_exc(limit=20, file=sys.stdout)
        except Exception as exc:
            print((
                    "\nError executing the ModelEngine initialization. Error executing command '" + command + "' . "
                                                                                                              "Error:" + str(
                exc)))
            traceback.print_exc(limit=20, file=sys.stdout)

        return status



    def executeStep(self, status, runMode):
        """
        Runs all steps for specific run mode, in the defined order, for every value of status.day property when
        status.simulation_start_day <= status.day <= status.simulation_end_day.
        status.day is incremented by 1 day at the end of the method.
        For every step, the “status” variable is set as an input of the step, is updated by the step and returned to the engine.

        Arguments:
        status: the status of the model
        runMode: the current run mode
        returns: the updated status of the model

        """
        try:
            components = self.getSteps2Run(runMode)

            # only the first day
            if status.simulation_start_day == status.day:
                for c in components:
                    c.setparameters(status)
                    status.model_initialized=True
                    if self.debug_timing_mode:
                        self.debug_timing_initialize_time[str(c.__class__.__name__)] = 0
                        self.debug_timing_integrate_time[str(c.__class__.__name__)] = 0
                        self.debug_timing_runstep_time[str(c.__class__.__name__)] = 0
                for c in components:
                    if self.debug_timing_mode:
                        starttimeinitialize=time.time()
                    status = c.initialize(status)
                    if self.debug_timing_mode:
                        self.debug_timing_initialize_time[str(c.__class__.__name__)]+=time.time()-starttimeinitialize


            # run steps from start to end day
            if status.simulation_start_day <= status.day <= status.simulation_end_day:
                for c in components:
                    if status.simulation_start_day != status.day:  # at start day execute only the run step, without integration
                        if self.debug_timing_mode:
                            starttimeintegratte = time.time()
                        if status.model_initialized==False:
                            raise Exception('model was not initialized. Please check the model start conditions')
                        status = c.integrate(status)
                        if self.debug_timing_mode:
                            self.debug_timing_integrate_time[str(c.__class__.__name__)] += time.time() - starttimeintegratte

                for c in components:
                    if self.debug_timing_mode:
                        starttimerunstep = time.time()
                    status = c.runstep(status)
                    if self.debug_timing_mode:
                        self.debug_timing_runstep_time[str(c.__class__.__name__)] += time.time() - starttimerunstep

            # if flags ReturnDailyDetails or PrintDailyDetails are set to true, at the first day initialize the structure to contain the daily values (status.dailydetails)
            if (self.ReturnDailyDetails or self.PrintDailyDetails) and status.simulation_start_day == status.day:

                if hasattr(status, 'dailydetails') == False:
                    status.dailydetails = {}

                # in the dailydetails, always add DAY and DOY column and then all the output columns defined in the configuration file
                for col in ['DAY', 'DOY'] + self.getOutputVariablesNames(runMode):
                    # initialize each column as an empy list. The list will contain a value for each day
                    status.dailydetails[col] = []

            # if flags ReturnDailyDetails or PrintDailyDetails are set to true, at the end of the daily step collect the ouput variables values
            # into the status.dailydetails dictionary (besides the output variables, add always also columns DAY (=complete date) and DOY (=julian day) )
            if (self.ReturnDailyDetails or self.PrintDailyDetails) and status.simulation_start_day <= status.day:

                # in the dailydetails, always add DAY and DOY column
                status.dailydetails['DAY'].append(status.day)
                status.dailydetails['DOY'].append(status.day.timetuple().tm_yday)

                # in the daily details, add all the output columns defined in the configuration file
                # retrieve the output variables for the specific runMode
                outVariables = self.getOutputVariables(runMode)
                i = 0

                # for each output column
                for oVar in outVariables:
                    # check if all variables levels are valid and if contains the elements
                    varParts = oVar.source.split('.')

                    # if varParts[0] is status, we use directly status because it is faster than eval
                    varValues = {}
                    if (varParts[0] == 'status'):
                        varValues[0] = status
                    else:
                        varValues[0] = eval(varParts[0])

                    progressiveVarName = varParts[0]
                    varConditions = True
                    finalValue = None
                    for p in range(1, len(varParts)):
                        if varValues[p - 1] is None:
                            finalValue = None
                            break

                        if "()" not in varParts[p]:
                            # davide: added the condition "[" in varParts[p] to manage arrays like "myvariable[3]"
                            if hasattr(varValues[p - 1], varParts[p]) or "[" in varParts[p]:
                                progressiveVarName = progressiveVarName + '.' + varParts[p]
                                # davide: if varParts[p] is in __dict__ of  varParts[p-1] we avoid the use of eval and we get the value directly from __dict__
                                if hasattr(varValues[p - 1], '__dict__') and varParts[p] in varValues[p - 1].__dict__:
                                    varValues[p] = varValues[p - 1].__dict__[varParts[p]]
                                else:
                                    varValues[p] = eval(progressiveVarName)
                                finalValue = varValues[p]
                            else:
                                varConditions = False
                                break
                        else:
                            progressiveVarName = progressiveVarName + '.' + varParts[p]
                            varValues[p] = eval(progressiveVarName)
                            finalValue = varValues[p]

                    if varConditions:
                        # append the current day value to the daily details array
                        status.dailydetails[oVar.name].append(finalValue)
                    else:
                        # if the variable is not valid, append None
                        status.dailydetails[oVar.name].append(None)

                    i = i + 1

            # get next day, using datetime
            status.day = status.day + timedelta(days=1)

            return status
        except Exception as exc:
            print(("\nError executing the ModelEngine.executeStep :" + str(exc)))
            traceback.print_exc(limit=20, file=sys.stdout)
            raise exc

    def finalize(self, status, runMode):
        """
        For the current run mode it generates an array with output variables calculated after the last time interval
        executed and returns it. To do so, it uses the output variables definition read from the workflow file.
        Arguments: status: the status of the model runMode: the current run mode returns: the array containing the
        values of the output variables, in the same order they are returned by getOutputVariables and
        getOutputVariablesNames methods
        """
        try:
            for k in self.debug_timing_initialize_time.keys():
                print( 'initialize time' + k + ' : ' + str(self.debug_timing_initialize_time[k]) + ' seconds')
            for k in self.debug_timing_integrate_time.keys():
                print( 'integrate time' + k + ' : ' + str(self.debug_timing_integrate_time[k]) + ' seconds')
            for k in self.debug_timing_runstep_time.keys():
                print( 'runstep time' + k + ' : ' + str(self.debug_timing_runstep_time[k]) + ' seconds')
            # retrieve the output variables for the specific runMode
            outVariables = self.getOutputVariables(runMode)
            if outVariables is None:
                print(('No output variables read for run mode ' + runMode))
            if len(outVariables) <= 0:
                return None

            # initialize the array to return
            to_return = np.zeros(len(outVariables))

            i = 0
            for oVar in outVariables:
                # check if all variables levels are valid and if contains the elements
                varParts = oVar.source.split('.')
                varValue = eval(varParts[0])
                varConditions = True
                progressiveVarName = varParts[0]
                for p in range(1, len(varParts)):
                    if varValue is None:
                        break

                    if "()" not in varParts[p]:
                        if hasattr(varValue, varParts[p]):
                            progressiveVarName = progressiveVarName + '.' + varParts[p]
                            varValue = eval(progressiveVarName)
                        else:
                            varConditions = False
                            break
                    else:
                        progressiveVarName = progressiveVarName + '.' + varParts[p]
                        varValue = eval(progressiveVarName)

                if varConditions == True and varValue is not None:
                    to_return[i] = varValue

                i = i + 1

            if self.PrintDailyDetails:
                print((str(list(status.dailydetails.keys()))))
                for row in range(0, len(status.dailydetails['DOY'])):
                    sys.stdout.write('\n')
                    for col in list(status.dailydetails.keys()):
                        if row < len(status.dailydetails[col]):
                            sys.stdout.write(str(status.dailydetails[col][row]) + ',')

            return to_return

        except Exception as exc:
            print(("\nError executing the ModelEngine finalize :" + str(exc)))
            traceback.print_exc(limit=20, file=sys.stdout)
            return None

    def SerializeStatus(self, status):
        """
        Serializes the status of the model, passed as argument. Returns the pickled serialized string
        """

        pickled_string = pickle.dumps(status)
        return pickled_string

    def DeserializeStatus(self, pickled_string):
        """
        Deserializes the status of the model. Returns the new status, created  from the pickled serialized string passed as argument
        """
        status = pickle.loads(pickled_string)
        return status

    def readWorkflowConfigurationFromXML(self):
        """
        Reads the workflows configuration for which the flag RUN is ON. It reads the XML configuration file with
        which the instance was created. While reading the file, it populates the elements of property Workflows,
        which, at the end of this operation, will contain the configuration to run. It also populates property initVariables,
        which,  at the end of this operation, will contain the instructions to initialize the model status.
        """
        xm = minidom.parse(self.XmlWorkflowConfig)
        xWs = xm.getElementsByTagName('Workflow')
        self.Workflows = list()

        # parse all models
        for xWk in xWs:
            wkRunnable = (xWk.attributes['run'].value == 'ON')
            if wkRunnable:
                wk = ModelEngineWorkflow()
                wk.steps = list()
                wk.name = xWk.attributes['name'].value
                xSteps = xWk.getElementsByTagName('Step')
                for xStep in xSteps:
                    stepParts = str(xStep.firstChild.nodeValue).split('|')
                    moduleParts = stepParts[0].split('.')

                    # load all modules hierarchy
                    moduleName = moduleParts[0]
                    moduleLoaded = importlib.import_module(moduleName)
                    for p in range(1, len(moduleParts)):
                        moduleName = moduleName + ('' if len(moduleName) == 0 else '.') + moduleParts[p]
                        moduleLoaded = importlib.import_module(moduleName)

                    # load the class
                    m = getattr(moduleLoaded, stepParts[1])
                    wk.steps.append(m())
                    # wk.steps.append( eval(str(xStep.firstChild.nodeValue)) () )

                # read output variables for current workflow
                xOutput = xWk.getElementsByTagName('Output')
                if len(xOutput) > 0:
                    xoVariables = xOutput[0].getElementsByTagName('Variable')
                    wk.outputVariables = list()
                    for xVar in xoVariables:
                        wkVar = OutputVariable()
                        wkVar.name = xVar.attributes['name'].value
                        wkVar.source = xVar.attributes['source'].value
                        wkVar.description = xVar.attributes['description'].value
                        wk.outputVariables.append(wkVar)

                self.Workflows.append(wk)

        # read init variables for current workflow, if exists
        xInit = xm.getElementsByTagName('Init')
        if len(xInit) > 0:
            xiVariables = xInit[0].getElementsByTagName('Variable')
            self.initVariables = list()
            for iVar in xiVariables:
                wiVar = InitVariable()
                wiVar.name = iVar.attributes['name'].value
                wiVar.source = iVar.attributes['source'].value
                self.initVariables.append(wiVar)

        # read driving variables
        xDriv = xm.getElementsByTagName('DrivingVariables')
        if len(xDriv) > 0:
            xiDrVariables = xDriv[0].getElementsByTagName('DrivingVariable')
            self.drivingVariables = list()
            for iVar in xiDrVariables:
                wiVar = DrivingVariable()
                wiVar.name = iVar.attributes['name'].value
                wiVar.description = iVar.attributes['description'].value
                wiVar.unitofmeasure = iVar.attributes['unitofmeasure'].value
                wiVar.type = iVar.attributes['type'].value
                self.drivingVariables.append(wiVar)

        return

    def getSteps2Run(self, runMode):
        """
        Retrieve the steps to run for specific run mode from the configured Workflows property
        Arguments:
            runMode: the current run mode
        Returns: The list of steps to run
        """
        for x in self.Workflows:
            if x.name == runMode:
                return x.steps
        return None

    def getOutputVariables(self, runMode):
        """
        Retrieves the output variables for specific run mode from the configured Workflows property
        Arguments:
            runMode: the current run mode
        Returns: The list of output variables as 'Variable' objects
        """
        for x in self.Workflows:
            if x.name == runMode:
                return x.outputVariables
        return None

    def getOutputVariablesNames(self, runMode):
        """
        Retrieves the output variables names for specific run mode from the configured Workflows property
        Arguments:
            runMode: the current run mode
        Returns: The list of output variables names
        """
        outputVariables = self.getOutputVariables(runMode)
        if outputVariables is None:
            return None
        return [v.name for v in outputVariables]

    def getNumberOfOutputVariables(self, runMode):
        """
        Retrieves the number of output variables for a specific run mode from the configured Workflows property
        Returns: The number of output variables names
        """
        outputVariables = self.getOutputVariables(runMode)
        return 0 if outputVariables is None else len(outputVariables)

    def getRunModeNames(self):
        """
        Returns the available run modes defined in the workflow file from the configured Workflows properties
        """
        return [w.name for w in self.Workflows]

    def getTotalNumberOfOutputVariables(self):
        """
        Retrieves the number of output variables for all run modes from the configured Workflows properties
        """
        runModes = self.getRunModeNames()
        numberOfVariables = 0
        for rm in runModes:
            numberOfVariables = numberOfVariables + self.getNumberOfOutputVariables(rm)

        return numberOfVariables

    def getOutputVariablePosition(self, runMode, variablename):
        """
        Retrieve the position of a variable among all the output variables from the configured Workflows properties
        """
        outputVariables = self.getOutputVariablesNames(runMode)
        if outputVariables is None:
            return -1
        return outputVariables.index(variablename)


class ModelEngineWorkflow:
    """
    Represents a model workflow file
    """
    name = ''
    """Name of the workflow"""

    steps = None
    """List of steps of the workflow"""

    outputVariables = None
    """List of output variables of the workflow (OutputVariable object)"""


class OutputVariable:
    """
    Represents a model output variable defined in the workflow file
    """
    name = ''
    """Name of the variable"""

    source = ''
    """Definition of the variable as used in the steps. A variable to be extracted as output should belong to property 
    'status', so the source should start with 'status' .E.g. 'status.weather.RAIN' """

    description = ''
    """Textual description of the variable"""


class DrivingVariable:
    """
    Reapresents the definition of a driving variable
    """
    name = ''
    description = ''
    unitofmeasure = ''
    type = ''

class InitVariable:
    """
    Represents a model initialization variable defined in the workflow file
    """

    name = ''
    """Name of the variable. The variable will be created as attribute of the status property using the preovided name. 
    For example is name is 'myvar', it will be created a variable status.myvar = value provided by source attribute
    """

    source = ''
    """The source represents the way the Engine can get the variable value from the input data. Input data include:
     -drivingVariables
     -timedependantvariables
     -allparameters
     -first_day
     -simulation_start_day
     -simulation_end_day
     
     e.g.
     source = drivingVariables['LAT']
     or
     source = first_day
     or 
     source = timedependantvariables
     
     Alternatively, the value of the variable can be directly written in the workflow file.
     Any valid python expression is valid as a value. 
     Examples:  source = "57" ,  source = "[]", source = "'a certain string'", 
     source = "0 if drivingVariables['DEPTH'] &lt;= 0 else drivingVariables['DEPTH'] 
     """