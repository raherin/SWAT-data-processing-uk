'''script for processing midas weather data for SWAT'''
import pandas as pd
import glob as gb
import argparse

def getCmdArgs():
    '''get arguments passed by user'''
    p = argparse.ArgumentParser(description=("Select options for processing weather\
                                             data, inputs marked with '*' are required"))
    p.add_argument("-i","--input",dest="fdir",type=str, \
                   help=("*path to input directory"))
    p.add_argument("-o","--outname", dest="outname", type=str, 
                   help=("*name for the output station file name, \n \
                         refer to SWAT documentation for weather \n \
                         station file naming conventions"))
    p.add_argument("-c","--cols",dest="dcols",nargs="+",type=str, \
                   help=("*name of data columns you wish to extract \n \
                         separated by a space, must include timestamp column first"))
    p.add_argument("-dr","--drange", dest="drange",nargs='+' ,type=str, \
                   help="*start and end date of your desired output in \n \
                    'yyyymmdd' format, separated by a space")
    p.add_argument("-ti","--timein", dest="timein", default='D', type=str, \
                   help=("timestep of the data input: 'D' for daily and \n \
                         'H' for hourly, default is 'D'"))
    p.add_argument("--sum", action="store_true", \
                   help=("calculate the sum of data for each timestep \n \
                         instead of the mean"))
    
    cmdargs = p.parse_args()
    return cmdargs

def formatSWAT(fdir, outname, dcols, drange, step, sum):
    '''function to reformat weather station data for SWAT input'''
    tstamp=dcols[0] #get name of timestamp colum

    fNames = gb.glob('{}*.csv'.format(fdir)) #get list of files from the target directory
    print('Total files to process: ', len(fNames))

    drange = pd.date_range(start=drange[0], end=drange[1], freq='D') #set the date range for the output file
    drange = drange.strftime('%Y-%m-%d')

    df1 = pd.DataFrame(columns=dcols)
    df1[tstamp]=drange
    df1.set_index(tstamp, inplace=True) #set index to the date range column
    df1 = df1.fillna(-99) #fill in nodata values

    fcount=len(fNames)
    
    for i in fNames: #loop over weather data files and add data to output dframe
        print('processing ', i)
        with open(i,'r+') as f: #determine number of metadata rows to skip
            skp = 0
            for line in f:
                skp = skp+1
                if line.startswith(tstamp):
                    break
            skp = skp-1
        print('skipping over ',skp,' rows of metadata')
        
        df2 = pd.read_csv(i, skiprows=skp) #skip metadata rows
        endDat = df2[(df2[tstamp] =='end data')].index #find and drop the last row
        df2.drop(endDat, inplace=True)
        
        df2[tstamp] = pd.to_datetime(df2[tstamp], format=step) #convert timestamp to datetime
       
        df2.drop(columns=[col for col in df2 if col not in dcols], inplace=True) #drop unwanted columns
        df2.set_index(tstamp, inplace=True)#set timestamp to index
        
        if sum == True: #resample to daily sum or mean
            df2 = df2.resample('D').sum()
        else:
            df2 = df2.resample('D').mean()
        
        df1.update(df2) #add data to main dataframe
        fcount = fcount-1
        print(i,' added to dataframe, ',fcount,' files remaining')
    
    df1.to_csv(outname, mode='a',index=False,header=False, float_format="%.3f") #add data rows to the output file
        
    return


if __name__=="__main__":
    '''Get values from the parser'''    
    cmd = getCmdArgs()
    fdir = cmd.fdir 
    outname = cmd.outname
    dcols=cmd.dcols
    drange=cmd.drange
    step = cmd.timein
    sum = cmd.sum

    with open(outname, 'w') as f: #create the output file with the correct header for SWAT
        f.write(drange[0])
        f.write('\n')

    if step == 'D': #check if input is in day or hms timestamp
        step = '%Y-%m-%d'
    else:
        step = '%Y-%m-%d %H:%M:%S'
    
    formatSWAT(fdir, outname, dcols, drange, step, sum)
