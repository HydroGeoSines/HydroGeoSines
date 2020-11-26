# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 17:23:06 2020

@author: Daniel
"""

import numpy as np
import random
import scipy.stats as ss

#%%
class SGenerator(object):
    """
    Generate synthetic harmonic signal data (cosine)
    """
    def __init__(self, time_array: float):
        self.time = time_array
        
    def signal(self, amps, phases, freqs,snr = 1,nflag=True):
        harmonic = np.zeros(self.time.shape)
        for i in range(len(freqs)):
            harmonic = harmonic + (amps[i] * np.cos(2*np.pi*freqs[i]*self.time + phases[i]))   
        
        if nflag == True:    
            # SNR = var_signal / var_n  (power_sig / power_n)
            # Measured power of signal (W= V**2): power is basically the amplitude**2 of the signal
            pw_signal = harmonic.var()
            # Calculate required noise power for desired SNR
            pw_n = pw_signal / snr 
            kratio = np.sqrt(pw_n)
            if snr == np.inf:   
                kratio = 0
            # add gaussian noise 
            noise = np.random.normal(0, kratio, size=self.time.shape) # Generate noise with calculated power
            # signal plus noise    
            harmonic = harmonic + noise
        ## signal to noice converted to db
        #snr_db = (10*sp.log10(pw_signal/pw_n)) 
        #snr_out =  10.0 ** (snr_db / 10.0)
        #print ("Calculated SNR =  %f dB" % (10*sp.log10(pw_signal/pw_n)))
        #print (snr_out)
        return harmonic

class TGenerator(object):
    """
    Generate synthetic time arrays with gaps and offsets

    ...

    Attributes
    ----------
    var : dict
        a dictionary that contains all the input variables
    dist : dict
        a dictionary that contains distribution statistics
    gamma_tol : float
        tolerance of small gaps gamma distribution
        
    Methods
    -------
    large_gaps(percentage,n_gaps)
        Creates a number of large gaps with total sized based on array length
    small_gaps(mean,var,sgp)
        Creates small gaps with sizes based on a gamma distribution
    irreg_sfreq(s_int,n_freq)
        Creates changes in sampling frequency (spd) within the time array
    tshift(shift,n_shift)  
        Creates time shifts/offsets while keeping the spd
    """

    gamma_tol = 1e-5
    
    def __init__(self, days: int = 1, spd: int = 24):
        """
        Parameters
        ----------
        days : int
            the number of days the time array has (default 1)
        spd : int
            the number of samples per day the time array has (default 24)
        ng : int, optional
            the number of gaps in time array (default is 0)
        """
        self.var            = dict() # variables
        self.dist           = dict() # distributions
        self.var["days"]    = days
        self.var["spd"]     = spd 
        self.time = np.linspace(0, days, (days*spd), endpoint=False)
        
        ## some general gap parameters
        self.var["ng"]      = 0
        self.var["tgp"]     = 0.0
        self.gidx = np.array([]).astype(int)
                                      
    @staticmethod
    def consecutive(data, stepsize=1):
            return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)  
    
    # find index nearest to value
    @staticmethod
    def find_nearest(array,value):
        idx = np.argmin(np.array(np.abs(array-value)))
        return idx 
    
    @staticmethod
    def gaussian(array):
        xs = np.linspace(0, 1, len(array))
        res = (xs - xs.mean()) / xs.std() # normalize vector with mean = 0 and std = 1
        y = ss.norm.pdf(res, res.mean(), res.std()) # get probability density function
        return (y/np.sum(y))
    
    def tidx(self):
        return np.arange(0,len(self.time),1) # time vector indices 
    
    def proportion(self,gidx):
        return (len(gidx)/len(self.time))
    
    def gtimes(self,gidx):
        return np.array([self.time[x] for x in np.sort(gidx)])
    
    def rr(self,gr):
        """
        Calculates relative range of gaps
        
        ...
        
        Parameters
        ----------
        gr: array
            ratios of the gap sizes
        """    
        return ((gr.max() - gr.min())/gr.mean())*100 
        
    def large_gaps(self,percentage,n_gaps: int):
        """
        Parameters
        ----------
        percentage : float
            the percentage of time removed from array
        n_gaps : float
            number of gaps
        """                  
        
        # allow maximum of 95% gaps
        if (self.var["tgp"] + percentage) > 95:
            percentage = 95 - self.var["tgp"]
            print("Maximum of 95% gaps was exceeded. Percentage reduced to {0:1f}".format(percentage)) 
        
        gidx = self.gidx        
        tidx = self.tidx()
        nid = 0
        errstop = 0
        lgp = 0  # large gap percentage        
        lgr = [] # large gap ratios
        while nid < n_gaps: 
            # prevents endless looping at high percentage with many gaps
            if (errstop + n_gaps) > n_gaps**4:
                gidx, nid, lgp, errstop = self.gidx,0,0,0
                lgr     = []
            errstop +=1
            #print(errstop)
            # calculate and update gap proportions
            gdiri = np.random.dirichlet(np.ones(n_gaps-nid),size=1) # percentage size of each gap
            lg_prop = (percentage/100-lgp)*gdiri
            # exclude indices that are already occupied by gidx
            tidx = np.setdiff1d(tidx,gidx,assume_unique=True)
            # identify gap location and indice exceptions
            gap_loc     = np.int_(random.sample(list(tidx[1:-2]),1)) #first and last indices already excluded in N condition   
            gap_len     = lg_prop[0][0]*self.var["days"]
            gap_start   = np.float(self.time[gap_loc])
            # identify gap indices
            N = np.where((self.time > gap_start) & (self.time < (gap_start + gap_len)))[0] 
            if len(N) == 0: # prevents endless looping
                continue
            # make sure gap does not go beyond end of time array (gap_start+gap_len) and does not overlap with other gaps
            if ((gap_start + gap_len) < self.time[-2]) and (len(np.intersect1d(N,gidx)) == 0):          
                gidx = np.append(gidx,N) 
                #print(lg_prop[0][0]," vs theo percent: ", (time[N[-1]+1]-time[N[0]-1])/days)
                lg_prop = (self.time[N[-1]+1]-gap_start)/self.var["days"] # actual total gap length is updated
                lgp += lg_prop
                lgr = np.append(lgr,lg_prop)
                nid += 1
        
        ## save variables         
        gidx_l = np.setdiff1d(gidx,self.gidx,assume_unique=True)  
        self.gidx              = np.sort(gidx)
        self.gidx_l            = np.sort(gidx_l)       
        self.var["tgp"]       += (lgp*100) # total gap percentage in time
        self.var["lgn"]        = n_gaps
        self.var["ng"]        += n_gaps
        self.var["lgp"]        = lgp*100
        self.dist["lgr"]       = lgr      


    def small_gaps(self, mean: float ,var: float, sg_prop: float):  
        """
        Parameters
        ----------
        mean : float
            the mean of the gamma distribution for gap sizes (default 1)
        var : float
            the variance of the gamma distribution (default 1)
        sg_prop : float
            proportion (0-1) of total indices removed from array
        """       
        
        # allow maximum of 95% gaps
        tg_prop = self.proportion(self.gidx)
        if (tg_prop + sg_prop) > 0.95:
            sg_prop = 0.95 - tg_prop
            print("Maximum of 95% indice gaps was exceeded. Max sg_prop reduced to {0:3f}".format(sg_prop))

        tidx        = self.tidx()
        gidx        = self.gidx
        gidx_s      = np.array([]).astype(int)
        td          = np.diff(self.time) 
        
        ## create gamma pdf of gaps
        shape       = (mean/np.sqrt(var))**2
        scale       = (var/mean) 
        # gaps of size zero are excluded from the gamma distribution             
        gap_size    = np.arange(1, int(len(self.time)), 1)
        dist        = ss.gamma(a=shape, loc = 0, scale=scale)
        dist_pdf    = dist.pdf(gap_size) # percentage of each gap size
        gap_size    = gap_size[dist_pdf > self.gamma_tol]
        dist_pdf    = dist_pdf[dist_pdf > self.gamma_tol]
        
        ##  The dist_pdf may not sum up to 1 and has to be scaled
        #dist_sum = np.sum(dist_pdf)
        #check with np.sum(dist_pdf/np.sum(dist_pdf)) == 1
        dist_pdf = dist_pdf/np.sum(dist_pdf)
        dist_pdf     = sg_prop*dist_pdf
        sg_tuple    = [(gap_size[i],dist_pdf[i]) for i in range(len(dist_pdf))]
        # create biggest gaps first to optimize sampling
        sg_tuple    = sorted(sg_tuple, key=lambda t: t[0])[::-1] 
        n_gaps      = []
        n_tot       = 0
        errstop = 0
        for gsize, gp in sg_tuple: 
            gap_num     = np.int_(np.round((gp/gsize)*len(self.time),decimals=0))
            n_gaps = [gsize]*gap_num
            n_tot  += gap_num
            sid = 0
            # compromise between gamma distribution and sg_prop
            while (sid < len(n_gaps)) and (len(gidx_s)/len(self.tidx()) < sg_prop):
                
                #print(len(gidx_s)/len(self.tidx()) < sg_prop, len(gidx_s)/len(self.tidx()),sg_prop)
                # prevents endless looping at high percentage with many gaps
                if ((errstop + len(n_gaps)) > (len(n_gaps)+1)**2) and len(n_gaps) > 0:
                    #print("errstop")
                    gidx, errstop, sid = self.gidx,0,0
                    gidx_s  = np.array([]).astype(int)
                    tidx    = self.tidx()
                errstop +=1
                tidx        = np.setdiff1d(tidx,gidx,assume_unique=True)
                gap_loc     = np.int_(random.sample(list(tidx[1:-2]),1))[0]
                # exclude values before and after gap to make sure gaps dont overlap
                N           = np.arange(gap_loc-1,gap_loc+n_gaps[sid]+1,1) 
                if len(self.time)-((self.var["ng"]+n_tot)*2)-len(gidx): # if sg_prop is too big for amount of gaps
                    N       = np.arange(gap_loc,gap_loc+n_gaps[sid],1)
                if len(N) == 0:
                    continue    
                if (gap_loc + n_gaps[sid] < tidx[-1]) and (len(np.intersect1d(N,gidx)) == 0):
                    gidx    = np.sort(np.append(gidx, np.arange(gap_loc,gap_loc+n_gaps[sid],1)))
                    gidx_s = np.sort(np.append(gidx_s, np.arange(gap_loc,gap_loc+n_gaps[sid],1)))
                    sid     += 1 

        
        sgp = (sum([(td[x]+td[x-1])/2 for x in gidx_s])/self.var["days"])*100 
         
        self.gidx           = np.sort(gidx)
        self.gidx_s         = np.sort(gidx_s)
        self.var["tgp"]    += sgp 
        self.var["sgp"]     = sgp
        self.var["sgn"]     = n_tot
        self.var["ng"]     += n_tot
        self.var["sg_mean"] = mean
        self.var["sg_var"]  = var
        self.dist["sgr"]    = dist_pdf

    def irreg_sfreq(self,s_int,n_freq: int, gaussian = True):
        # check the existance of local gap variables
        self.var["nf"] = n_freq
        try:
            gidx    = self.gidx
            g_times = self.gtimes(gidx)
        except AttributeError:
            gidx    = np.array([]).astype(int)
            g_times = np.array([]).astype(int)
        #TODO: add gidx_s and gidx_l to freq and shift indexing of gaps
        if gaussian == True:
            yn = self.gaussian(s_int)       
        time = self.time
        
        tidx = np.array([x for x in self.tidx() if x not in gidx])
        d_times = np.array([time[x] for x in self.tidx() if x not in gidx])
        #if len(np.intersect1d(d_times,g_times)) == 0:
            #print("gap and time array are consistent")
               
        g_junks = self.consecutive(gidx,stepsize=1)
        d_junks = self.consecutive(tidx,stepsize=1)
        d_start = [time[d[0]] for d in d_junks]
        g_junks = [time[g] for g in g_junks]    
        
        #TODO: are changes in frequency also identified as gaps?!
        if n_freq > len(d_start): 
            #print("Warning! Not enough data gaps to match number of frequency changes. Instead, frequency changes are randomly distributed.")         
            d_start = d_times
                    
        for i in np.sort(random.sample(list(d_start), n_freq)):
            tmax = time[-1]
            if gaussian == True:
                td_new  = np.random.choice(s_int,1, p = yn)
            else:    
                td_new  = np.random.choice(s_int,1)
            t_loc = self.find_nearest(time,i)
            t_irr = np.arange(i, tmax+td_new, td_new)
            time = np.append(time[:t_loc],t_irr)
    
        # identify new gap locations
        if self.var["ng"] > 0:    
            g_times = []
            for gd in g_junks:
                g_times = np.append(g_times,(time[(time >= gd[0]) & (time <= gd[-1])])) 
        
            self.gidx = np.unique(np.array([self.find_nearest(time,g_times[x]) for x in range(len(g_times))])) 
            
        self.time       = time
        
    def tshift(self,shift,n_shift: int):
        self.var["ns"] = n_shift
        # check the existance of local gidx variable
        try:
            gidx    = self.gidx
        except AttributeError:
            gidx    = np.array([]).astype(int)
        
        time = self.time
        g_times = self.gtimes(gidx)
        tidx = np.array([x for x in self.tidx() if x not in gidx])
        
        d_junks = self.consecutive(tidx,stepsize=1)
        d_start = [time[d[0]] for d in d_junks]
                        
        sidx = np.zeros(len(time))
        
        if n_shift > len(d_start): 
            n_shift = len(d_start)
            print("Warning! Not enough data gaps for number of shifts. n_shift is set to {0:3d}".format(n_shift))         
            
        t_cor = 0 # make sure indices are also shifted in loop   
        for i in np.sort(random.sample(list(d_start), n_shift)):
            i += t_cor
            t_shift = np.random.choice(shift,1)  # in days
            t_loc = self.find_nearest(time,i)
            time = np.append(time[:t_loc],time[t_loc::] + t_shift)
            t_cor += np.copy(t_shift)
            sidx[t_loc::] = t_shift # shift identification vector            
        
        self.time, indices = np.unique(time,return_index=True) # make sure every time entry only exists once (due to find_nearest function and irregular shifts)   
        self.sidx = sidx[indices] # identify indices that need to be shifted      

        if self.var["ng"] > 0:
            g_times = g_times + [self.sidx[x] for x in gidx] # add shift to original gap_times
            self.gidx  = np.unique(np.array([self.find_nearest(time,g_times[x]) for x in range(len(g_times))]))   
            
                          
#%% Testing of Generators
"""
import matplotlib.pyplot as plt

a = syn_gen(days=50,spd=24)
print(len(a.time))


# IRREG
st = [5,10,15,30,60,120,240,360,480,720] # sampling interval in x/min (between 5/min to 4/day)
s_int = [i/(60*24.0) for i in st] #sampling interval in days
a.irreg_sfreq(s_int,4,gaussian=True)
print(len(a.time))

#a.large_gaps(20,3)
#print(len(a.gidx)/len(a.time))

#SMALL GAPS
a.small_gaps(2.1,1.1,0.5)


# SHIFT
shift = np.arange(1,60,1.0)/(24*60)
n_shift = 3
a.tshift(shift=shift,n_shift=n_shift)

print(len(a.gidx)/len(a.time))
print(a.var)
print("Small gap proportions is: {0:2f}".format(a.proportion(a.gidx_s)))
#print("Large and small gap proportions are: {0:2f}, {1:2f}".format(a.proportion(a.gidx_l),a.proportion(a.gidx_s)))
td = np.diff(a.time)
#Plotting
fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True) #12, 10

mask = np.ones(a.time.shape,dtype=bool)
mask[a.gidx.astype(int)] = False
y_ticks        = [-1, 0]
y_labels       = ["No","Yes"]

ax[0].scatter(a.time,mask*-1,s=2)
ax[0].set_yticks(y_ticks)
ax[0].set_yticklabels(y_labels)
ax[0].set_ylabel("Data Gap")

ax[1].plot(a.time[1::],np.round(td,decimals = 5))
ax[1].set_ylabel("Sampling frequency\n[$s * d^{-1}$]")
ax[1].set_yscale("log")

ax[2].plot(a.time,a.sidx*(24*60)) # plot shift in min
ax[2].set_ylabel("Frequency\noffset\n[min]")
ax[2].set_xlabel('Time [days]') 

# For signal
test_signal = SGenerator(a.time)
test_signal.signal([5],[1],[1])

"""