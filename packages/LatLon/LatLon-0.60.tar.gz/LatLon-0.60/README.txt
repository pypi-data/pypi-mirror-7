===========
LatLon
===========
---------------
Features
---------------
Methods for representing geographic coordinates (latitude and longitude) including the ability to:
    
    * Convert lat/lon strings from almost any format into a LatLon object
    
    * Automatically store decimal degrees, decimal minutes, and degree, minute, second information in a LatLon object
    
    * Output lat/lon information into a formatted string
    
    * Project lat/lon coordinates into some other proj projection
    
    * Calculate distances between lat/lon pairs using either the FAI or WGS84 approximation

----------------
Installation
----------------
*LatLon* has only been tested in Python 2.7

Installation through pip::

        $ pip install LatLon

Requires the following non-standard libraries:

     * *pyproj*

----------------
Usage Notes
----------------
Usage of *LatLon* is primarily through the class *LatLon*, which is designed to hold a single pair of *Latitude* and *Longitude* objects. Strings can be converted to *LatLon* objects using the method *string2latlon*, and to *Latitude* or *Longitude* objects using *string2geocoord*

Latitude or Longitude Construction
=========================================
Latitude of longitude construction is through the classes *Latitude* and *Longitude*, respectively. You can pass a latitude or longitude coordinate in any combination of decimal degrees, degrees and minutes, or degrees minutes and seconds. Alternatively, you can pass a formatted string using the function *string2geocoord* for a string containing a single latitude or longitude, or *string2latlon* for a pair of strings representing the latitude and longitude.

String formatting:
============================
*string2latlon* and *string2geocoord* both take a *formatter* string which is loosely modeled on the *format* keyword used in *datetime's* *strftime* function. Indicator characters (e.g. *H* or *D*) are placed between a specific separator character (*%*) to specify the way in which a coordinate string is formatted. Possible values are as follows:
          
          *H* is a hemisphere identifier (e.g. N, S, E or W)
          
          *D* is a coordinate in decimal degrees notation (e.g. 5.833)
          
          *d* is a coordinate in degrees notation (e.g. 5)
          
          *M* is a coordinate in decimal minutes notation (e.g. 54.35)
          
          *m* is a coordinate in minutes notation (e.g. 54)
          
          *S* is a coordinate in seconds notation (e.g. 28.93)
          
          Any other characters (e.g. ' ' or ', ') will be treated as a separator between the above components.
          
          All components should be separated by the *%* character. For example, if the coord_str is '5, 52, 59.88_N', the format_str would be 'd%, %m%, %S%_%H'

*Important*
===========
One format that will not currently work is one where the hemisphere identifier and a degree or decimal degree are not separated by any characters. For example  '5 52 59.88 N' is valid whereas '5 52 59.88N' is not.

String output:
=====================
Both *LatLon* and *Latitude* and *Longitude* objects include a *to_string()* method for outputting a formatted coordinate.

Projection:
=================
Use *LatLon.project* to transform geographical coordinates into a chosen projection. Requires that you pass it a *pyproj* or *basemap* projection.

Distance Calculation:
============================
*LatLon* objects have a *distance()* and *distance_sphere()* method which accepts a 2nd *LatLon* object as an argument. *distance()* will calculate the great-circle distance between the two coordinates using the WGS84 ellipsoid, and *distance_sphere()* will do the same using the more approximate FAI sphere.

--------------
Examples
--------------
Create a LatLon object using decimal degrees (simplest case)::

    >> palmyra = LatLon(Latitude(5.8833), Longitude(-162.0833)) # Location of Palmyra Atoll
    >> print palmyra.to_string('d% %m% %S% %H') # Print coordinates to degree minute second
    ('5 52 59.88 N', '162 4 59.88 W')

Create a Latlon object from a formatted string::

    >> palmyra = string2latlon('5 52 59.88 N', '162 4 59.88 W', 'd% %m% %S% %H')
    >> print palmyra.to_string('d%_%M') # Print coordinates as degree minutes separated by underscore
    ('5_52.998', '-162_4.998')

Perform some calculations::
	
    >> palmyra = LatLon(Latitude(5.8833), Longitude(-162.0833))
    >> honolulu = LatLon(Latitude(21.3), Longitude(-157.8167)) # Honolulu, HI
    >> print palmyra.distance(honolulu) # WGS84 distance
    1766.69130376
    >> print palmyra.distance_sphere(honolulu) # FAI distance
    1774.77188181
    
--------------
Version
--------------
0.60 - Not extensively tested. Please email me to let me know of any issues.

Changelog
============
**0.60 (AUGUST/27/2014)**

	* Added compatibility with comparison, negation, addition and multiplication magic methods

**0.50 (AUGUST/20/2014)**

	* First release