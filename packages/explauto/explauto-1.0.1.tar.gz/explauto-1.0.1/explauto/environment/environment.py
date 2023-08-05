from numpy import zeros, array

from abc import ABCMeta, abstractmethod

from ..utils.config import make_configuration
from ..utils.observer import Observable
from .. import ExplautoNoTestCasesError
from ..utils import rand_bounds
from ..third_party.models.models.testbed.testcase import Lattice
from ..third_party.models_adaptors import configuration



class Environment(Observable):
    """ Abstract class to define environments.

    When defining your sub-environment, you should specify whether they could be forked and run in different processes through the use_process class variable. By default, it is set to False to guarantee that the code will work.

    """
    __metaclass__ = ABCMeta
    use_process = False

    def __init__(self, m_mins, m_maxs, s_mins, s_maxs):
        """
        :param array m_mins, m_maxs, s_mins, s_maxs: bounds of the motor (m) and sensory (s) spaces

        """
        Observable.__init__(self)

        self.conf = make_configuration(m_mins, m_maxs, s_mins, s_maxs)
        self.state = zeros(self.conf.ndims)

    def update(self, ag_state, log=True):
        m = self.compute_motor_command(ag_state)
        self.state[:self.conf.m_ndims] = m

        s = self.compute_sensori_effect()
        self.state[-self.conf.s_ndims:] = s

        if log:
            self.emit('motor', m)
            self.emit('sensori', s)

    @abstractmethod
    def compute_motor_command(self, ag_state):
        pass

    @abstractmethod
    def compute_sensori_effect(self):
        pass

    def random_motors(self, n=1):
        return rand_bounds(self.conf.bounds[:, self.conf.m_dims], n)

    def dataset(self, orders):
        n = orders.shape[0]
        m_ndims = orders.shape[1]

        data = zeros((n, self.conf.ndims))
        data[:, :m_ndims] = orders

        for i, m in enumerate(orders):
            self.update(m)
            data[i, m_ndims:] = self.state[m_ndims:]

        return data

    def uniform_sensor(self, n_cases=100):
        n_random_motor = n_cases * 100
        m_feats, s_feats, m_bounds = configuration(self)
        ms_uniform_motor = self.dataset(self.random_motors(n_random_motor))
        resolution = max(2, int((1.3*n_cases)**(1.0/len(s_feats))))
        observations = []
        for ms in ms_uniform_motor:
            observations.append((ms[self.conf.m_dims], ms[self.conf.s_dims]))
        lattice = Lattice(s_feats, observations, res=resolution)
        result = []
        for ms in list(lattice.grid.values()):
            result.append(ms[1])
        return array(result)
