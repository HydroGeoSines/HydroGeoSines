import numpy as np
import datetime as dt
import pandas as pd
import inspect
import re
import pytz

from . import _time
from . import _series


# the modelling class
class results(_time.time, _series.series):
    def __init__(self, BP, GW, ET):
        self.BP = BP
        self.GW = GW
        self.ET = ET
        self.all = None
        pass
    