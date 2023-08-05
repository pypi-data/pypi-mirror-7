#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import sys
import os.path
import re

from coopr.core.plugin import alias

from coopr.pyomo.base.param import Param
from coopr.pyomo.data.TableData import TableData


class TextTable(TableData):

    alias("tab", "Manage IO with ASCI tables.")

    def __init__(self):
        TableData.__init__(self)

    def open(self):
        if self.filename is None:
            raise IOError("No filename specified")

    def close(self):
        self.FILE.close()

    def read(self):
        if not os.path.exists(self.filename):
            raise IOError("Cannot find file '%s'" % self.filename)
        self.FILE = open(self.filename, 'r')
        try:
            tmp=[]
            for line in self.FILE:
                line=line.strip()
                tokens = re.split("[\t ]+",line)
                if tokens != ['']:
                    tmp.append(tokens)
            if len(tmp) == 0:
                raise IOError("Empty *.tab file")
            elif len(tmp) == 1:
                if not self.options.param is None:
                    if type(self.options.param) in (list, tuple):
                        p = self.options.param[0]
                    else:
                        p = self.options.param
                    if isinstance(p, Param):
                        self.options.model = p.model()
                        p = p.name
                    self._info = ["param",p,":=",tmp[0][0]]
                elif len(self.options.symbol_map) == 1:
                    self._info = ["param",self.options.symbol_map[self.options.symbol_map.keys()[0]],":=",tmp[0][0]]
                else:
                    raise IOError("Data looks like a parameter, but multiple parameter names have been specified: %s" % str(self.options.symbol_map))
            else:
                self._set_data(tmp[0], tmp[1:])
        except Exception:
            # Ensure that the file is close when an exception occurs
            self.FILE.close()
            raise sys.exc_info()[1]
            
        self.FILE.close()
        return True

    def write(self, data):
        if self.options.set is None and self.options.param is None:
            raise IOError("Unspecified model component")
        self.FILE = open(self.filename, 'w')
        table = self.get_table()
        for line in table:
            self.FILE.write(' '.join(map(str, line))+'\n')
        self.FILE.close()
        return True

