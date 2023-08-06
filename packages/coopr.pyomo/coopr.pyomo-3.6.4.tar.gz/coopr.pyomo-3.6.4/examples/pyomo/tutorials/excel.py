#
# Imports
#
from coopr.pyomo import *
import coopr.environ

##
## Using a Model
##
#
# Pyomo makes a fundamental distinction between an abstract model and a
# problem instance.  The Pyomo AbstractModel() class is used to manage the 
# declaration of model components (e.g. sets and variables), and to 
# generate a problem instance.
#
model = AbstractModel()

##
## Declaring Sets
##
#
# An unordered set of arbitrary objects
#
model.A = Set()
#
# An unordered set of numeric values
#
model.B = Set()
#
# A simple cross-product
#
model.C = model.A * model.B
#
# A simple cross-product loaded with a tabular data format
#
model.D = Set(within=model.A * model.B)
#
# A multiple cross-product
#
model.E = Set(within=model.A * model.B * model.A)

#
# An indexed set
# 
model.F = Set(model.A)
#
# An indexed set
# 
model.G = Set(model.A,model.B)
#
# A simple set
#
model.H = Set()
#
# A simple set
#
model.I = Set()
#
# A two-dimensional set
#
model.J = Set(dimen=2)

##
## Declaring Params
##
#
#
# A simple parameter
#
model.Z = Param()
#
# A single-dimension parameter
#
model.Y = Param(model.A)
#
# An example of initializing two single-dimension parameters together
#
model.X = Param(model.A)
model.W = Param(model.A)
#
# Initializing a parameter with two indices
#
model.U = Param(model.I,model.A)
model.T = Param(model.A,model.I)
#
# Initializing a parameter with missing data
#
model.S = Param(model.A)
#
# An example of initializing two single-dimension parameters together with
# an index set
#
model.R = Param(model.H, within=Reals)
model.Q = Param(model.H, within=Reals)
#
# An example of initializing parameters with a two-dimensional index set
#
model.P = Param(model.J, within=Reals)
model.PP = Param(model.J, within=Reals)
model.O = Param(model.J, within=Reals)
   
##
## Process an input file and confirm that we get appropriate 
## set instances.
##
#model.pprint()

data = ModelData(model=model)
data.add("excel.xls", range="Atable", format='set', set='A')
data.add("excel.xls", range="Btable", format='set', set='B')
data.add("excel.xls", range="Ctable", format='set', set='C')
data.add("excel.xls", range="Dtable", format='set_array', set='D')
data.add("excel.xls", range="Etable", format='set', set='E')
data.add("excel.xls", range="Itable", format='set', set='I')
data.add("excel.xls", range="Zparam", format='param', param='Z')
data.add("excel.xls", range="Ytable", index=['A'], param=['Y'])
data.add("excel.xls", range="XWtable", index=['A'], param=['X','W'])
data.add("excel.xls", range="Ttable", format='transposed_array', param='T')
data.add("excel.xls", range="Utable", format='array', param='U')
data.add("excel.xls", range="Stable", index=['A'], param=['S'])
data.add("excel.xls", range="RQtable", index_name='H', index=['H'], param=('R','Q'))
data.add("excel.xls", range="POtable", index_name='J', index=('A','B'), param=('P','O'))
data.add("excel.xls", range="PPtable", index=('A','B'), param="PP")
try:
    data.read()
except coopr.ApplicationError:
    sys.exit(0)
 
instance = model.create(data)
instance.pprint()

