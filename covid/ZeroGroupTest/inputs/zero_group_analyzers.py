
from idmtools.entities import IAnalyzer

def ZeroGroupAnalyzer(IAnalyzer):
    def __init__(self, outbreak_day, sqlite_filename):
        self.outbreak_day = outbreak_day

"""
TODO: Load campaign file. Should have one RASV event, one Outbreak Individual, both targeted at Household:0 only
TODO: Load insetchart.
 Verify that Campaign Cost at end of sim == number of New Infections on first day with new infections.
 Verify that New Infections on first day == Cumulative infections on last day.
 
NOTE: If we don't have a cumulative infections channel, just make sure that the rest of new infections = 0  
"""
