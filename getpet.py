'''A python script to extract a timeseries of evapotranspiration from a set coordinates'''
import datetime
import numpy as np
from netCDF4 import Dataset
import argparse
import pandas as pd
import glob as gb

def getCmdArgs():
    '''get arguments passed by user'''
    p = argparse.ArgumentParser(description=("Select options for processing PET files"))
    p.add_argument("-i","--input",dest="fdir",type=str, \
                   help=("path to input directory"))
    p.add_argument("--lat",dest="lat", type=int, default=916217, \
                   help="northing of desired coordinate for timeseries")
    p.add_argument("--lon",dest="lon", type=int, default=274515, \
                   help="easting of desired coordinate for timeseries")
    
    cmdargs = p.parse_args()
    return cmdargs

def pet_timeseries(fdir,lon,lat):
    '''create dataframe with indexed date range'''
    
    fnames = gb.glob('{}*.nc'.format(fdir)) # get names of files in the target directory

    '''create empty arrays to store year, julian date and PET values'''
    dfyear = [] 
    dfdate = []
    dfpet = []

    for n in fnames:
        nc_fid = Dataset(n, 'r') #read file to dataset

        '''read the values from the file'''
        lons = nc_fid.variables['x'][:]
        lats = nc_fid.variables['y'][:]
        pet = nc_fid.variables['pet'][:]
        time = nc_fid.variables['time_bnds'][:,0]

        '''convert the date to julian'''
        time = nc_fid.variables['time_bnds'][:,0]
        epoch = datetime.datetime(1961,1,1)
        dat = [epoch+datetime.timedelta(days=t) for t in time]
        date = [d.timetuple().tm_yday for d in dat]
        year = [d.timetuple().tm_year for d  in dat]

        '''search for the timeseries 
        data from the given coords'''
        lons_idx = np.abs(lons - lon).argmin()
        lats_idx = np.abs(lats - lat).argmin()
        bpet = pet[:, lats_idx,lons_idx]

        '''append values to the main arrays'''
        for y in year:
            dfyear.append(y)
        del year
        for d in date:
            dfdate.append(d)
        del date
        for p in bpet:
            dfpet.append(float(p))
        del bpet
        del nc_fid

    '''create dataframe using values from the arrays as columns'''    
    petdf = pd.DataFrame(columns=['year','date','pet'])
    petdf['year'] = dfyear
    petdf['date'] = dfdate
    petdf['date'] = petdf['date'].apply(str)
    petdf['date'] = petdf['date'].str.pad(3, side='left', fillchar='0') #format julian date so SWAT can read it
    petdf['pet'] = dfpet
    
    petdf = petdf.sort_values(['year','date'], ascending=[True,True]) #arrange values in chronological order
    petdf['pet'] = petdf['pet'].apply(float) #float pet values
    petdf.to_csv('pet.cli',mode='a',index=False, float_format='%.3f', sep=' ') #print the output file in the format required by SWAT


if __name__=="__main__":
    cmd = getCmdArgs()
    fdir = cmd.fdir
    lon = cmd.lon
    lat = cmd.lat

    with open('pet.cli', 'w') as f: #create the output file with the correct header for SWAT
        f.write('pet.cli \n') #SWAT doesn't read the file correctly without these lines
        f.write('line2 \n')
        f.write('line3 \n') 
    pet_timeseries(fdir,lon,lat)
