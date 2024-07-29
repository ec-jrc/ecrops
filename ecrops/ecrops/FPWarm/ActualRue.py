from ecrops.Step import Step

class ActualRue(Step):
    """
    Actual Rue
    """

    def setparameters(self, container):
        container.WarmParameters.MaximumRadiationUseEfficiency = container.allparameters['MaximumRadiationUseEfficiency']

        return container

    def initialize(self, container):
        container.states.RUEActual=0
        return container

    def integrate(self, container):
        s = container.states  # states
        r = container.rates  # rates

        return container

    def getparameterslist(self):
        return {
            "MaximumRadiationUseEfficiency": {"Description": "MaximumRadiationUseEfficiency", "Type": "Number",
                                              "Mandatory": "True", "UnitOfMeasure": "kg MJ-1"},
        }

    def getinputslist(self):
        return {

            "RUESaturationEffectRate": {"Description": "RUE Saturation Effect Rate", "Type": "Number", "UnitOfMeasure": "",
                    "StatusVariable": "status.rates.RUESaturationEffectRate"},
            "RUESenescenceEffectRate": {"Description": "RUE Senescence Effect Rate", "Type": "Number",
                                        "UnitOfMeasure": "",
                                        "StatusVariable": "status.rates.RUESenescenceEffectRate"},
            "RUETemperatureEffectRate": {"Description": "RUE Temperature Effect Rate", "Type": "Number",
                                        "UnitOfMeasure": "",
                                        "StatusVariable": "status.rates.RUETemperatureEffectRate"},


            "DevelopmentStageCode": {"Description": "Development stage", "Type": "Number", "UnitOfMeasure": "unitless",
                    "StatusVariable": "status.states.DevelopmentStageCode"},

            "UseSaturation": {"Description": "Booelan to use the saturation effect on RUE", "Type": "Boolean", "UnitOfMeasure": "unitless",
                                     "StatusVariable": "status.UseSaturation"},
            "UseSenescence": {"Description": "Booelan to use the senescence effect on RUE", "Type": "Boolean",
                              "UnitOfMeasure": "unitless",
                              "StatusVariable": "status.UseSenescence"},
            "UseTemperature": {"Description": "Booelan to use the temperature effect on RUE", "Type": "Boolean",
                              "UnitOfMeasure": "unitless",
                              "StatusVariable": "status.UseTemperature"},
            "UseCO2": {"Description": "Booelan to use the co2 effect on RUE", "Type": "Boolean",
                               "UnitOfMeasure": "unitless",
                               "StatusVariable": "status.UseCO2"},
            "GrowthRatioCO2": {"Description": "Growth on RUE due to CO2 concentration", "Type": "Number",
                               "UnitOfMeasure": "unitless",
                               "StatusVariable": "status.auxiliary.GrowthRatioCO2"},


        }

    def getoutputslist(self):
        return {
            "RUEActualRate": {"Description": "RUE Actual Rate", "Type": "Number",
                                         "UnitOfMeasure": "",
                                         "StatusVariable": "status.rates.RUEActualRate"},
            "RUEActual": {"Description": "RUE Actual", "Type": "Number",
                              "UnitOfMeasure": "",
                              "StatusVariable": "status.states.RUEActual"},

        }

    def runstep(self, container):
        """

        """

        try:

            p = container.WarmParameters  # parameters
            s = container.states  # states
            r = container.rates  # rates
            a = container.auxiliary

            if (s.DevelopmentStageCode >= 1 and s.DevelopmentStageCode <= 3):
                if (container.UseSaturation == True and
                        container.UseSenescence == True and
                        container.UseTemperature == True):  # 1
                    r.RUEActualRate = p.MaximumRadiationUseEfficiency * r.RUESaturationEffectRate * \
                                      r.RUESenescenceEffectRate * r.RUETemperatureEffectRate

                else:
                    if (container.UseSaturation == True and
                            container.UseSenescence == True and
                            container.UseTemperature == False):  # 2
                        r.RUEActualRate = p.MaximumRadiationUseEfficiency * r.RUESaturationEffectRate * r.RUESenescenceEffectRate

                    else:
                        if (container.UseSaturation == True and
                                container.UseSenescence == False and
                                container.UseTemperature == True):  # 3
                            r.RUEActualRate = p.MaximumRadiationUseEfficiency * r.RUESaturationEffectRate * r.RUETemperatureEffectRate

                        else:
                            if (container.UseSaturation == False and
                                    container.UseSenescence == True and
                                    container.UseTemperature == True):  # 4
                                r.RUEActualRate = p.MaximumRadiationUseEfficiency * r.RUESenescenceEffectRate * r.RUETemperatureEffectRate

                            else:
                                if (container.UseSaturation == True and
                                        container.UseSenescence == False and
                                        container.UseTemperature == False):  # 5
                                    r.RUEActualRate = p.MaximumRadiationUseEfficiency * r.RUESaturationEffectRate

                                else:
                                    if (container.UseSaturation == False and
                                            container.UseSenescence == True and
                                            container.UseTemperature == False):  # 6
                                        r.RUEActualRate = p.MaximumRadiationUseEfficiency * r.RUESenescenceEffectRate

                                    else:
                                        if (container.UseSaturation == False and
                                                container.UseSenescence == False and
                                                container.UseTemperature == True):  # 7
                                            r.RUEActualRate = p.MaximumRadiationUseEfficiency * r.RUETemperatureEffectRate

                                        else:  # 8
                                            r.RUEActualRate = p.MaximumRadiationUseEfficiency

            else:
                r.RUEActualRate = 0

            if (container.UseCO2 == True):
                r.RUEActualRate = r.RUEActualRate * a.GrowthRatioCO2

            s.RUEActual += r.RUEActualRate



        except  Exception as e:
            print('Error in method runstep of class ActualRue:' + str(e))

        return container
