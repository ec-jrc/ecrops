class ActualRue:
    """
    Actual Rue
    """

    def setparameters(self, container):
        return container

    def initialize(self, container):
        return container

    def integrate(self, container):
        return container

    def getparameterslist(self):
        return {
            "MaximumRadiationUseEfficiency": {"Description": "MaximumRadiationUseEfficiency", "Type": "Number",
                                              "Mandatory": "True", "UnitOfMeasure": "kg MJ-1"},
        }

    def runstep(self, container):
        """

        """

        try:
            ex = container.Weather[(container.day - container.first_day).days]  # get the meteo data for current day
            p = container.Parameters  # parameters
            s = container.States  # states
            s1 = container.States1  # ???
            a = container.Auxiliary  # ???
            r = container.Rates  # rates

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

            s1.RUEActual = s.RUEActual + r.RUEActualRate



        except  Exception as e:
            print('Error in method runstep of class ActualRue:' + str(e))

        return container
