import os,sys

from hydrogeoscines.controllers.site import Site
#from hydrogeoscines.view import View

class Workflow(object):

    def __init__(self, model, view):
        self.site  = Site
        #self.view   = View