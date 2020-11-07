import os,sys

from hydrogeoscines.model.site import Site
from hydrogeoscines.view import View

class Controller(object):

    def __init__(self, model, view):
        self.site  = Site
        self.view   = View