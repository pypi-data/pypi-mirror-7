[default]
parser = string(default='parsers.PlainParser')
loader = string(default='loaders.PlainLoader')
using = int_list(min=2, max=2, default=None)
average = boolean(default=False)
strict = boolean(default=True)
output = string(default='contin-cd.in')

[experiment]
number = integer(min=0, default=None)
molecular_weight = float(min=0, default=None)
concentration = float(min=0, default=None)
molar_concentration = float(min=0, default=None)
length = float(min=0, default=1.0)
