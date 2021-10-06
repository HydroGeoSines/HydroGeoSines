# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 11:30:00 2021

@author: Chris
"""

import hydrogeosines as hgs
import numpy as np
import matplotlib.pyplot as plt


# Create site object
site = hgs.Site('death valley', geoloc=[-116.471360, 36.408130, 688])

# Import data into site object
site.import_csv('tests/data/death_valley/Rau_et_al_2021.csv',
                 input_category=["GW","BP","ET"], utc_offset=0, unit=["m","m","nstr"],
                 how="add", check_duplicates=True)

# Obtain each time series as a numpy array
GW = np.array(site.data[site.data.category=='GW'].value)
BP = np.array(site.data[site.data.category=='BP'].value)
ET = np.array(site.data[site.data.category=='ET'].value)

# Manually define sampling period and frequency, for now
ps = 15./60./24. # 15 minute sampling period, converted to day units
fs = 1./ps # sampling frequency in cpd

# Manually create time elapsed vector, for now
t = np.arange(0., len(GW)*ps, ps)

# Create process object
process = hgs.Processing(site)

# Perform and plot autocorrelation analyses
GW_ac = hgs.ext.hgs_analysis.Time_domain.autocorrelation(GW)
plt.plot(t[:len(GW_ac)], GW_ac); plt.show()
BP_ac = hgs.ext.hgs_analysis.Time_domain.autocorrelation(BP)
plt.plot(t[:len(BP_ac)], BP_ac); plt.show()
ET_ac = hgs.ext.hgs_analysis.Time_domain.autocorrelation(ET)
plt.plot(t[:len(ET_ac)], ET_ac); plt.show()

# Perform and plot cross correlation analyses
GW_BP_cc = hgs.ext.hgs_analysis.Time_domain.crosscorrelation(GW, BP)
plt.plot(t[:len(GW_BP_cc)], GW_BP_cc); plt.show()
GW_ET_cc = hgs.ext.hgs_analysis.Time_domain.crosscorrelation(GW, ET)
plt.plot(t[:len(GW_ET_cc)], GW_ET_cc); plt.show()

# Perform and plot power spectral density analyses
f, GW_psd_welch = hgs.ext.hgs_analysis.Freq_domain.power_spectral_density(GW, fs, method='welch')
plt.plot(f, GW_psd_welch); plt.show()
f, GW_psd_bartlett = hgs.ext.hgs_analysis.Freq_domain.power_spectral_density(GW, fs, method='bartlett')
plt.plot(f, GW_psd_bartlett); plt.show()
#f, GW_psd_lombscargle = hgs.ext.hgs_analysis.Freq_domain.power_spectral_density(GW, method='lombscargle')
#plt.plot(f, GW_psd_lombscargle); plt.show()

# Perform and plot cross spectral density analyses
f, GW_BP_csd = hgs.ext.hgs_analysis.Freq_domain.cross_spectral_density(GW, BP, fs)
plt.plot(f, GW_BP_csd); plt.show()
f, GW_ET_csd = hgs.ext.hgs_analysis.Freq_domain.cross_spectral_density(GW, ET, fs)
plt.plot(f, GW_ET_csd); plt.show()

# Perform and plot coherence analyses
f, GW_BP_coh = hgs.ext.hgs_analysis.Freq_domain.coherence(GW, BP, fs)
plt.plot(f, GW_BP_coh); plt.show()
f, GW_ET_coh = hgs.ext.hgs_analysis.Freq_domain.coherence(GW, ET, fs)
plt.plot(f, GW_ET_coh); plt.show()

# Perform and plot spectrogram analyses
f, tau, GW_spec_stft = hgs.ext.hgs_analysis.Freq_domain.spectrogram(GW, fs, method='stft')
plt.pcolormesh(np.abs(GW_spec_stft)); plt.show()
plt.pcolormesh(np.unwrap(np.angle(GW_spec_stft))); plt.show()
f, tau, GW_spec_stft = hgs.ext.hgs_analysis.Freq_domain.spectrogram(GW, fs, method='welch')
plt.pcolormesh(np.abs(GW_spec_stft)); plt.show()
plt.pcolormesh(np.unwrap(np.angle(GW_spec_stft))); plt.show()
#f, tau, GW_spec_stft = hgs.ext.hgs_analysis.Freq_domain.spectrogram(GW, fs, method='cwt')
#plt.pcolormesh(np.abs(GW_spec_stft)); plt.show()
#plt.pcolormesh(np.unwrap(np.angle(GW_spec_stft))); plt.show()

# Calculate BE(f) using SISO method (Quilty and Roeloffs, 1991)
f, BE_SISO = hgs.ext.hgs_analysis.Freq_domain.BE_SISO(GW, BP, fs)
plt.plot(f, BE_SISO); plt.show()

# Calculate BE(f) using MISO method (Rojstaczer, 1988)
f, Hb, He = hgs.ext.hgs_analysis.Freq_domain.BE_MISO(GW, BP, ET, fs)
plt.plot(f, Hb); plt.show()
plt.plot(f, He); plt.show()


