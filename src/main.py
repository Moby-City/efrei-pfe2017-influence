#!/usr/bin/env python3
import datasource/lefigaro
import datasource/carenews
import datasource/cnews_matin
import datasource/ulule

import sys

search_term = sys.argv[-1]

DataSourceLeFigaro().findAllFor(search_term)
DataSourceCNewsMatin().findAllFor(search_term)

#DataSourceUlule().findAll()
#DataSourceCarenews().findAll()
