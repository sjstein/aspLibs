from json import loads
from time import sleep
from urllib2 import Request, urlopen
import csv
import sys
import winsound

API_KEY = 'AIzaSyFq-MWZR7YFVd5NLan5ZyrNeoZi2H4tBis'
#NOTE: Above code will NOT work - it just shows the format on how to store your own API key

frequency = 2600  # Set Frequency To 2600 Hertz (ha!)   : For end of run sound
duration = 1000  # Set Duration To 1000 ms == 1 second  : For end of run sound

fname = sys.argv[1].replace('.txt','')
if len(sys.argv) > 2:       # API Key has been put on command line
    API_KEY = sys.argv[2]   # Read second argument as API key
lat = [0]
lon = [0]
dat = [0]
tim = [0]
dep = [0]

outputFile = open(fname + '_depth.txt','w')
with open(fname + '.txt') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            lat[0]=row[0]
            lon[0]=row[1]
            dat[0]=row[2]
            tim[0]=row[3]
            locations = [(lat[0],lon[0])]
            line_count += 1
            for loc in locations:
                requestStr='https://maps.googleapis.com/maps/api/elevation/json?locations={0},{1}&key='+API_KEY
                request = Request(requestStr.format(loc[0], loc[1]))
                response = urlopen(request).read()
                places = loads(response)
                print 'At {0} elevation is: {1}'.format(loc, places['results'][0]['elevation'])
                dep[0] = places['results'][0]['elevation']
                outputFile.write(str(lat[0]) + ',' + str(lon[0]) + ',' + str(dat[0]) + ',' + str(tim[0]) + ',' + str(dep[0]) + '\n')
                sleep(1)
        else:
            lat.append(row[0])
            lon.append(row[1])
            dat.append(row[2])
            tim.append(row[3])

            locations = [(lat[line_count], lon[line_count])]
            for loc in locations:
                requestStr='https://maps.googleapis.com/maps/api/elevation/json?locations={0},{1}&key='+API_KEY
                request = Request(requestStr.format(loc[0], loc[1]))
                response = urlopen(request).read()
                places = loads(response)
                print 'At {0} elevation is: {1}'.format(loc, places['results'][0]['elevation'])
                dep.append(places['results'][0]['elevation'])
                i=line_count
                outputFile.write(str(lat[i]) + ',' + str(lon[i]) + ',' + str(dat[i]) + ',' + str(tim[i]) + ',' + str(dep[i]) + '\n')
                line_count += 1
                sleep(1)
        print('processed set # ' + str(line_count) )

csv_file.close()
outputFile.close()
winsound.Beep(frequency, duration)
print('Output finished with ' + str(line_count) + ' depths discovered')
