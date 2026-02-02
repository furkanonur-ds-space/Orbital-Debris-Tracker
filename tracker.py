from skyfield.api import load, wgs84
import pandas as pd

stations_url = 'http://celestrak.org/NORAD/elements/stations.txt'
satellites = load.tle(stations_url)
iss = satellites['ISS (ZARYA)']
#print(iss)
ts = load.timescale()
t = ts.now()
geocentric = iss.at(t)
#print(geocentric.position.km)
subpoint = wgs84.subpoint(geocentric)
print(subpoint.latitude)
print(subpoint.longitude)
print(subpoint.elevation.km)

satellites_data = []



for i in satellites.values():

    geocentric = i.at(t)
    subpoint = wgs84.subpoint(geocentric)
    #print(subpoint.latitude.degrees)
    #print(subpoint.longitude.degrees)
    #print(subpoint.elevation.km)
    satellites_data.append({'name': i.name, 'latitude': subpoint.latitude.degrees, 'longitude': subpoint.longitude.degrees })

df = pd.DataFrame(satellites_data)
df = df.drop_duplicates(subset="name") 
print(df.head())