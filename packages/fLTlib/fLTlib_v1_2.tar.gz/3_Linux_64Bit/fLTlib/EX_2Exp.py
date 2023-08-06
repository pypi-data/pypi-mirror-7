# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#    This file contains the code for EXP curve filter and fit, using the C/C++ finite Legendre transform library, fLTlib.
#    There are 4 demos, 1) the generation of Legendre polynomials, 2) the normal LMA fit, 3) L-domain filter function
#    and 4) L-domain fit function.
#
#    For more information on fLTlib, please use Help(fLTlib) or look at the last part of fLTHelpFun.py
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

from   fLTHelpFun        import *
import matplotlib.pyplot as plt
import numpy             as np

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#      Demo 1): Generate Legendre spectrum
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Suppose we fit a curve with 1500 sample points, and we would like to have the first 50 Legendre components
nl=[1500,   50]                                 #[points, facts]
P, X = fLTlib.myLegendre_P(nl[0], nl[1])        #generate spectrum
# = = = = = = = = Display the Legendre components = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
plt.figure; ax = plt.subplot(221);
plt.plot(X, np.transpose(P[1:5,:]));            #show first 5 lines
plt.text(0.2, 0.88, 'Legendre Polynomial', transform=ax.transAxes)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#      Demo Code to generate noisy EXP curves
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#      Some starting values:
#                    [A1    A2  ]  [T1  T2]  [time range ]    Offset    [OffsetErrorFact     PoissonFact]
A, T, XX, Off, fn  = [1000, 3000], [10, 30], [0,      100],   10.    ,  [1. ,                1.         ]
eX  = np.linspace(XX[0], XX[1], nl[0])      # X-axis value
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Generate noisy exp curves with A and T, Ym is the noisy curve
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
Y  = ((A[0] * np.exp(-eX/T[0]) + A[1] * np.exp(-eX/T[1])+0.5)); Yi = np.uint32(Y) # take int value for Poisson noise input
Yn = np.random.rand(nl[0]) * Off; Yn = Yn - np.mean(Yn); Yn = [(np.random.poisson(Yi)-Yi)*fn[0], Yn*fn[1]];
Ym = np.double(np.uint32(Y + Yn[0]+Yn[1])); nIndex = Ym<0; Ym[nIndex] = 0;  # suppose it is photon count, we round to int, >= 0

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#     Demo 2): Normal LMA fit
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
print "LM Fit"
Chi, n, A_lm, A_err = fLTlib.myFitEXP_LM(Ym, [1,1,1,1,1])   #Normal LM-fit 
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#      After fitting, we need to re-calculate Tau for the real X
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
AT_lm = myEXPBackCal(A_lm, XX[1], nl[0])
print '[A1 Tau1 A2 Tau2 Offset]=', np.array(AT_lm)
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#      Now, let us use the real X to generate the fit result and the plot
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
Yf = myEXPCal(eX, AT_lm)       # Now we calculate the exp curve with the real X
ax = plt.subplot(222); plt.plot(eX, Ym, eX, Yf,'r');plt.text(0.2, 0.88, 'T-Domain Fit', transform=ax.transAxes)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#
# *** Demo (3, 4):  Code using the new method to filter and fit the noisy EXP curve
#
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#  First, we calculate the amplitude (the Legendre components)
#  This step is the same for Demo 3) and 4), the function will return noiseless data as a filter
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
nn=5                                     # we use the first 5 components for filtering and fitting
A, Yf2 = fLTlib.myLegendre_A(Ym, 5, P)   # the return curve, Yf2, is already a noiseless curve for demo 3)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#  Yf2 is a noiseless curve, this is also the filter function of this method,
#  We display this curve:
ax = plt.subplot(223);plt.plot(eX, Ym, eX, Yf2, 'r');plt.text(0.2, 0.88, 'L-filter', transform=ax.transAxes)

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#  Secondly, we fit the Legendre components to find A and Tau
#          Function myFitEXP_LL(legendre_A, T_end, [Fit_Par_Switch], [Starting_Value]) can be found by help(fLTlib)
#          or at the end of fLTHelpFun.py
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
print "LL Fit"
A_all = fLTlib.myFitEXP_LL(A, XX[1], [1,1,1,1,1]) # same as, Chi, n, A_ll, A_err = ...
# = = = = = = = = = = = Display the results = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
print  '[A1 Tau1 A2 Tau2 Offset]=',A_all[2]
Yf = myEXPCal(eX, A_all[2]);
ax = plt.subplot(224);plt.plot(eX, Ym,eX, Yf,'r');plt.text(0.2, 0.88, 'L-Domain Fit', transform=ax.transAxes)
plt.show();

