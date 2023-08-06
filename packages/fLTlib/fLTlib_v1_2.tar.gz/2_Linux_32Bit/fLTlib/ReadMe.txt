README for fLTlib v1.1 (Linux 32-bit systems)
18-Aug-2014


RUNNING ENVIRONMENT & PACKAGEs

Python 2.7 + numpy + scipy + matplotlib

NOTE: to install numpy, scipy and matplotlib packages, please download the installation files according to your system and follow the installing instructions on http://www.scipy.org/install.html


FILE DETAILS

1) The following 5 files are demo codes for filtering and fitting:

LegendreLowpassFilter.py	Demo for filters (use numpy, scipy, matplotlib, LegendrePolynomials.py).
LegendreFitting.py		Demo for single EXP fitting (numpy, scipy, matplotlib, LegendrePolynomials.py).
EX_2Exp.py			Demo for double EXP fitting (numpy, matplotlib, fLTHelpFun.py)
EX_2Exp_Conv_L.py		Demo for EXP convoluting a system device function (numpy, matplotlib, fLTHelpFun.py).
EX_2Exp_Conv_T.py		Same demo using a normal LMA method (numpy, matplotlib, fLTHelpFun.py).


2) The following 3 files are the Legendre Function library files (and the dependent packages):

LegendrePolynomials.py	(needs numpy, scipy)
fLTHelpFun.py	(needs numpy)
fLTlib.so
fLTlib_py.py	A platform independent version, used when "fLTlib.so" is missing or error in loading (needs numpy)


3) The following 2 files contain some test data:

noisyExp.dat
TEST_With_Device_Responce_Function.csv


For more information, please visit our web on: http://www.ukmn.gwdg.de/
Or the paper on: http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0090500

For bug reports, questions, or comments please contact: dschild@gwdg.de or gbao@gwdg.de
