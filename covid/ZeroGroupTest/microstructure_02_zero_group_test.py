"""
Using the zero group microstructure
TODO: Campaign gives RASV to everyone in household group 0 at 100% effective in environmental route (dayjob)
TODO: Campaign gives OutbreakIndividual to everyone in household group 0

Run sim

TODO: Analyzer pulls back InsetChart.json
OBSERVE: Number of infections given by OutbreakIndividual == Number of RASV interventions given
VERIFY: Total number of infections never increases after outbreak:
1. Only people infected are in zero group
2. Zero group people do not transmit in environmental route
3. Zero group people _can_ not transmit in contact route (zero group modifier)
"""