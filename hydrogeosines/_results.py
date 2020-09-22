import numpy as np
import datetime as dt
import pandas as pd
import inspect
import re
import pytz

from . import _time
from . import _series

from . import _const
const = _const.const

# the modelling class
class results(pd.DataFrame, _time.time, _series.series):
    def __init__(self, *args, **kwargs):
        # use the __init__ method from DataFrame to ensure
        # that we're inheriting the correct behavior
        super(results, self).__init__(*args, **kwargs)
    
    # this method is makes it so our methods return an instance
    # of ExtendedDataFrame, instead of a regular DataFrame
    @property
    def _constructor(self):
        return results
    