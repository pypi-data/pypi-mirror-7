import os, math, re, time

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from libc cimport stdlib, stdio
from cython cimport view

import numpy
cimport numpy

cdef extern from "GWsim-stub.h":
    ctypedef struct gwSrc:
        pass 

    void GWbackground(gwSrc *gw,int numberGW,long *idum,long double flo,long double fhi,double gwAmp,double alpha,int loglin)
    void setupGW(gwSrc *gw)
    void setupPulsar_GWsim(long double ra_p,long double dec_p,long double *kp)
    long double calculateResidualGW(long double *kp,gwSrc *gw,long double obstime,long double dist)

cdef extern from "tempo2.h":
    enum: MAX_PSR_VAL
    enum: MAX_FILELEN
    enum: MAX_OBSN_VAL
    enum: MAX_PARAMS
    enum: MAX_JUMPS
    enum: param_pepoch
    enum: param_raj
    enum: param_decj

    int MAX_PSR, MAX_OBSN

    ctypedef struct parameter:
        char **label
        char **shortlabel
        long double *val
        long double *err
        int  *fitFlag
        int  *paramSet
        long double *prefit
        long double *prefitErr
        int aSize

    ctypedef struct observation:
        long double sat        # site arrival time
        long double bat        # barycentric arrival time
        int deleted            # 1 if observation deleted, -1 if not in fit
        long double prefitResidual
        long double residual
        double toaErr          # error on TOA (in us)
        double toaDMErr        # error on TOA due to DM (in us)
        char **flagID          # ID of flags
        char **flagVal         # Value of flags
        int nFlags             # Number of flags set
        double freq            # frequency of observation (in MHz)
        double freqSSB         # frequency of observation in barycentric frame (in Hz)
        char telID[100]        # telescope ID

    ctypedef struct pulsar:
        parameter param[MAX_PARAMS]
        observation *obsn
        char *name
        int nobs
        int rescaleErrChisq
        int noWarnings
        double fitChisq
        int nJumps
        double jumpVal[MAX_JUMPS]
        int fitJump[MAX_JUMPS]
        double jumpValErr[MAX_JUMPS]
        char *binaryModel

    void initialise(pulsar *psr, int noWarnings)
    void destroyOne(pulsar *psr)

    void readParfile(pulsar *psr,char parFile[][MAX_FILELEN],char timFile[][MAX_FILELEN],int npsr)
    void readTimfile(pulsar *psr,char timFile[][MAX_FILELEN],int npsr)

    void preProcess(pulsar *psr,int npsr,int argc,char *argv[])
    void formBatsAll(pulsar *psr,int npsr)
    void updateBatsAll(pulsar *psr,int npsr)                    # what's the difference?
    void formResiduals(pulsar *psr,int npsr,int removeMean)
    void doFit(pulsar *psr,int npsr,int writeModel)
    void updateParameters(pulsar *psr,int p,double val[],double error[])

    # for tempo2 versions older than, change to
    # void FITfuncs(double x,double afunc[],int ma,pulsar *psr,int ipos)
    void FITfuncs(double x,double afunc[],int ma,pulsar *psr,int ipos,int ipsr)

    int turn_hms(double turn,char *hms)

    void textOutput(pulsar *psr,int npsr,double globalParameter,int nGlobal,int outRes,int newpar,char *fname)
    void writeTim(char *timname,pulsar *psr,char *fileFormat)

cdef class tempopar:
    cdef public object name

    cdef int _isjump
    cdef void *_val
    cdef void *_err
    cdef int *_fitFlag
    cdef int *_paramSet

    def __init__(self,*args,**kwargs):
        raise TypeError("This class cannot be instantiated from Python.")

    property val:
        def __get__(self):
            if not self._isjump:
                return numpy.longdouble((<long double*>self._val)[0])
            else:
                return float((<double*>self._val)[0])
        def __set__(self,value):
            if not self._isjump:
                if not self._paramSet[0]:
                    self._paramSet[0] = 1

                (<long double*>self._val)[0] = value    # can we set it to numpy.longdouble?
                (<long double*>self._err)[0] = 0
            else:
                (<double*>self._val)[0] = value
                (<double*>self._err)[0] = 0
    property err:
        def __get__(self):
            if not self._isjump:
                return numpy.longdouble((<long double*>self._err)[0])
            else:
                return float((<double*>self._err)[0])
        def __set__(self,value):
            if not self._isjump:
                (<long double*>self._err)[0] = value
            else:
                (<double*>self._err)[0] = value

    property fit:
        def __get__(self):
            return True if self._fitFlag[0] else False
        def __set__(self,value):
            if value:
                if not self._paramSet[0]:
                    self._paramSet[0] = 1

                self._fitFlag[0] = 1
            else:
                self._fitFlag[0] = 0

    # note that paramSet is not always respected in tempo2
    property set:
        def __get__(self):
            if not self._isjump:
                return True if self._paramSet[0] else False
            else:
                return True
        def __set__(self,value):
            if not self._isjump:
                if value:
                    self._paramSet[0] = 1
                else:
                    self._paramSet[0] = 0

    def __str__(self):
        # TO DO: proper precision handling
        if self.set:
            return '%s (%s): %g +/- %g' % (self.name,'fitted' if self.fit else 'not fitted',self.val,self.err)
        else:
            return '%s (unset)'

# since the __init__ for extension classes must have a Python signature,
# we use a factory function to initialize its attributes to pure-C objects

cdef create_tempopar(parameter par,int subct):
    cdef tempopar newpar = tempopar.__new__(tempopar)

    newpar.name = str(par.shortlabel[subct])

    newpar._isjump = 0

    newpar._val = &par.val[subct]
    newpar._err = &par.err[subct]
    newpar._fitFlag = &par.fitFlag[subct]
    newpar._paramSet = &par.paramSet[subct]

    return newpar

# TODO: note that currently we cannot change the number of jumps programmatically
cdef create_tempojump(pulsar *psr,int ct):
    cdef tempopar newpar = tempopar.__new__(tempopar)

    newpar.name = 'JUMP{0}'.format(ct)

    newpar._isjump = 1

    newpar._val = &psr.jumpVal[ct]
    newpar._err = &psr.jumpValErr[ct]
    newpar._fitFlag = &psr.fitJump[ct]

    return newpar

class prefitpar(object):
    def __init__(self,name,val,err):
        self.__dict__['name'] = name
        self.__dict__['val']  = val
        self.__dict__['err']  = err

    def __setattr__(self,par,val):
        raise TypeError, "Cannot write to prefit parameters."

    def __str__(self):
        # TO DO: proper precision handling
        return '%s: %g +/- %g' % (self.name,self.val,self.err)

cdef class GWB:
    cdef gwSrc *gw
    cdef int ngw

    def __cinit__(self,ngw=1000,seed=None,flow=1e-8,fhigh=1e-5,gwAmp=1e-20,alpha=-0.66,logspacing=True):
        self.gw = <gwSrc *>stdlib.malloc(sizeof(gwSrc)*ngw)
        self.ngw = ngw

        if seed is None:
            seed = -int(time.time())

        gwAmp = gwAmp * (86400.0*365.25)**alpha

        cdef long idum = seed
        GWbackground(self.gw,ngw,&idum,flow,fhigh,gwAmp,alpha,1 if logspacing else 0)

        for i in range(ngw):
          setupGW(&self.gw[i])

    def __dealloc__(self):
        stdlib.free(self.gw)

    def add_gwb(self,tempopulsar pulsar,distance=1):
        cdef long double dist = distance * 3.086e19

        cdef long double ra_p  = pulsar.psr[0].param[param_raj].val[0]
        cdef long double dec_p = pulsar.psr[0].param[param_decj].val[0]

        cdef long double epoch = pulsar.psr[0].param[param_pepoch].val[0]

        cdef long double kp[3]

        setupPulsar_GWsim(ra_p,dec_p,&kp[0])

        cdef numpy.ndarray[long double,ndim=1] res = numpy.zeros(pulsar.nobs,numpy.longdouble)
        cdef long double obstime

        for i in range(pulsar.nobs):
            obstime = (pulsar.psr[0].obsn[i].sat - epoch)*86400.0
            res[i] = 0.0

            for k in range(self.ngw):
                res[i] = res[i] + calculateResidualGW(kp,&self.gw[k],obstime,dist)

        res[:] = res[:] - numpy.mean(res)
        
        pulsar.stoas[:] += res[:] / 86400.0

# this is a Cython extension class; the benefit is that it can hold C attributes,
# but all attributes must be defined in the code

cdef class tempopulsar:
    cpdef object parfile
    cpdef object timfile

    cdef int npsr           # number of pulsars
    cdef pulsar *psr        # array of pulsar structures

    cpdef object pardict    # dictionary of parameter proxies
    cpdef public object prefit     # dictionary of pre-fit parameters
    cpdef public int nobs   # number of observations (public)
    cpdef public object allflags    # a list of all flags that have values
    cpdef public object flags       # a dictionary of numpy arrays with flag values
    cpdef public double fitchisq

    # TO DO: is cpdef required here?
    cpdef jumpval, jumperr

    def __cinit__(self,parfile,timfile=None,warnings=False,fixangularerror=True,fixprefiterrors=True,
                  dofit=True,maxobs=None):
        # initialize

        global MAX_PSR, MAX_OBSN

        self.npsr = 1

        # to save memory, only allocate space for this many pulsars and observations
        MAX_PSR = 1
        MAX_OBSN = MAX_OBSN_VAL if maxobs is None else maxobs

        self.psr = <pulsar *>stdlib.malloc(sizeof(pulsar)*MAX_PSR)
        initialise(self.psr,1)          # 1 for no warnings

        # read par and tim file

        timfile = rewritetim(timfile)
        self._readfiles(parfile,timfile)
        os.unlink(timfile)

        # set tempo2 flags

        self.psr.rescaleErrChisq = 0        # do not rescale fit errors by sqrt(red. chisq)

        if not warnings:
            self.psr.noWarnings = 2         # do not show some warnings

        # preprocess the data

        preProcess(self.psr,self.npsr,0,NULL)
        formBatsAll(self.psr,self.npsr)

        # create parameter proxies, copy prefit values

        self.nobs = self.psr[0].nobs
        self._readpars(fixangularerror=fixangularerror,fixprefiterrors=fixprefiterrors)
        self._readflags()

        # save prefit TOAs and residuals

        self.prefit.toas = self.toas()
        self.prefit.residuals = self.residuals(updatebats=False)

        # do a fit if requested
        if dofit:
            self.fit()

    def __dealloc__(self):
        for i in range(self.npsr):
            destroyOne(&(self.psr[i]))
            stdlib.free(&(self.psr[i]))

    def _readfiles(self,parfile,timfile):
        cdef char parFile[MAX_PSR_VAL][MAX_FILELEN]
        cdef char timFile[MAX_PSR_VAL][MAX_FILELEN]

        if timfile is None:
            timfile = re.sub('\.par$','.tim',parfile)

        self.parfile = parfile
        self.timfile = timfile

        if not os.path.isfile(parfile) or not os.path.isfile(timfile):
            raise IOError, "Cannot find parfile (%s) or timfile (%s)!" % (parfile,timfile)

        stdio.sprintf(parFile[0],"%s",<char *>parfile);
        stdio.sprintf(timFile[0],"%s",<char *>timfile);

        readParfile(self.psr,parFile,timFile,self.npsr);   # load the parameters    (all pulsars)
        readTimfile(self.psr,timFile,self.npsr);           # load the arrival times (all pulsars)

    def _readpars(self,fixangularerror=True,fixprefiterrors=True):
        cdef parameter *params = self.psr[0].param

        # create live proxies for all the parameters
        # and collect the prefit values of the parameters

        self.pardict = OrderedDict()
        self.prefit = OrderedDict()

        for ct in range(MAX_PARAMS):
            for subct in range(params[ct].aSize):
                if fixprefiterrors and not params[ct].fitFlag[subct]:
                    params[ct].prefitErr[subct] = 0

                newpar = create_tempopar(params[ct],subct)
                self.pardict[newpar.name] = newpar
                self.prefit[newpar.name] = prefitpar(newpar.name,
                                                     numpy.longdouble(params[ct].prefit[subct]),
                                                     numpy.longdouble(params[ct].prefitErr[subct]))

        for ct in range(1,self.psr[0].nJumps+1):  # jump 1 in the array not used...
            newpar = create_tempojump(&self.psr[0],ct)
            self.pardict[newpar.name] = newpar
            self.prefit[newpar.name] = prefitpar(newpar.name,
                                                 numpy.longdouble(self.psr[0].jumpVal[ct]),
                                                 numpy.longdouble(self.psr[0].jumpValErr[ct]))

        # TODO: it should also not be possible to replace or alter prefit,
        #       or to replace prefit.vals and prefit.errs

        self.prefit.vals = numpy.fromiter((self.prefit[par].val for par in self.pars),numpy.longdouble)
        self.prefit.vals.flags.writeable = False

        self.prefit.errs = numpy.fromiter((self.prefit[par].err for par in self.pars),numpy.longdouble)
        self.prefit.errs.flags.writeable = False

        # the designmatrix plugin also adds extra parameters for sinusoidal whitening
        # but they don't seem to be used in the EPTA analysis
        # if(pPsr->param[param_wave_om].fitFlag[0]==1)
        #     nPol += pPsr->nWhite*2-1;

    def _readflags(self):
        cdef int i, j

        # TO DO: make these attributes read only
        self.allflags = []
        self.flags = dict()

        for i in range(self.nobs):
            for j in range(self.psr[0].obsn[i].nFlags):
                flag = self.psr[0].obsn[i].flagID[j][1:]

                if flag not in self.allflags:
                    self.allflags.append(flag)
                    # the maximum flag-value length is hard-set in tempo2.h
                    self.flags[flag] = numpy.zeros(self.nobs,dtype='a32')

                self.flags[flag][i] = self.psr[0].obsn[i].flagVal[j]

    # TO DO: possibly set the name?
    property name:
        def __get__(self):
            return self.psr[0].name

    def __getitem__(self,key):
        return self.pardict[key]

    def __contains__(self,key):
        return key in self.pardict

    property pars:
        """Returns tuple of names of parameters that are fitted (deprecated, use fitpars)."""
        def __get__(self):
            return self.fitpars

    property fitpars:
        """Returns tuple of names of parameters that are fitted."""
        def __get__(self):
            return tuple(key for key in self.pardict if self.pardict[key].fit and key not in ['START','FINISH'])

    property setpars:
        """Returns tuple of names of parameters that have been set."""
        def __get__(self):
            return tuple(key for key in self.pardict if self.pardict[key].set)

    property allpars:
        """Returns tuple of names of all tempo2 parameters (whether set or unset, fit or not fit)."""
        def __get__(self):
            return tuple(self.pardict)

    property vals:
        """Returns (or sets from a sequence) a numpy longdouble vector of values of all parameters that are fitted (deprecated, use fitvals)."""
        def __get__(self):
            return self.fitvals

        def __set__(self,values):
            self.fitvals = values

    property errs:
        """Returns a numpy longdouble vector of errors of all parameters that are fitted."""
        def __get__(self):
            return self.fiterrs

    property fitvals:
        """Returns (or sets from a sequence) a numpy longdouble vector of values of all parameters that are fitted."""
        def __get__(self):
            ret = numpy.fromiter((self.pardict[par].val for par in self.fitpars),numpy.longdouble)
            ret.flags.writeable = False
            return ret

        def __set__(self,values):
            for par,value in zip(self.fitpars,values):
                self.pardict[par].val = value
                self.pardict[par].err = 0

    property fiterrs:
        """Returns a numpy longdouble vector of errors of all parameters that are fitted."""
        def __get__(self):
            ret = numpy.fromiter((self.pardict[par].err for par in self.fitpars),numpy.longdouble)
            ret.flags.writeable = False
            return ret

        def __set__(self,values):
            for par,value in zip(self.fitpars,values):
                self.pardict[par].err = value

    property setvals:
        """Returns (or sets from a sequence) a numpy longdouble vector of values of all parameters that have been set."""
        def __get__(self):
            ret = numpy.fromiter((self.pardict[par].val for par in self.setpars),numpy.longdouble)
            ret.flags.writeable = False
            return ret

        def __set__(self,values):
            for par,value in zip(self.setpars,values):
                self.pardict[par].val = value
                self.pardict[par].err = 0

    property seterrs:
        """Returns a numpy longdouble vector of errors of all parameters that have been set."""
        def __get__(self):
            ret = numpy.fromiter((self.pardict[par].err for par in self.setpars),numpy.longdouble)
            ret.flags.writeable = False
            return ret

    # the best way to access prefit pars would be through the same interface:
    # psr.prefit['parname'].val, psr.prefit['parname'].err, perhaps even psr.prefit.cols
    # since the prefit values don't change, it's OK for psr.prefit to be a static attribute

    property binarymodel:
        def __get__(self):
            return self.psr[0].binaryModel

    # number of active fit parameters
    property ndim:
        def __get__(self):
            return sum(self.pardict[par].fit for par in self.pardict if par not in ['START','FINISH'])

    property deleted:
        def __get__(self):
            cdef int [:] _deleted = <int [:self.nobs]>&(self.psr[0].obsn[0].deleted)
            _deleted.strides[0] = sizeof(observation)

            return (numpy.asarray(_deleted) == 1)
        def __set__(self,vals):
            cdef int [:] _deleted = <int [:self.nobs]>&(self.psr[0].obsn[0].deleted)
            _deleted.strides[0] = sizeof(observation)

            numpy.asarray(_deleted)[:] = vals[:]

    property telescope:
        def __get__(self):
            ret = numpy.zeros(self.nobs,dtype='a32')
            for i in range(self.nobs):
                ret[i] = self.psr[0].obsn[i].telID
                if ret[i] in aliases:
                    ret[i] = aliases[ret[i]]

            return ret

    # TOAs in days (numpy.longdouble array)
    def toas(self):
        cdef long double [:] _toas = <long double [:self.nobs]>&(self.psr[0].obsn[0].bat)
        _toas.strides[0] = sizeof(observation)

        updateBatsAll(self.psr,self.npsr)

        return numpy.asarray(_toas).copy()

    # site arrival times; divide residuals by 86400.0 to subtract
    property stoas:
        def __get__(self):
            cdef long double [:] _stoas = <long double [:self.nobs]>&(self.psr[0].obsn[0].sat)
            _stoas.strides[0] = sizeof(observation)

            return numpy.asarray(_stoas)

    # return TOA errors in microseconds (numpy.double array)
    property toaerrs:
        """Returns a (read-only) array of TOA errors in microseconds."""
        def __get__(self):
            cdef double [:] _toaerrs = <double [:self.nobs]>&(self.psr[0].obsn[0].toaErr)
            _toaerrs.strides[0] = sizeof(observation)

            return numpy.asarray(_toaerrs)

    # frequencies in MHz (numpy.double array)
    property freqs:
        def __get__(self):
            cdef double [:] _freqs = <double [:self.nobs]>&(self.psr[0].obsn[0].freq)
            _freqs.strides[0] = sizeof(observation)

            return numpy.asarray(_freqs)

    # residuals in seconds
    def residuals(self,updatebats=True,formresiduals=True):
        """Return a long-double numpy array of residuals (a private copy).
        Update TOAs and recompute residuals if updatebats = True (default) and
        formresiduals = True (default), respectively."""

        cdef long double [:] _res = <long double [:self.nobs]>&(self.psr[0].obsn[0].residual)
        _res.strides[0] = sizeof(observation)

        if updatebats:
            updateBatsAll(self.psr,self.npsr)
        if formresiduals:
            formResiduals(self.psr,self.npsr,1)     # 1 to remove the mean

        return numpy.asarray(_res).copy()

    def designmatrix(self,updatebats=True,fixunits=False):
        """Return the design matrix [nobs x (ndim+1)] for the current
        fit-parameter values; if fixunits=True, adjust the units
        of the design-matrix columns so that they match the tempo2
        parameter units."""

        cdef int fit_start  = self['START'].fit
        cdef int fit_finish = self['FINISH'].fit

        self['START'].fit = self['FINISH'].fit = False

        cdef int i
        cdef numpy.ndarray[double,ndim=2] ret = numpy.zeros((self.nobs,self.ndim+1),'d')

        cdef long double epoch = self.psr[0].param[param_pepoch].val[0]
        cdef observation *obsns = self.psr[0].obsn

        # the +1 is because tempo2 always fits for an arbitrary offset...
        cdef int ma = self.ndim + 1

        if updatebats:
            updateBatsAll(self.psr,self.npsr)

        for i in range(self.nobs):
            # for tempo2 versions older than, change to
            # FITfuncs(obsns[i].bat - epoch,&ret[i,0],ma,&self.psr[0],i)
            FITfuncs(obsns[i].bat - epoch,&ret[i,0],ma,&self.psr[0],i,0)

        self['START'].fit, self['FINISH'].fit = fit_start, fit_finish

        cdef numpy.ndarray[double, ndim=1] dev, err

        if fixunits:
            dev, err = numpy.zeros(ma,'d'), numpy.ones(ma,'d')

            fp = self.fitpars
            save = [self[p].err for p in fp]

            updateParameters(&self.psr[0],0,&dev[0],&err[0])
            dev[0], dev[1:]  = 1.0, [self[p].err for p in fp]

            for p,v in zip(fp,save):
                self[p].err = v

            for i in range(ma):
                ret[:,i] /= dev[i]

        return ret

    # run tempo2 fit
    # TO DO: see if the parameter-number mismatch is a problem
    def fit(self,iters=1):
        for i in range(iters):
            updateBatsAll(self.psr,self.npsr)
            formResiduals(self.psr,self.npsr,1)     # 1 to remove the mean

            doFit(self.psr,self.npsr,0)

        self.fitchisq = self.psr[0].fitChisq

    def chisq(self):
        res, err = self.residuals(), self.toaerrs

        return numpy.sum(res * res / (1e-12 * err * err))

    def rms(self):
        err = self.toaerrs
        norm = numpy.sum(1.0 / (1e-12 * err * err))

        return math.sqrt(self.chisq() / norm)

    # utility function
    def rd_hms(self):
        cdef char retstr[256]

        ret = {}
        for i,par in enumerate(self.parameters):
            if par[0] in ['RAJ','DECJ']:
                turn_hms(float(self.params[par[1]].val[par[2]]/(2*math.pi)),<char *>retstr)
                ret[par[0]] = retstr

        return ret['RAJ'], ret['DECJ']

    # legacy support; abs only
    def logL(self,dxs=None,abs=False):
        if dxs is not None:
            if not abs:
                raise NotImplementedError, 'pulsar.logL() works only with abs=True'

            self.vals = dxs

        return -0.5 * self.chisq()

    def savepar(self,parfile):
        cdef char parFile[MAX_FILELEN]

        if not parfile:
            parfile = self.parfile

        stdio.sprintf(parFile,"%s",<char *>parfile)

        # void textOutput(pulsar *psr,int npsr,
        #                 double globalParameter,  -- ?
        #                 int nGlobal,             -- ?
        #                 int outRes,              -- output residuals
        #                 int newpar, char *fname) -- write new par file
        textOutput(&(self.psr[0]),1,0,0,0,1,parFile)

    def savetim(self,timfile):
        cdef char timFile[MAX_FILELEN]

        if not timfile:
            timfile = self.timfile

        stdio.sprintf(timFile,"%s",<char *>timfile)

        writeTim(timFile,&(self.psr[0]),'tempo2');

def findpartim(pulsar,dirname='.',partimfiles=None):
    # this general setup may be more trouble than it's worth, but I'll leave it
    # in case it becomes useful in the future
    sets = {}
    sets['nanograv_12'] = {'dirname_par': '../nanograv/par',          'dirname_tim': '../nanograv/tim',
                           'parfile': pulsar + '_NANOGrav_dfg+12.par','timfile': pulsar + '_NANOGrav_dfg+12.tim'}
    sets['IPTA_13']     = {'dirname_par': '../IPTA/' + pulsar,        'dirname_tim': '../IPTA/' + pulsar,
                           'parfile': pulsar + '.par',                'timfile': pulsar + '_all.tim'}

    if partimfiles:
        if partimfiles in sets:
            parfile = dirname + '/' + sets[partimfiles]['dirname_par'] + '/' + sets[partimfiles]['parfile']
            timfile = dirname + '/' + sets[partimfiles]['dirname_tim'] + '/' + sets[partimfiles]['timfile']
        else:
            parfile = dirname + '/' + partimfiles.split(',')[0]
            timfile = dirname + '/' + partimfiles.split(',')[1]
    else:
        parfile = dirname + '/' + pulsar + '.par'
        timfile = dirname + '/' + pulsar + '.tim'

    if not os.path.isfile(parfile):
        raise IOError, "[ERROR] libstempo.findpartim: cannot find parfile {0}.".format(parfile)
    if not os.path.isfile(timfile):
        raise IOError, "[ERROR] libstempo.findpartim: cannot find timfile {0}.".format(timfile)

    return parfile, timfile

def rewritetim(timfile):
    import tempfile
    out = tempfile.NamedTemporaryFile(delete=False)

    for line in open(timfile,'r').readlines():
        if 'INCLUDE' in line:
            m = re.match('([ #]*INCLUDE) *(.*)',line)
            
            if m:
                out.write('{0} {1}/{2}\n'.format(m.group(1),os.path.dirname(timfile),m.group(2)))
            else:
                out.write(line)
        else:
            out.write(line)

    return out.name

def purgetim(timfile):
    lines = filter(lambda l: 'MODE 1' not in l,open(timfile,'r').readlines())
    open(timfile,'w').writelines(lines)

aliases = {}
if 'TEMPO2' in os.environ:
    for line in open(os.environ['TEMPO2'] + '/observatory/aliases'):
        toks = line.split()

        if '#' not in line and len(toks) == 2:
            aliases[toks[1]] = toks[0]
