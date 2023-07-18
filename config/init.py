# -*- coding: utf-8 -*-

def run():
    import matplotlib.pyplot
    
    matplotlib.pyplot.rcdefaults() #use this to change matplotlib-style-values to default
    matplotlib.pyplot.style.use(u"config/project.mplstyle")
    matplotlib.pyplot.close("all")
