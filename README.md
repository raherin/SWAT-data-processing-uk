# SWAT-data-processing-uk
Python scripts to help in processing UK weather data for SWAT and SWAT+ modelling

## Overview
I created this project as part of my [dissertation research](https://www.geos.ed.ac.uk/~mscgis/22-23/s2434646/) to create a hydrologic model of the River Brora using the Soil and Water Assessment Tool (SWAT). In order to prepare climate data for the project, I needed to process a large number of climate station data files from the Met Office [MIDAS](https://catalogue.ceda.ac.uk/uuid/dbd451271eb04662beade68da43546e1) database into station data files used by [SWAT and SWAT+](https://swat.tamu.edu/software/). I wrote the `processWeather.py` script to process these files in batches by station and climate reading type.

Due to the unavailability of accurate radiation data for the study catchment, I also needed to read evapotranspiration (ET) data into the model. I wrote the `getpet.py` script to extract a timeseries of ET data for a single coordinate location from a batch of NetCDF files from the UKCEH [CHESS-PE](https://catalogue.ceh.ac.uk/documents/9116e565-2c0a-455b-9c68-558fdd9179ad) dataset.

## Requirements
Both scripts require the user to have Python installed on their system.

### processWeather.py

The user should download the weather data from MIDAS so that the file directory is organized by station and climate variable. For example, in this project there was a folder for precipitation, within that directory was a folder for each station used for precipitation readings which contained all the precipitation files for the station. This is the same directory structure that the files will be in if an FTP service is used to download the station variables in bulk from the MIDAS server.

### getpet.py

The CHESS-PE data is stored in NetCDF files where each file contains one month's worth of data for the whole of the UK in 1km grid format. Each file will have a separate band for each day of the month.

The timestamp data in the NetCDF file represents 'number of days since 01-01-1961'. The `getpet.py` script will convert this into the correct date format for SWAT.

## How to use

### processWeather.py
The user will need to specify the name of the output file, using the naming convention recommended by the SWAT documentation. They will also need to look at the MIDAS file to determine which columns contain the data they wish to extract. In order to format the data correctly, use the following command line options to instruct the script to create the correct output:

| **Option** | **Description** |
|       ---: | :---            |
| `-h, --help` | show help menu |
| `-i, --input` | path to input file directory (required) |
| `-o, --outname` | output file path, should follow SWAT documentation for naming conventions (required) |
| `-c, --cols` | name of data columns to extract from MIDAS file, separated by a space, must include timestamp column first (required) |
| `-dr, --drange` | start and end date of desire output in 'yyyymmdd' format, separated by a space (required) |
| `-ti, timein` | timestep of the data input: 'D' for daily and 'H' for hourly, default is 'D' |
| ` --sum` | calculate the sum of data for each day instead of the mean (disabled by default) |

The following is an example command shell usage of the `processWeather.py` script:

```
	$ python3 processWeather.py --input temp/00048_kinbrace-hatchery/qc-version-1/ -o swat_weather/kinbracetmp.txt -c ob_end_time max_air_temp min_air_temp -dr 20010101 20171231 -ti H
```

This command would create an output file titled `kinbracetmp.txt` in the `swat_weather` folder. The file would contain the minimum and maximum mean temperatures for each day from 01-01-2001 to 31-12-2017. 

The script works by creating the output file indicated by the user and putting the first date in the time series in the first line of the file, as specified by SWAT+ requirements, it then creates a Pandas dataframe with the requested output columns to store the time series data and fills it with -99 values(these are used by SWAT so it can use its built in weather generator to fill in data gaps). The script then loops over each file in the target directory, resampling the data to the requested daily outputs and updates the dataframe with the values extracted from the file. Once all of the files have been read into the dataframe, the data columns are written into the output file.

### getpet.py

This script will create a file named `pet.cli` which needs to be put in the `TextInOut` folder that is created after the first run of the SWAT model in SWAT+ Editor. The folder can be found in the project directory under the path `/Scenarios/Default/TextInOut`. The script requires the user to declare the path to the NetCDF files to be processed and the desired coordinates for the time series data in EPSG 27700 format. It is recommended to use a coordinate that is within the catchment boundary.

| **Option** | **Description** |
| ---: | :--- |
| `-i, --input` | path to directory of NetCDF files to be processed |
| `--lat` | northing of desired coordinates for time series data |
| `--lon` | easting of desired coordinates for time series data |

The following is an example command line usage of the `getpet.py` script:

```
$ python3 getpet.py --i pet/ --lat 916217 --lon 274515
```
