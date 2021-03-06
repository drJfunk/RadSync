import numpy as np
import matplotlib.pyplot as plt
from radsync_glue import electrons,  synchrotronPy, emission


class Synchronator(object):


    def __init__(self, Ngrid=500):
        self._Ngrid = Ngrid
        self._constFactor = 25352.525
        self._gammaFlag = False
    def SetParameters(self,ne , A,BG ,  gamma_min,  gamma_max,  index,  gamma_cool,silent=True):

        self._ne = ne
        self._A = A
        self._gamma_min = gamma_min
        self._gamma_max = gamma_max
        self._index = index
        self._BG = BG 
        
        self._syncCool = 1./(A*A*self._constFactor)  
        
        
        self._DT = self._syncCool/(gamma_max/1.)
        #mincool = self._syncCool/(gamma_min/1.)
        #print mincool
        self._steps = np.round(gamma_max/gamma_cool)

        
        if not silent:
            print "Cooling electrons...\n"
            print "Synchrotron cooling time is %.2e s"%self._syncCool
            print "Time step is for %.2e s"%self._DT
            #print self._syncCool / gamma_max
        

        step = np.exp(1./self._Ngrid*np.log(gamma_max*1.1))

        self._gamma = np.power(step,np.arange(self._Ngrid))
        self._gammaFlag = True


        #if not silent:
        #    print "Emitted %.3f percent of the indejected energy"%(100.*(1.-self._epsilon(steps)))

               
    def GetEmisson(self,ene):
        if self._gammaFlag:
            norm = self._BG * self._A *3.7797251E-22
            erg2keV = 6.242E8
            if self._steps ==0:
                return np.zeros_like(ene)
            return erg2keV*norm*np.array(emission(ene,
                                       self._ne,
                                       self._A,
                                       self._BG,
                                       self._gamma_min,
                                       self._gamma_max,
                                       self._index,
                                       self._DT,
                                       self._Ngrid,
                                       self._steps))
        else:
            print "No Parameters Set!"
            return

  

    def GetGammaGrid(self):
        return self._gamma

    def GetGammaDist(self):
        self._fgammma = np.array(electrons(self._ne, self._A,  self._gamma_min,  self._gamma_max,  self._index,  self._DT,  self._Ngrid, self._steps ))
        return self._fgammma
   


    def _Source(self,gamma):

        
        if (self._gamma_min<=gamma and gamma<=self._gamma_max):

            return self._ne*np.power(gamma,-self._index) * (1-self._index)* 1./ (np.power(self._gamma_max,1-self._index)-np.power(self._gamma_min,1-self._index))
        else:
            return 0

    def _epsilon(self,steps):


        N = self._Ngrid
        y=np.zeros(N)
        for i in range(N):
                
            y[i] = self._gamma[i] * self._Source(self._gamma[i])
            #y[i] = self._Source(self._gamma[i])
            
    
        s = y[0] + 2.0 * y[1:N-1].sum() + y[N-1]
        h = float(self._gamma[-1] - self._gamma[0]) / N
            
        sourceIntegral = s * h / (2.0)

        y=np.zeros(N)
        for i in range(N):
                
            y[i] = self._gamma[i] * (self._Source(self._gamma[i]) -  self._fgammma[i])
            #y[i] =  (self._Source(self._gamma[i]) -  self._fgammma[i])
            
            
    
        s = y[0] + 2.0 * y[1:N-1].sum() + y[N-1]
        h = float(self._gamma[-1] - self._gamma[0]) / N
            

        finalIntegral = s * h / (2.0)

#        print finalIntegral
#        print sourceIntegral
        
        return finalIntegral/((1.)*sourceIntegral)
