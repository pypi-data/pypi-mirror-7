## ---- setup ----
require(knitr)
require(knitrBootstrap) # https://github.com/jimhester/knitrBootstrap
require(rCharts) # https://github.com/ramnathv/rCharts/
require(DESeq)
require(org.Hs.eg.db)
require(data.table)
require(plyr)
require(dplyr)
require(gdata)
require(annotate)
require(XML)
require(xtable)
require(pander)
require(KEGGREST)
require(knitcitations) # https://github.com/cboettig/knitcitations

source(paste(config$R_SOURCE_PATH, '/src/core/functions.R', sep=''))

cite_options(tooltip=TRUE) # use bootstrap to create mouse over citations