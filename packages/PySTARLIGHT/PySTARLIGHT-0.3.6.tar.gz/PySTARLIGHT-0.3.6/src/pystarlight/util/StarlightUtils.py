'''
Created on Mar 13, 2012

@author: Andre Luiz de Amorim,
         Robeto Cid Fernandes

'''

import pystarlight.io #@UnusedImport
import atpy
import numpy as np
from scipy.interpolate import interp1d

###############################################################################
## Spectral resampling utility
###############################################################################
def ReSamplingMatrix(lorig , lresam, norm='True', extrap = False):
    '''
    Compute resampling matrix R_o2r, useful to convert a spectrum sampled at 
    wavelengths lorig to a new grid lresamp. Both are assumed to be uniform grids (ie, constant step).
    Input arrays lorig and lresamp are the bin centres of the original and final lambda-grids.
    ResampMat is a Nlresamp x Nlorig matrix, which applied to a vector F_o (with Nlorig entries) returns
    a Nlresamp elements long vector F_r (the resampled spectrum):

        [[ResampMat]] [F_o] = [F_r]

    Based on (but less general than) STARLIGHT's routine RebinSpec. Conserves flux, except for 
    possible loss at the blue & red edges of lorig (1st and last pixels).

    ElCid@Sanchica - 09/Feb/2012
    
    
    Parameters
    ----------
    lorig : array_like
            Original spectrum lambda array.
    
    lresam : array_like
             Spectrum lambda array in which the spectrum should be sampled.        
        
    Returns
    -------
    ResampMat : array_like
                Resample matrix. 
    
    Examples
    --------
    >>> lorig = np.linspace(3400, 8900, 4623)
    >>> lresam = np.linspace(3400, 8900, 9000)
    >>> forig = np.random.normal(size=len(lorig))**2
    >>> matrix = slut.ReSamplingMatrix(lorig, lresam)
    >>> fresam = np.dot(matrix, forig)
    >>> np.trapz(fresam, lresam)
    5588.7178984840939
    >>> np.trapz(forig, lorig)
    5588.7178984824877
    '''
    
    # Defs: steps & numbers
    dlorig  = lorig[1]  - lorig[0]
    dlresam = lresam[1] - lresam[0]
    Nlorig  = len(lorig)
    Nlresam = len(lresam)

    # Defs: lower & upper bin borders for lorig & lresam
    lorig_low  = lorig - dlorig/2
    lorig_upp  = lorig + dlorig/2
    lresam_low = lresam - dlresam/2
    lresam_upp = lresam + dlresam/2

    # Reset & fill resampling matrix
    ResampMat = np.zeros((Nlresam,Nlorig))

    # Find out if the original array is simply a subset of the resampled.
    # If it is, this routine already returns the correct resampling matrix
    subset = lresam_subset_lorig(lresam, lorig, ResampMat)

    if (not subset):

        for i_r in range(Nlresam):
            # inferior & superior lambdas representing the contribution of each lorig bin to current lresam bin.
            l_inf = np.where(lorig_low > lresam_low[i_r] , lorig_low , lresam_low[i_r])
            l_sup = np.where(lorig_upp < lresam_upp[i_r] , lorig_upp , lresam_upp[i_r])
    
            # lambda interval overlap of each lorig bin for current lresam bin. Negatives cliped to zero.
            dl = (l_sup - l_inf).clip(0)
    
            # When a lresam bin is not fully (> 99%) covered by lorig pixels, then discard it (leave it with zeros).
            # This will only happen at the edges of lorig.
            if (0 < dl.sum() < 0.99* dlresam):
                dl = 0 * lorig
    
            ResampMat[i_r,:] = dl
    
        if norm:
            ResampMat = ResampMat / dlresam

    # Fix extremes: extrapolate if needed
    if (extrap):
        extrap_ResampMat(ResampMat, lorig_low, lorig_upp, lresam_low, lresam_upp)

    return ResampMat


def ReSamplingMatrixNonUniform(lorig, lresam, extrap = False):
    '''
    Compute resampling matrix R_o2r, useful to convert a spectrum sampled at 
    wavelengths lorig to a new grid lresamp. Here, there is no necessity to have constant gris as on :py:func:`ReSamplingMatrix`.
    Input arrays lorig and lresamp are the bin centres of the original and final lambda-grids.
    ResampMat is a Nlresamp x Nlorig matrix, which applied to a vector F_o (with Nlorig entries) returns
    a Nlresamp elements long vector F_r (the resampled spectrum):

        [[ResampMat]] [F_o] = [F_r]

    Warning! lorig and lresam MUST be on ascending order!
    
    
    Parameters
    ----------
    lorig : array_like
            Original spectrum lambda array.
    
    lresam : array_like
             Spectrum lambda array in which the spectrum should be sampled.        

    extrap : boolean, optional
           Extrapolate values, i.e., values for lresam < lorig[0]  are set to match lorig[0] and
                                     values for lresam > lorig[-1] are set to match lorig[-1].
           

    Returns
    -------
    ResampMat : array_like
                Resample matrix. 
    
    Examples
    --------
    >>> lorig = np.linspace(3400, 8900, 9000) * 1.001
    >>> lresam = np.linspace(3400, 8900, 5000)
    >>> forig = np.random.normal(size=len(lorig))**2
    >>> matrix = slut.ReSamplingMatrixNonUniform(lorig, lresam)
    >>> fresam = np.dot(matrix, forig)
    >>> print np.trapz(forig, lorig), np.trapz(fresam, lresam)
    '''
    
    # Init ResampMatrix
    matrix = np.zeros((len(lresam), len(lorig)))
    
    # Define lambda ranges (low, upp) for original and resampled.
    lo_low = np.zeros(len(lorig))
    lo_low[1:] = (lorig[1:] + lorig[:-1])/2
    lo_low[0] = lorig[0] - (lorig[1] - lorig[0])/2 

    lo_upp = np.zeros(len(lorig))
    lo_upp[:-1] = lo_low[1:]
    lo_upp[-1] = lorig[-1] + (lorig[-1] - lorig[-2])/2

    lr_low = np.zeros(len(lresam))
    lr_low[1:] = (lresam[1:] + lresam[:-1])/2
    lr_low[0] = lresam[0] - (lresam[1] - lresam[0])/2
    
    lr_upp = np.zeros(len(lresam))
    lr_upp[:-1] = lr_low[1:]
    lr_upp[-1] = lresam[-1] + (lresam[-1] - lresam[-2])/2

    
    # Find out if the original array is simply a subset of the resampled.
    # If it is, this routine already returns the correct resampling matrix
    subset = lresam_subset_lorig(lresam, lorig, matrix)

    if (not subset):

        # Iterate over resampled lresam vector
        for i_r in range(len(lresam)): 
            
            # Find in which bins lresam bin within lorig bin
            bins_resam = np.where( (lr_low[i_r] < lo_upp) & (lr_upp[i_r] > lo_low) )[0]
    
            # On these bins, eval fraction of resamled bin is within original bin.
            for i_o in bins_resam:
                
                aux = 0
                
                d_lr = lr_upp[i_r] - lr_low[i_r]
                d_lo = lo_upp[i_o] - lo_low[i_o]
                d_ir = lo_upp[i_o] - lr_low[i_r]  # common section on the right
                d_il = lr_upp[i_r] - lo_low[i_o]  # common section on the left
                
                # Case 1: resampling window is smaller than or equal to the original window.
                # This is where the bug was: if an original bin is all inside the resampled bin, then
                # all flux should go into it, not then d_lr/d_lo fraction. --Natalia@IoA - 21/12/2012
                if (lr_low[i_r] >= lo_low[i_o]) & (lr_upp[i_r] <= lo_upp[i_o]):
                    aux += 1.
                    
                # Case 2: resampling window is larger than the original window.
                if (lr_low[i_r] < lo_low[i_o]) & (lr_upp[i_r] > lo_upp[i_o]):
                    aux += d_lo / d_lr
    
                # Case 3: resampling window is on the right of the original window.
                if (lr_low[i_r] > lo_low[i_o]) & (lr_upp[i_r] > lo_upp[i_o]):
                    aux += d_ir / d_lr
    
                # Case 4: resampling window is on the left of the original window.
                if (lr_low[i_r] < lo_low[i_o]) & (lr_upp[i_r] < lo_upp[i_o]):
                    aux += d_il / d_lr
    
                matrix[i_r, i_o] += aux


    # Fix matrix to be exactly = 1 ==> TO THINK
    #print np.sum(matrix), np.sum(lo_upp - lo_low), (lr_upp - lr_low).shape

    
    # Fix extremes: extrapolate if needed
    if (extrap):
        extrap_ResampMat(matrix, lo_low, lo_upp, lr_low, lr_upp)
        
    return matrix


def ReSamplingMatrixNonUniform_alt(lorig , lresam, norm='True', extrap = False):
    '''
    This is the pythonic equivalent to ReSamplingMatrixNonUniform.
    However, because the resampling matrix is so sparse, this version
    is *not* as fast as ReSamplingMatrixNonUniform when tested
    against arrays of sizes ~3000. It might be faster in some cases,
    so it remains here. It *is* faster than ReSamplingMatrix.

    ----
    
    Compute resampling matrix R_o2r, useful to convert a spectrum sampled at 
    wavelengths lorig to a new grid lresamp. Both are assumed to be uniform grids (ie, constant step).
    Input arrays lorig and lresamp are the bin centres of the original and final lambda-grids.
    ResampMat is a Nlresamp x Nlorig matrix, which applied to a vector F_o (with Nlorig entries) returns
    a Nlresamp elements long vector F_r (the resampled spectrum):

        [[ResampMat]] [F_o] = [F_r]

    Based on (but less general than) STARLIGHT's routine RebinSpec. Conserves flux, except for 
    possible loss at the blue & red edges of lorig (1st and last pixels).

    ElCid@Sanchica - 09/Feb/2012
    
    
    Parameters
    ----------
    lorig : array_like
            Original spectrum lambda array.
    
    lresam : array_like
             Spectrum lambda array in which the spectrum should be sampled.        
        
    Returns
    -------
    ResampMat : array_like
                Resample matrix. 
    
    Examples
    --------
    >>> lorig = np.linspace(3400, 8900, 4623)
    >>> lresam = np.linspace(3400, 8900, 9000)
    >>> forig = np.random.normal(size=len(lorig))**2
    >>> matrix = slut.ReSamplingMatrix(lorig, lresam)
    >>> fresam = np.dot(matrix, forig)
    >>> np.trapz(fresam, lresam)
    5588.7178984840939
    >>> np.trapz(forig, lorig)
    5588.7178984824877
    '''

    # Init ResampMatrix
    ResampMat__ro = np.zeros((len(lresam), len(lorig)))
    
    # Define lambda ranges (low, upp) for original and resampled.
    lo_low = np.zeros(len(lorig))
    lo_low[1:] = (lorig[1:] + lorig[:-1])/2
    lo_low[0] = lorig[0] - (lorig[1] - lorig[0])/2 

    lo_upp = np.zeros(len(lorig))
    lo_upp[:-1] = lo_low[1:]
    lo_upp[-1] = lorig[-1] + (lorig[-1] - lorig[-2])/2

    lr_low = np.zeros(len(lresam))
    lr_low[1:] = (lresam[1:] + lresam[:-1])/2
    lr_low[0] = lresam[0] - (lresam[1] - lresam[0])/2
    
    lr_upp = np.zeros(len(lresam))
    lr_upp[:-1] = lr_low[1:]
    lr_upp[-1] = lresam[-1] + (lresam[-1] - lresam[-2])/2

    
    # Find out if the original array is simply a subset of the resampled.
    # If it is, this routine already returns the correct resampling matrix
    subset = lresam_subset_lorig(lresam, lorig, ResampMat__ro)

    if (not subset):
        
        # Create comparison matrixes for lower and upper bin limits
        na = np.newaxis
        lo_low__ro = lo_low[na, ...]
        lo_upp__ro = lo_upp[na, ...]
        lr_low__ro = lr_low[..., na]
        lr_upp__ro = lr_upp[..., na]
    
        # Find in which bins lresam bin within lorig bin
        ff = (lr_low__ro < lo_upp__ro) & (lr_upp__ro > lo_low__ro)
    
        # Eval fraction of resamled bin is within original bin
        d_lr = lr_upp__ro - lr_low__ro
        d_lo = lo_upp__ro - lo_low__ro
        d_ir = lo_upp__ro - lr_low__ro  # common section on the right
        d_il = lr_upp__ro - lo_low__ro  # common section on the left
    
        # Case 1: resampling window is smaller than or equal to the original window.
        f1 = (ff) & (lr_low__ro >= lo_low__ro) & (lr_upp__ro <= lo_upp__ro)
        if (f1.sum() > 0):
            ResampMat__ro[f1] += 1.
    
        # Case 2: resampling window is larger than the original window.
        f2 = (ff) & (lr_low__ro < lo_low__ro) & (lr_upp__ro > lo_upp__ro)
        if (f2.sum() > 0):
            ResampMat__ro[f2] += (d_lo / d_lr)[f2]
    
        # Case 3: resampling window is on the right of the original window.
        f3 = (ff) & (lr_low__ro > lo_low__ro) & (lr_upp__ro > lo_upp__ro)
        if (f3.sum() > 0):
            ResampMat__ro[f3] += (d_ir / d_lr)[f3]
    
        # Case 4: resampling window is on the left of the original window.
        f4 = (ff) & (lr_low__ro < lo_low__ro) & (lr_upp__ro < lo_upp__ro)
        if (f4.sum() > 0):
            ResampMat__ro[f4] += (d_il / d_lr)[f4]

    # Fix extremes: extrapolate if needed
    if (extrap):
        extrap_ResampMat(ResampMat__ro, lo_low, lo_upp, lr_low, lr_upp)

    return ResampMat__ro


def lresam_subset_lorig(lresam, lorig, ResampMat__ro):
    '''
    Finds out if lorig is a subset of lresam. If so,
    create a `diagonal' resampling matrix (in place).
    '''

    subset = False
    tol = 1.e-5
    
    ff = (lresam >= lorig[0]) & (lresam <= lorig[-1])
    lresam_sub = lresam[ff]

    N_lo = len(lorig)

    if (len(lresam_sub) == N_lo):
        Nok = (abs(lorig - lresam_sub) < tol).sum()

        if (Nok == N_lo):
            subset = True
            ilow = np.where(ff)[0][0]
            iupp = np.where(ff)[0][-1]
    
            io_diag = np.arange(len(lorig))
            ir_diag = np.arange(ilow, iupp+1)
            ResampMat__ro[ir_diag, io_diag] = 1.

    return subset


def extrap_ResampMat(ResampMat__ro, lo_low, lo_upp, lr_low, lr_upp):
    '''
    Extrapolate resampling matrix on the borders, i.e.,
    by making it copy the first and the last bins.

    This modifies ResampMat__ro in place.
    '''
    
    bins_extrapl = np.where( (lr_low < lo_low[0])  )[0]
    bins_extrapr = np.where( (lr_upp > lo_upp[-1]) )[0]

    if (len(bins_extrapl) > 0) & (len(bins_extrapr) > 0):
        io_extrapl = np.where( (lo_low >= lr_low[bins_extrapl[0]]) )[0][0]
        io_extrapr = np.where( (lo_upp <= lr_upp[bins_extrapr[0]]) )[0][-1]

        ResampMat__ro[bins_extrapl, io_extrapl] = 1.
        ResampMat__ro[bins_extrapr, io_extrapr] = 1.

    
###############################################################################
## Starlight base utility
###############################################################################

class StarlightBase(object):
    '''
    Starlight base interface and utilities.
    '''
    
    def __init__(self, baseFile, baseDir):
        self._baseTable = atpy.Table(baseFile, type='starlightv4_base', basedir=baseDir, read_basedir=True)
        self.ageBase__t = np.unique(self._baseTable.age_base)
        self.nAges = len(self.ageBase__t)

        self.metBase__t = np.unique(self._baseTable.Z_base)
        self.nMet = len(self.metBase__t)
        
        self.l_ssp__l = self._baseTable.l_ssp[0]
        if (self._baseTable.l_ssp != self.l_ssp__l).any():
            raise 'Error! Base is not well defined on all elements in wavelength!' #Base must be consistent on lambdas! Check this here.
        self.nWavelength = len(self.l_ssp__l)
         
        # Base spectra using the original wavelength sampling.
        self.f_ssp__tZl = self.from_j_to_tZ(self._baseTable.f_ssp, n=self.nWavelength)
        
        # Base files, for whatever reason.
        self.sspfile = self._baseTable.sspfile
        
        # Interpolation function for the spectra.
        self._interp_f_ssp__tZl = self._getInterpSpectra()
    
    
    def from_j_to_tZ(self, a, n=1):
        '''
        Convert an array from 1-D j-notation to 2-D (Z, age)-notation.
        '''
        return np.transpose(a.reshape((self.nMet, self.nAges, n)), axes=(1, 0, 2))
        
        
    def _getInterpSpectra(self):
        '''
        Interpolation function for latter use.
        Note the fill value of 0 when interpolating out of bounds.
        '''
        return interp1d(self.l_ssp__l, self.f_ssp__tZl,
                        axis=2, bounds_error=False, fill_value=0)


    def getLookbacktimeSpectraOperator(self, evoBase__T, wavelength=None):
        '''
        Returns an operator for computing spectra in lookbacktime.
        If wavelength is None, use the base wavelength array.
        
        Examples
        ========
        evoBase__T = 10.0**np.arange(8, 10, 0.1) # log_10 steps
        mini__tZ = (popmu_ini__tZ * Mini_tot / 100.0)
        f_ssp__TtZl = base.getLookbacktimeSpectraOperator(evoBase__T)
        F__Tl = np.tensordot(f_ssp__TtZl, mini__tZ, [(1, 2), (0, 1)])
        
        # plot all the spectra.
        plt.figure()
        for i, age in enumerate(evoBase__T):
            plt.plot(base.l_ssp__l, F__Tl[i], label=age)
        plt.legend()
        plt.show()
        '''
        interpolated_f_ssp__tZl = self._interp_f_ssp__tZl(wavelength)
        f_ssp__TtZl = np.zeros((len(evoBase__T), self.nAges, self.nMet, len(wavelength)))
        for i, T in enumerate(evoBase__T):
            mask = self.ageBase__t >= T
            sel = np.digitize(self.ageBase__t[mask] - T, self.ageBase__t)
            f_ssp__TtZl[i][mask] = interpolated_f_ssp__tZl[sel]
        return f_ssp__TtZl


###############################################################################


def ageSmoothingKernel(logAgeBase, logTc, logtc_FWHM=0.1):
    '''
    Given an array of logAgeBase = log10(base ages), and an array logTc of "continuous" log ages 
    (presumably uniformly spaced), computes the smoothing kernel s_bc, which resamples and smooths
    any function X(logAgeBase) to Y(logTc). 
    If X = X_b, where b is the logAgeBase index, and Y = Y_c, with c as the index in logTc, then 

    Y_c = sum-over-all-b's of X_b s_bc

    gives the smoothed & resampled version of X. 
    The smoothing is performed in log-time, with gaussian function of FWHM = logtc_FWHM. 
    Conservation of X is ensured (ie, X_b = sum-over-all-c's of Y_c s_bc).

    Notice that logTc and logtc_FWHM are given default values, in case of lazy function callers...
    However, I do NOT know how to call the function using the default logTc but setting a FWHM different from default!!!
    ???Andre????

    Input:  logAgeBase = array of log base ages [in log yr]
            logTc = array of log "continous" ages [in log yr]
            logtc_FWHM = width of smoothing filter [in dex]
    Output: s__bc = (len(logAgeBase) , len(logTc)) matrix [adimensional]

    ElCid@Sanchica - 18/Mar/2012
    '''
    s__bc = np.zeros( (len(logAgeBase) , len(logTc)) )
    logtc_sig =  logtc_FWHM / (np.sqrt(8 * np.log(2)))
    for i_b , a_b in enumerate(logAgeBase):
        aux1 = np.exp(-0.5 * ((logTc - a_b) / logtc_sig)**2)
        s__bc[i_b,:] = aux1 / aux1.sum()
    return s__bc


#############################################################################
## MStars utility
#############################################################################

class MStars(object):
    '''
    Handle Mstars interpolation for population mass evolution.
    '''
    
    def __init__(self, ageBase, metBase, Mstars):
        self._interpMstars = self._getInterpMstars(ageBase, metBase, Mstars)
        self._metBase = metBase

        
    def _getInterpMstars(self, ageBase, metBase, Mstars):
        '''
        Find the interpolation function for Mstars in the base
        ageBase and metBase. Points are added in age==0.0 and
        age==1e20, so one can find Mstars(today) and Mstars(at big bang).
        
        Returns a list of interpolation functions, one for each metallicity.
        '''
        _Mstars = np.empty((len(ageBase)+2, len(metBase)))
        _Mstars[1:-1] = Mstars
        _Mstars[0] = 1.0
        _Mstars[-1] = _Mstars[-2]
        _ageBase = np.empty((len(ageBase)+2))
        _ageBase[0] = 0.0
        _ageBase[1:-1] = ageBase
        _ageBase[-1] = 1e20
        interpMstars = [interp1d(_ageBase, _Mstars[:,Zi]) for Zi in range(len(metBase))]
        return interpMstars 


    def forTime(self, ageBase, Tc=None):
        '''
        MStars is the fraction of the initial stellar mass for a given
        population that is still trapped inside stars.
        This method calculates Mstars for populations given by ageBase,
        in evolutionary times given by Tc.
        
        If Tc is None, use the same times as ageBase.
        
        Returns a ndarray with shape (len(Tc), len(ageBase), len(metBase)),
        where metBase is the one used in constructor.
        '''
        if Tc is None:
            Tc = ageBase
        if not isinstance(Tc, np.ndarray):
            Tc = np.array([Tc])
            
        _f = np.zeros((len(Tc), len(ageBase), len(self._metBase)))
        for Ti in range(len(Tc)):
            mask = ageBase >= Tc[Ti]
            for Zi in range(len(self._metBase)):
                _f[Ti][mask,Zi] = self._interpMstars[Zi](ageBase[mask] - Tc[Ti])
    
        return _f
    


#############################################################################

def interpAge(prop, logAgeBase, logAgeInterp):
    '''
    Interpolate linearly Mstars or fbase_norm in log time.
    
    Parameters
    ----------
    prop : array
        Array containing ``Mstars`` or ``fbase_norm``.
        
    logAgeBase : array
        The age base, the same legth as the first
        dimension of ``prop``.

    logAgeInterp : array
        The age to which interpolate ``prop``. The
        returned value will have the same length in
        the first dimension.
        
    Returns
    -------
    propInterp : array
        The same ``prop``, interpolated to ``logAgeInterp``.
    '''
    nMet = prop.shape[1]
    nAgeInterp = len(logAgeInterp)
    propInterp = np.empty((nAgeInterp, nMet), dtype='>f8')
    for z in xrange(nMet):
        propInterp[:,z] = np.interp(logAgeInterp, logAgeBase, prop[:,z])
    return propInterp


#############################################################################

def light2MassIni(popx, fbase_norm, Lobs_norm, q_norm, A_V):

    '''
    Compute the initial mass from popx (and other parameters).
    The most important thing to remember is that popx (actually luminosity)
    must be "dereddened" before converting it to mass using fbase_norm
    (popmu_ini).
    
    Based on the subroutine ConvertLight2Mass (starlight source code).
    
    Parameters
    ----------
    popx: array
        The light fractions (in percents).
        
    fbase_norm: array
        Light to mass ratio for each population.
        
    Lobs_norm : array
        Luminosity norm of ``popx``.
        
    q_norm : float 
        Ratio between the extinction in l_norm (where Lobs_norm
        is calculated) and ``A_V``.
        
    A_V : array 
        Extinction in V band.
    
    Returns
    -------
    Mini : array
        The initial mass in each population.

    '''
    Lobs = popx / 100.0
    Lobs *= Lobs_norm
    Lobs *= 10.0**(0.4 * q_norm * A_V)
    
    Mini = Lobs / arrayAsRowMatrix(fbase_norm, Lobs.ndim)
    return Mini


#############################################################################

def calcSFR(popx, fbase_norm, Lobs_norm, q_norm, A_V, logtb, logtc, logtc_FWHM):
    '''
    Calculate the star formation rate (SFR) from the light fractions,
    using a smoothed logarithmic (base 10) time base. The smoothed
    log. time base ``logtc`` must be evenly spaced.
    
    This code is is basen on the equation (5) from Asari (2007)
    <http://adsabs.harvard.edu/abs/2007MNRAS.381..263A> 

    Parameters
    ----------
    popx: array
        The light fractions (in percents).
        
    fbase_norm: array
        Light to mass ratio for each population.
        
    Lobs_norm : array
        Luminosity norm of ``popx``.
        
    q_norm : float 
        Ratio between the extinction in l_norm (where Lobs_norm
        is calculated) and ``A_V``.
        
    A_V : array 
        Extinction in V band.
    
    logtb : array 
        Logarithm (base 10) of original time base.
    
    logtc : array 
        Logarithm (base 10) of resampled time base.
        Must be evenly spaced.
    
    logtc_FWHM : float
        Width of the age smoothing kernel used to resample ``popx``.
    
    Returns
    -------
    SFR_sm : array
        The star formation rate, smoothed.
        Note: ``len(SFR_sm) == len(logtc)`` 

    '''
    tc = 10.0**logtc
    
    # FIXME: how calculate/verify the time step properly?
    logtc_step = logtc[1] - logtc[0]
    
    smoothKernel = ageSmoothingKernel(logtb, logtc, logtc_FWHM)
    popx_sm = np.tensordot(smoothKernel, popx, (0,0))
    
    fbase_norm_interp = interpAge(fbase_norm, logtb, logtc)
    Mini_sm = light2MassIni(popx_sm, fbase_norm_interp, Lobs_norm, q_norm, A_V)
    Mini_sm = Mini_sm.sum(axis=1)
    tmp = np.log10(np.exp(1.0)) / (logtc_step * tc)
    SFR_sm = Mini_sm * arrayAsRowMatrix(tmp, len(Mini_sm.shape))
    
    return SFR_sm


#############################################################################

def calcPopmu(popx, fbase_norm, Lobs_norm, Mstars, q_norm, A_V):
    '''
    Compute popmu_ini and popmu_cor from popx (and other parameters).
    The most important thing to remember is that popx (actually luminosity)
    must be "dereddened" before converting it to mass using fbase_norm
    (popmu_ini). Also note the role of Mstars when computing the mass
    currently trapped inside stars (popmu_cor).
    
    Based on the subroutine ConvertLight2Mass (starlight source code).
    
    Parameters
    ----------
    popx: array
        The light fractions (in percents).
        
    fbase_norm: array
        Light to mass ratio for each population.
        
    Lobs_norm : array
        Luminosity norm of ``popx``.
        
    Mstars : array 
        Fraction of the initial stellar mass for a given
        population that is still trapped inside stars.
        
    q_norm : float 
        Ratio between the extinction in l_norm (where Lobs_norm
        is calculated) and ``A_V``.
        
    A_V : array 
        Extinction in V band.
    
    Returns
    -------
    popmu_ini : array
        The initial mass fractions (in percents).

    popmu_cor : array
        The current mass fractions (in percents).

    '''
    Mini = light2MassIni(popx, fbase_norm, Lobs_norm, q_norm, A_V)
    ndim = len(Mini.shape)
    Mcor = Mini * arrayAsRowMatrix(Mstars, ndim)
    
    popmu_ini = Mini / Mini.sum(axis=1).sum(axis=0) * 100.0
    popmu_cor = Mcor / Mcor.sum(axis=1).sum(axis=0) * 100.0
    return popmu_ini, popmu_cor 


#############################################################################

def arrayAsRowMatrix(a, ndim):
    '''
    Reshape ``a`` to a "row matrix" of bigger rank, ``ndim``.
    
    Parameters
    ----------
    a : array
        Array to reshape.
        
    ndim : integer
        Number of dimensions to reshape.
        
    Returns
    -------
    a_reshaped : array
        The same array as ``a``, reshaped to ``ndim`` dimensions.
    '''
    if a.ndim == ndim:
        return a
    if a.ndim > ndim:
        raise ValueError('number of dimensions of input must be smaller than %d.' % ndim)
    new_shape = np.ones(ndim, dtype=int)
    new_shape[:a.ndim] = a.shape
    return a.reshape(new_shape)


################################################################################

def gaussVelocitySmooth(lo, fo, v0, sig, ls=None, n_u=31, n_sig=6):
    '''
    c # Smooth an input spectrum fo(lo) with a Gaussian centered at velocity
    c # v = v0 and with sig as velocity dispersion. The output is fs(ls).
    c # The convolution is done with a BRUTE FORCE integration of n_u points
    c # from u = -n_sig to u = +n_sig, where u = (v - v0) / sig.
    c # OBS: Assumes original spectrum fo(lo) is EQUALLY SPACED in lambda!!
    C #      Units of v0 & sig = km/s
    c # Cid@Lynx - 05/Dec/2002
    
    c # Added n_u as a parameter!
    c # Cid@Lynx - 16/Mar/2003
    
    *ETC* !AKI! gfortran does not like do u=u_low,u_upp,du! But works! Fix
    *     after other tests are done! Cid@Lagoa - 11/Jan/2011
    
    *     This version of GaussSmooth replaces the u-loop by one in an
    *     integer index i_u. The differences wrt are minute (< 1e-5) and due
    *     to precision...
    *
    *      ElCid@Sanchica - 16/Ago/2011
    
    *ATT* Promoted to new oficial GaussSmooth without much testing!
    *      Previous version removed to skip compilation warnings...
    *    ElCid@Sanchica - 08/Oct/2011
    
    *ATT* Found an array bounds-bug when compiling with gfortran ... -fbounds-check
    *      Ex: Fortran runtime error: Index '3402' of dimension 1 of array 'fo' above upper bound of 3401
    *      Happens only when sig is very large. The old routine is kept below, and documents the bug briefly.
    *    ElCid@Sanchica - 05/Nov/2011
    '''
    c  = 2.997925e5

    if n_u < 5:
        raise ValueError('n_u=%d too small to integrate properly.' % n_u)

    if ls is None:
        ls = lo
        
# Parameters for the brute-force integration in velocity
    u = np.linspace(-n_sig, n_sig, n_u)
    du = u[1] - u[0]
    d_lo = lo[1] - lo[0]

    Ns = len(ls)
    No = len(lo)
    fs = np.empty(Ns, dtype=fo.dtype)

# loop over ls, convolving fo(lo) with a gaussian
    for i_s in xrange(Ns):

# reset integral of {fo[ll = ls/(1+v/c)] * Gaussian} & start integration
        sum_fg = 0.
        for _u in u:

# define velocity & lambda corresponding to u
            v  = v0 + sig * _u
            ll = ls[i_s] / (1.0 + v/c)

# find fo flux for lambda = ll
            ind = int((ll - lo[0]) / d_lo)
            if ind < 0: 
                ff = fo[0]
            elif ind >= No-1:
                ff = fo[No-1]
            else:
                a  = (fo[ind+1] - fo[ind]) / (lo[ind+1] - lo[ind])
                b  = fo[ind] - a * lo[ind]
                ff = a * ll + b

# smoothed spectrum
            sum_fg = sum_fg + ff * np.exp(-(_u**2/2.)) 
        fs[i_s] = sum_fg * du / np.sqrt(2. * np.pi)
    return fs


################################################################################\


