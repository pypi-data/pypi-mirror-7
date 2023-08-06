## ---- brcaMolClassData ----
require(pamr)

load(paste(config$R_SOURCE_PATH, '/data/brca_mol_class/pamr.ER.Rdata', sep='')) # predictor for ER receptor status
load(paste(config$R_SOURCE_PATH, '/data/brca_mol_class/pamr.PR.Rdata', sep='')) # predictor for PR receptor status
load(paste(config$R_SOURCE_PATH, '/data/brca_mol_class/pamr.HER2.Rdata', sep='')) # predictor for HER2 receptor status
load(paste(config$R_SOURCE_PATH, '/data/brca_mol_class/pamr.MG.Rdata', sep='')) # predictor for molecular subtypes (basel, her2, luminalA, luminalB)

## ----- brcaReceptorStatus -----
ERstatus <- as.vector(predictER(as.matrix(patientCountsNorm)))
PRstatus <- as.vector(predictPR(as.matrix(patientCountsNorm)))
HER2status <- as.vector(predictHER2(as.matrix(patientCountsNorm)))

receptorTable <- data.table(Receptor=c('ER', 'PR', 'HER2'),
                            Status=c(as.vector(ERstatus$prediction), as.vector(PRstatus$prediction), as.vector(HER2status$prediction)),
                            Prediction_probability=c(round(as.numeric(ERstatus$prob[1,ERstatus$prediction]),2),
                                                     round(as.numeric(PRstatus$prob[1,PRstatus$prediction]),2),
                                                     round(as.numeric(HER2status$prob[1,HER2status$prediction]),2)
                            )
)
#dTable(receptorTable, sPaginationType='full_numbers', iDisplayLength=25, sScrollX='100%', width='100%')
kable(receptorTable, format='html', table.attr = 'id=\"receptor_table\"')


## ----- brcaMolClass ----
MG <- as.vector(predictMG(as.matrix(patientCountsNorm)))

MGTable <- data.table(Subtype=as.vector(MG$prediction),
                      Prediction_probability=round((as.numeric(MG$prob[1,MG$prediction])),2)
)
#dTable(MGTable, sPaginationType='full_numbers', iDisplayLength=25, sScrollX='100%', width='100%')
kable(MGTable, format='html', table.attr = 'id=\"mol_table\"')


