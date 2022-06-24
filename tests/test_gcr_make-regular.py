import hydrogeosines as hgs
import numpy as np
import pandas as pd

#%%  Testing MVC principal
data = hgs.Site('csiro', geoloc=[141.73099, -31.2934, 160])

data.import_csv('tests/data/tobiah_adj.csv', 
                        input_category=['BP', 'GW', 'GW'], 
                        utc_offset = 10, 
                        unit=['kpa', 'm', 'm'], 
                        loc_names = ["Baro", "Loc-1", "Loc-2"],
                        how="add", check_duplicates=True, dayfirst=False)

#%%
process = hgs.Processing(data)
process.describe()

#%%
process.fft()
