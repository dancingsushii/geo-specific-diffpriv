# How to use this proxy

In order to test our solution, the following steps have to be done. Python 3 is required (we are using Python 3.9.12) as well as pip (we are using pip 21.2.4).

1. Clone the repository into a folder and go inside the folder with the command:
```
cd geo-specific-diffpriv
```
2. Create a virtual environment and start it with the folowing 2 commands (on MacOS):
```
virtualenv venv
source venv/bin/activate
```
3. Install the required python libraries:
```
pip install -r requirements.txt
```
4. Run the program with the command:
```
python3 client_interface.py
```

## Query parameters

The main method that is calling all the functions for differentially privacy is:
```
client_request(SQLquery, privacy_budget)
```
The parameters can be changed for testing purposes. Some rules are below.

1. SQL query

SQL query has to be a correct SQL query with select and from parts and a semicolon at the end (Postgres rule). Moreover, depending on the query, different aggregation functions are used:

- ST_Envelope - bounding box
- ST_Centroid - geometric center

2. Privacy budget

At the moment the chosen budget is 0.1 as per the paper "Node Location Privacy Protection Based on Differentially Private Grids in Industrial Wireless Sensor Networks" by Jun Wang, Rongbo Zhu, Shubo Liu and Zhaohui Cai (2018).

# Jupyter notebook

Alternatively, Jupyter Notebook [geo_dp_proxy.ipynb](https://github.com/dancingsushii/geo-specific-diffpriv/blob/main/geo_dp_proxy.ipynb) can be used to run the code.

# How to manually setup PostGIS

For instructions on how to manually setup PostGIS in your host/VM, please check [README.postgis.md](https://github.com/dancingsushii/geo-specific-diffpriv/blob/main/README.postgis.md)


# Technical scopes of this project
Our goal is to implement generic and reusable plugin for PostGIS geospatial database or for GeoPandas with a purpose to allow developers community easily ensure differential privacy concept over geospatial data. Ensuring differential privacy in plugin will be applicable on geospatial data. So that the output from the geospatial database and after plugin executing will provide randomised geospatial data.

Furthermore, this plugin will support two aggregation methods. After certain research we chose following methods: 
1. Geometric center
2. Bounding rectangle


One of the basic requirements for testing and evaluation of the plugin is a proper dataset. Geospatial databases contain information describing objects linked to specific locations or surfaces. Geospatial data is usually a large set of data collected from many different sources such as weather data, census data, or social media data. This data becomes meaningful more often in an economic or social context, where it can be used to draw conclusions.

# Evaluation
In order to prove that our plugin performs as expected, we will use YCSB for benchmarking performance. Apart from the key characteristic of reusability the benchmarking process should also prove that geospatial querying will output nearly the same result whether data is randomized or not.
