# generally accessible constants

const = {}
# pressure conversion constants
const['_pucf'] = {'m': 1, 'dm': 0.1, 'cm': 0.01, 'mm': 0.001, 'pa': 0.00010197442889221, 'hpa': 0.010197442889221, 'kpa': 0.10197442889221, \
         'mbar': 0.010197442889221, 'bar': 10.197442889221, 'mmhg': 0.013595475598539, 'psi': 0.70308890742557, 'ft': 1200/3937, 'yd': 3600/3937, 'inch': 0.0254}

# the most common Earth tide frequencies found in groundwater pressure (Merritt, 2004; McMillan et al., 2019)
const['_etfqs'] = {'Q1': 0.893244, 'O1': 0.929536, 'M1': 0.966446, 'P1': 0.997262, 'S1': 1.0, 'K1': 1.002738, 'N2': 1.895982, 'M2': 1.932274, 'S2': 2.0, 'K2': 2.005476}
# the most common atmospheric tide frequencies (McMillan et al., 2019)
const['_atfqs'] = {'P1': 0.997262, 'S1': 1.0, 'K1': 1.002738, 'S2': 2.0, 'K2': 2.005476}
