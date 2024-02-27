from math import sin, cos, sqrt, atan2, radians

R = 6378.137  # Föld sugara kilométerben
# Házhely
lat2 = 46.5778801  # Második pont szélessége
lon2 = 24.3791469  # Második pont hosszúsága

lat1 = 46.5778557  # Első pont szélessége
lon1 =  24.3766188  # Első pont hosszúsága

dLat = radians(lat2) - radians(lat1)
dLon = radians(lon2) - radians(lon1)

a = sin(dLat / 2) * sin(dLat / 2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2) * sin(dLon / 2)
c = 2 * atan2(sqrt(a), sqrt(1 - a))

d = R * c  # D az így kapott távolság
print(d*1000)  # távolság métereiben kiíratva
