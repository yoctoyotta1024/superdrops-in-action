"""
Copyright (c) 2025 MPI-M, Clara Bayley

----- Microphysics Test Cases -----
File: output_thermodynamics.py
Project: thermo
Created Date: Thursday 29th February 2024
Author: Clara Bayley (CB)
Additional Contributors:
-----
Last Modified: Monday 2nd September 2024
Modified By: CB
-----
License: BSD 3-Clause "New" or "Revised" License
https://opensource.org/licenses/BSD-3-Clause
-----
File Description:
class for storing thermodynamics output during model run
"""

import numpy as np

from .thermodynamics import Thermodynamics


class OutputVariable:
    """Class to output a variable with some of its metadata.

    Attributes:
        name (string):
          Name of variable.
        units (string):
          Units of variable.
        values (np.ndarray):
          Values of variable; must be able to be appended to.
    """

    def __init__(self, name, units, shape):
        """Initialise OutputVariable instance

        Parameters:
          name (string):
            Name of variable.
          units (string):
            Units of variable.
          shape (array of integers)
            Shape of final array. Note that values are added by write function
            as slices along first dimension (e.g. first dimension is time)
        """

        self.name = name
        self.units = units
        self.values = np.zeros(shape)
        self._i = 0

    def write(self, val):
        """Copy values 'val' to the array in slice along its first dimension.

        Parameters:
          val (any): Value(s) to append.
        """
        assert np.shape(self.values)[0] > self._i, "no space left in array"
        assert (
            np.shape(val) == np.shape(self.values)[1:]
        ), "values to add must be complete slice along 0th dimension"
        self.values[self._i] = val
        self._i += 1

    def set(self, val):
        """Copy values 'val' to the entire array.

        Parameters:
          val (any): Value(s) of array.
        """
        self.values = val
        self._i = np.nan  # destroy ability of write() function

    def finalize(self):
        """Convert values to a NumPy array."""
        print(self.name + " shape: " + str(self.values.shape))


class OutputThermodynamics:
    """Class is method and store for thermodynamic variables output during model timestep.

    Thermodynamic variables include pressure, temperature, moist air density and the specific
    content (mass mixing ratio) of vapour and condensates.

    Attributes:
        time (OutputVariable):
          time (s).
        temp (OutputVariable):
          Temperature (K).
        rhod (OutputVariable):
          Density of dry air (kg/m3).
        press (OutputVariable):
          Pressure (Pa).
        qvap (OutputVariable):
          Specific water vapor content (kg/kg).
        qcond (OutputVariable):
          Specific cloud water content (kg/kg).
        qice (OutputVariable):
          Specific cloud ice content (kg/kg).
        qrain (OutputVariable):
          Specific rain content (kg/kg).
        qsnow (OutputVariable):
          Specific snow content kg/kg).
        qgrau (OutputVariable):
          Specific graupel content (kg/kg).
    """

    def __init__(self, shape, zhalf=None, xhalf=None, yhalf=None):
        """Initialize an OutputThermodynamics object.

        Args:
            shape (tuple): Shape of the output variables, time is first dimension.
            zhalf (np.ndarray, optional): Half-level z-coordinates (m). Defaults to None.
            xhalf (np.ndarray, optional): Half-level x-coordinates (m). Defaults to None.
            yhalf (np.ndarray, optional): Half-level y-coordinates (m). Defaults to None.
        """

        self.time = OutputVariable("time", "s", [shape[0]])
        self.temp = OutputVariable("temp", "K", shape)
        self.rhod = OutputVariable("rhod", "kg m-3", shape)
        self.press = OutputVariable("press", "Pa", shape)
        self.qvap = OutputVariable("qvap", "kg/kg", shape)
        self.qcond = OutputVariable("qcond", "kg/kg", shape)
        self.qice = OutputVariable("qice", "kg/kg", shape)
        self.qrain = OutputVariable("qrain", "kg/kg", shape)
        self.qsnow = OutputVariable("qsnow", "kg/kg", shape)
        self.qgrau = OutputVariable("qgrau", "kg/kg", shape)

        if zhalf is not None:
            self.zhalf = OutputVariable("zhalf", "m", [len(zhalf)])
            self.zhalf.set(zhalf)
        else:
            self.zhalf = None

        if xhalf is not None:
            self.xhalf = OutputVariable("xhalf", "m", [len(xhalf)])
            self.xhalf.set(xhalf)
        else:
            self.xhalf = None

        if yhalf is not None:
            self.yhalf = OutputVariable("yhalf", "m", [len(yhalf)])
            self.yhalf.set(yhalf)
        else:
            self.yhalf = None

    def output_thermodynamics(self, time: float, thermo: Thermodynamics):
        """output thermodynamics from thermo to each variable in thermodynamics output.

        This method writes time and thermodynamic variables from thermo such as temperature, density,
        pressure, and specific mass mixing ratios to the respective output variables.

        Parameters:
            time (float):
              The time at which the thermodynamic variables are output (s).
            thermo (Thermodynamics):
              An instance of the Thermodynamics class containing the thermodynamic variables to output.

        Returns:
            None
        """
        self.time.write(time)
        self.temp.write(thermo.temp)
        self.rhod.write(thermo.rhod)
        self.press.write(thermo.press)
        self.qvap.write(thermo.massmix_ratios["qvap"])
        self.qcond.write(thermo.massmix_ratios["qcond"])
        self.qice.write(thermo.massmix_ratios["qice"])
        self.qrain.write(thermo.massmix_ratios["qrain"])
        self.qsnow.write(thermo.massmix_ratios["qsnow"])
        self.qgrau.write(thermo.massmix_ratios["qgrau"])

    def __call__(self, time: float, thermo: Thermodynamics):
        """Invoke the object as a function to call the `output_thermodynamics` method.

        Parameters:
            time (float):
              The time at which the thermodynamic variables are output (s).
            thermo (Thermodynamics):
              An instance of the Thermodynamics class containing the thermodynamic variables to output.

        Returns:
            None
        """
        self.output_thermodynamics(time, thermo)

    def __getitem__(self, key):
        """
        Get the value of an attribute by its name using bracket notation.

        Parameters:
            key (str): The name of the attribute to access.

        Returns:
            object: The value of the attribute if it exists, otherwise None.
        """
        return getattr(self, key, None)

    def finalize(self):
        """Finalize the thermodynamics output.

        This method finalizes the output of thermodynamic variables by calling the `finalize` method
        of each output variable, e.g. to ensure that all variables are properly formatted
        for further use or analysis.

        Returns:
            None
        """
        self.time.finalize()
        self.temp.finalize()
        self.rhod.finalize()
        self.press.finalize()
        self.qvap.finalize()
        self.qcond.finalize()
        self.qice.finalize()
        self.qrain.finalize()
        self.qsnow.finalize()
        self.qgrau.finalize()

        if self.zhalf is not None:
            self.zhalf.finalize()
        if self.xhalf is not None:
            self.xhalf.finalize()
        if self.yhalf is not None:
            self.yhalf.finalize()
