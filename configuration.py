# -----------------------------------------------------------------------
# configuration.py
# Author: Hari Raval
# -----------------------------------------------------------------------


# a configuration object represents the inputs provided to a
class Configuration(object):

    # constructor of the Course Object
    def __init__(self, timeout, workgroups, threads_per_workgroup):
        self._timeout = timeout
        self._workgroups = workgroups
        self._threads_per_workgroup = threads_per_workgroup

    # getter method to retrieve the timeout
    def get_timeout(self):
        return self._timeout

    # getter method to retrieve the number of workgroups
    def get_number_of_workgroups(self):
        return self._workgroups

    # getter method to retrieve the number of threads per workgroup
    def get_threads_per_workgroup(self):
        return self._threads_per_workgroup
