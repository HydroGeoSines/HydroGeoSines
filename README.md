<img src="https://github.com/HydroGeoSines/HydroGeoSines/blob/master/logo/HGS_v0.svg" width="400" />

## HydroGeoSines: Signals In the Noise Exploration Software (SINES) for Hydro-Geological datasets

HydroGeoSines (HGS) is a Python package that allows easy calculation of Barometric Efficiency (BE) and Barometric Response Functions (BRF) from standard groundwater monitoring datasets. This includes correction of groundwater heads that are affected by barometric and Earth tide influences. BE estimations include time-domain and frequency-domain solutions. BRF analysis is based on regression deconvolution allowing either the use of Earth tide time series or automatic estimation of the Earth tide signal. The implemented methods are based on peer-reviewed literature or expert technical reports. A number of useful pre-processing routines are also implemented. These include import, alignment and gap handling of groundwater, barometric pressure and Earth tide time series. Automatic pressure unit conversion to and from any accepted standard is handled. HGS can further automatically add theoretical Earth tides for any location on Earth because because it includes the [PyGTide](https://github.com/hydrogeoscience/pygtide) package.

Developed by:
* Gabriel C. Rau - Karlsruhe Institute of Technology (Germany) and UNSW Sydney (Australia)
* Daniel Schweizer - Karlsruhe Institute of Technology (Germany)
* Chris Turnadge - CSIRO (Australia)
* Todd Rasmussen - University of Georgia (USA)

### Example notebooks

[Groundwater head correction from Earth tides and atmospheric pressure](examples/Notebooks/Groundwater_head_correction.ipynb)

[Estimating hydraulic conductivity (K), specific storage (Ss) and barometric efficiency (BE)](examples/Notebooks/Estimation_of_K_Ss_BE.ipynb)

### Please note that HGS is currently under development!

If you want to help out, plese contact [Gabriel Rau](https://hydrogeo.science)

**Funding**: This project has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie Skłodowska-Curie grant agreement No 835852.

<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/">Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License</a>
