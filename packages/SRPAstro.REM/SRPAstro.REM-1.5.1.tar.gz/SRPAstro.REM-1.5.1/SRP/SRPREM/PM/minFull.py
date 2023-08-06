""" Utility functions and classes for SRP

Context : SRP
Module  : PM
Version : 1.2.0
Author  : Stefano Covino
Date    : 07/01/2014
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (23/08/2012) First version.
        : (01/07/2013) Better check of paramter names.
        : (22/08/2013) Improvement.
        : (03/12/2013) Better naming.
        : (07/01/2014) Better organization of parameters.
"""

from Full import Full
from SRP.SRPMath.FastAngularDistance import FastAngularDistance



def minFull ((f_AAN,f_EAN,f_AAE,f_EAE,f_NPAE,f_BNP,f_AES,f_AEC,f_EES,f_EEC,f_AOFS,f_EOFS),taz,talt,oaz,oalt):
    caz, calt = Full((taz,talt),(f_AAN,f_EAN,f_AAE,f_EAE,f_NPAE,f_BNP,f_AES,f_AEC,f_EES,f_EEC,f_AOFS,f_EOFS))
    return FastAngularDistance(oaz,oalt,caz,calt).sum()

