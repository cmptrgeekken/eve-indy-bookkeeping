EVE SDE
=======

Simple EVE Online Static Data Export SQLite database wrapper for Python 2.7


### License ###

GPLv2


### Usage ###

```PYTHON
import evesde
sde = evesde.StaticDataExport('/path/to/sde.sqlite')

# item ID of Tritanium
print sde().invTypes(typeName='Tritanium').typeID

# border systems in Catch region
catch = sde().mapRegions(regionName='Catch').regionID
print [s.solarSystemName for s in sde().mapSolarSystems(regionID=catch, border=1)]
```
