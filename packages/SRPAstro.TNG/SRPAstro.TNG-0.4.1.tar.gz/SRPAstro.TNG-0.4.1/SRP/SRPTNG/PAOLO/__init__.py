""" 

Context : SRP
Module  : PAOLO
Version : 1.1.1
Author  : Stefano Covino
Date    : 08/04/2013
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : to be imported

Remarks :

History : (26/02/2012) First version.
        : (27/09/2012) New constants.
        : (25/03/2013) New constants.
        : (01/04/2013) New constants.
        : (08/04/2013) New constants.
"""


__all__ = ['AverHourAngle', 'AverParallacticAngle', 'MuellerOffsetMatrix', 'StokesOffsetVector', 
           'TNGMuellerMatrix', 'TNGMuellerMatrixNoDerot']




# Columns and headers
eFlux       = 'eFlux'
Flux        = 'Flux'
TotFlux     = 'TotFlux'
eTotFlux    = 'eTotFlux'
eMag        = 'eMag'
Mag         = 'Mag'
TotMag      = 'TotMag'
eTotMag     = 'eTotMag'
Id          = 'Id'
I           = 'I'
eI          = 'eI'
Q           = 'Q'
eQ          = 'eQ'
U           = 'U'
eU          = 'eU'
V           = 'V'
eV          = 'eV'
X           = 'X'
Y           = 'Y'
CalQ        = 'CalQ'
eCalQ       = 'eCalQ'
CalU        = 'CalU'
eCalU       = 'eCalU'
CalV        = 'CalV'
eCalV       = 'eCalV'
CompI       = 'CompI'
CompeI      = 'CompeI'
CompQ       = 'CompQ'
CompeQ      = 'CompeQ'
CompU       = 'CompU'
CompeU      = 'CompeU'
CompV       = 'CompV'
CompeV      = 'CompeV'
AZ          = 'AZ'
ALT         = 'ALT'
DATE        = 'DATE'
DEROT       = 'DEROT'
EXPTIME     = 'EXPTIME'
FILTER      = 'FILTER'
HOURANG     = 'HOURANG'
LAMBDA2     = 'LAMBDA2'
LAMBDA4     = 'LAMBDA4'
OBJECT      = 'OBJECT'
PARANG      = 'PARANG'
POLSLIDE    = 'PLATE'
POSANG      = 'POSANG'
PRISM       = 'PRISM'
PSTOP       = 'PSTOP'
PPSTOP      = 'PPSTOP'
RA          = 'RA'
DEC         = 'DEC'
ROTLAM2     = 'ROTLAM2'
ROTLAM4     = 'ROTLAM4'
SEQUENCE    = 'SEQUENCE'
TIME        = 'TIME'
WAVE        = 'WAVELEN'
MJD         = 'MJD'
#
N           = 'N'
K           = 'K'
DETOFF      = 'DETOFF'
Q0          = 'Q0'
U0          = 'U0'
V0          = 'V0'
CHI2        = 'CHI2'
#
tempfile    = '_temp.fits'
#
quad1cut    = '55 790 22 1210'
quad2cut    = '55 935 55 1065'
quad3cut    = '55 1070 55 925'
quad4cut    = '55 1215 55 785'
framecut    = '85 870 330 700'
#
XCORR       = 'XCORR'
