# Copyright 2018 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Unit tests for the :mod:`openqml_pq` devices.
"""

import unittest
import logging as log
#import inspect
#from unittest_data_provider import data_provider
from pkg_resources import iter_entry_points
from defaults import openqml as qm, BaseTest
from openqml import Device
from openqml import numpy as np
from openqml.plugins.default_qubit import DefaultQubit
import openqml_pq
import openqml_pq.expval
from openqml_pq.devices import ProjectQSimulator

#import traceback #todo: remove once we no longer capture the exception further down

log.getLogger('defaults')

class CompareWithDefaultQubitTest(BaseTest):
    """Compares the behavior of the ProjectQ plugin devices with the default qubit device.
    """
    num_subsystems = 3 #This should be as large as the largest gate/observable, but we cannot know that before instantiating the device. We thus check later that all gates/observables fit.

    devices = None
    def setUp(self):
        self.devices = [DefaultQubit(wires=self.num_subsystems), ProjectQSimulator(wires=self.num_subsystems)]
        super().setUp()

    def test_simple_circuits(self):
        """Automatically compare the behavior on simple circuits"""
        self.logTestName()

        class IgnoreOperationException(Exception):
            pass

        outputs = {}


        rnd_int_pool = np.random.randint(0, 5, 100)
        rnd_float_pool = np.random.randn(100)

        for dev in self.devices:

            # run all single operation circuits
            for operation in dev.gates:
                for observable in dev.observables:
                    print("Running device "+dev.short_name+" with a circuit consisting of a "+operation+" Operation followed by an "+observable+" Expectation")

                    @qm.qnode(dev)
                    def circuit():
                        if hasattr(qm, operation):
                            operation_class = getattr(qm, operation)
                        else:
                            operation_class = getattr(openqml_pq, operation)
                        if hasattr(qm.expval, observable):
                            observable_class = getattr(qm.expval, observable)
                        else:
                            observable_class = getattr(openqml_pq.expval, observable)

                        if operation_class.num_wires > self.num_subsystems:
                            raise IgnoreOperationException('Skipping in automatic test because the operation '+operation+" acts on more than the default number of wires "+str(self.num_subsystems)+". Maybe you want to increase that?")
                        if observable_class.num_wires > self.num_subsystems:
                            raise IgnoreOperationException('Skipping in automatic test because the observable '+observable+" acts on more than the default number of wires "+str(self.num_subsystems)+". Maybe you want to increase that?")

                        if operation_class.par_domain == 'N':
                            operation_pars = rnd_int_pool[:operation_class.num_params]
                        elif operation_class.par_domain == 'R':
                            operation_pars = np.abs(rnd_float_pool[:operation_class.num_params]) #todo: some operations/expectations fail when parameters are negative (e.g. thermal state) but par_domain is not fine grained enough to capture this
                        elif operation_class.par_domain == 'A':
                            if str(operation) == "QubitUnitary":
                                operation_pars = [np.array([[1,0],[0,-1]])]
                            elif str(operation) == "QubitStateVector":
                                random_ket = np.random.uniform(-1,1,2**self.num_subsystems)
                                random_ket = random_ket / np.linalg.norm(random_ket)
                                operation_pars = [np.array(random_ket)]
                            else:
                                raise IgnoreOperationException('Skipping in automatic test because I don\'t know how to generate parameters for the operation '+operation)
                        else:
                            operation_pars = {}

                        if observable_class.par_domain == 'N':
                            observable_pars = rnd_int_pool[:observable_class.num_params]
                        if observable_class.par_domain == 'R':
                            observable_pars = np.abs(rnd_float_pool[:observable_class.num_params]) #todo: some operations/expectations fail when parameters are negative (e.g. thermal state) but par_domain is not fine grained enough to capture this
                        elif observable_class.par_domain == 'A':
                            if str(observable) == "Hermitian":
                                observable_pars = [np.array([[1,0],[0,0]])]
                            else:
                                raise IgnoreOperationException('Skipping in automatic test because I don\'t know how to generate parameters for the observable '+observable)
                        else:
                            observable_pars = {}

                        # apply to the first wires
                        operation_wires = list(range(operation_class.num_wires)) if operation_class.num_wires > 1 else 0
                        observable_wires = list(range(observable_class.num_wires)) if observable_class.num_wires > 1 else 0

                        operation_class(*operation_pars, operation_wires)
                        return observable_class(*observable_pars, observable_wires)

                    try:
                        output = circuit()
                        if (operation, observable) not in outputs:
                            outputs[(operation, observable)] = {}

                        outputs[(operation, observable)][type(dev)] = output

                    except IgnoreOperationException as e:
                        print(e)

        #if we could run the circuit on more than one device assert that both should have given the same output
        for (key,val) in outputs.items():
            if len(val) >= 2:
                self.assertAllElementsAlmostEqual(val.values(), delta=self.tol, msg="Outputs of "+str(list(val.keys()))+" do not agree for a circuit consisting of "+str(key))


if __name__ == '__main__':
    print('Testing OpenQML ProjectQ Plugin version ' + qm.version() + ', Device class.')
    # run the tests in this file
    suite = unittest.TestSuite()
    for t in (CompareWithDefaultQubitTest, ):
        ttt = unittest.TestLoader().loadTestsFromTestCase(t)
        suite.addTests(ttt)

    unittest.TextTestRunner().run(suite)