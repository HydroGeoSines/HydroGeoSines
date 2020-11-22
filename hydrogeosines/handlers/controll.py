import os,sys

from ..model.site import Site
from ..visualization.visualize import Visualize

class Controller(object):

    def __init__(self, model, view):
        self.site  = Site
        #self.view   = View