# Technical scopes
Our goal is to implement generic and reusable plugin for PostGIS geospatial database or for GeoPandas with a purpose to allow developers community easily ensure differential privacy concept over geospatial data. Ensuring differential privacy in plugin will be applicable on geospatial data. So that the output from the geospatial database and after plugin executing will provide randomised geospatial data.

![](https://github.com/dancingsushii/geo-specific-diffpriv/blob/main/architecture.jpg)

Furthermore, this plugin will support five aggregation methods. After certain research we chose following methods: 
1) Geometric center
2) Bounding rectangle
3) Clustering of points ([DBSCAN]([http://localhost/](https://en.wikipedia.org/wiki/DBSCAN)))
4) Hexagons
5) Aggregation per administrative units

One of the basic requirements for testing and evaluation of the plugin is a proper dataset. Geospatial databases contain information describing objects linked to specific locations or surfaces. Geospatial data is usually a large set of data collected from many different sources such as weather data, census data, or social media data. This data becomes meaningful more often in an economic or social context, where it can be used to draw conclusions.

# Ealuation
In order to prove that our plugin performs as expected, we will use Google Cloud Platform for benchmarking performance. Apart from the key characteristic of reusability the benchmarking process should also prove that geospatial querying will output nearly the same result whether data is randomized or not.
