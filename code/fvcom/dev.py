from shapely.geometry import shape
from shapely.geometry import MultiPolygon, Polygon
import shapely.speedups
shapely.speedups.enable()
import geojson
import numpy as np
from scipy.interpolate import griddata
from matplotlib.path import Path
import matplotlib.pyplot as plt
import math, os, json, codecs, sys
np.set_printoptions(threshold=sys.maxsize)

# load data (x.npy (non-grid mesh), y.npy (non-grid mesh), temp3D.npy (point,layer,day))
x = np.load('x.npy').reshape(2005,)
y = np.load('y.npy').reshape(2005,)
z = np.load('temp3D.npy')

# determine non-grid mesh bounds and temp range
yMax=np.amax(y)
yMin=np.amin(y)
xMax=np.amax(x)
xMin=np.amin(x)
zMax=np.amax(z)
zMin=np.amin(z)

print(zMax,zMin)
# 7.506698131561279 0.6350017905792342

# create grid from mesh
xi = np.arange(xMin,xMax,0.025) # <- ~2.2km; what should resolution be?
yi = np.arange(yMin,yMax,0.025)
xi2,yi2 = np.meshgrid(xi,yi) # array of [lon rows and col],[lat rows and col]



# generate gridded data volume

# reshape data array from (point,layer,day) to (day,layer,point)
zAll=np.array(z)
zAll2= np.flip(np.rot90(zAll, 1, (2,0)),axis=2)


# generating all layers for all days
ziArrayAll=[]
for index1 in enumerate(zAll2):
    ziArrayDay=[]
    for index2 in enumerate(zAll2[index1[0]]):
        zi = griddata((x,y),zAll2[index1[0]][index2[0]],(xi2,yi2),method='linear')  

        """
        # create un-masked interpolated png plots for Day 0, all layers
        if index1[0]==0:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            plt.contourf(xi,yi,zi,np.arange(zMin,zMax,0.01))
            #plt.plot(x,y,'k.')
            #plt.plot(xi,yi,'k.')
            plt.xlabel('xi',fontsize=16)
            plt.ylabel('yi',fontsize=16)
            plt.savefig('interpolated'+str(index2[0])+'.png',dpi=100)
            plt.close(fig)
        """

        ziArrayDay.append(zi)
    ziArrayAll.append(ziArrayDay)
ziArrayAll2=np.asarray(ziArrayAll)


"""
# generating all layers for day 0
ziArrayDay=[]
for index2 in enumerate(zAll2[0]):
    zi = griddata((x,y),zAll2[0][index2[0]],(xi2,yi2),method='linear') # generating all layers for day 0 
    ziArrayDay.append(zi)
ziArrayAll2=np.asarray(ziArrayDay)
"""


# find relevant land mask polygons and mask data

xi2yi2 = np.dstack((xi2,yi2)) # array of [lon lat] rows and columns
xi2yi2_flat = xi2yi2.reshape((-1, 2)) # array of [lon lat] as a single column

geo2: dict = {'type': 'Polygon',
   'coordinates': [[[xMax,yMin],[xMax,yMax],[xMin,yMax],[xMin,yMin],[xMax,yMin]]]}
polygon2: Polygon = shape(geo2)

"""
source for land_mask_USA.json
https://mit.maps.arcgis.com/apps/mapviewer/index.html?layers=615e85efe40845718cd0d1ece1966a8b&layerId=91
https://services.arcgis.com/jIL9msH9OI208GCb/arcgis/rest/services/Ocean_and_Country_Polygon_Masks/FeatureServer/91
"""
with open('land_mask_USA.json') as f:
    gj = geojson.load(f)

for index in enumerate(gj['features']):
    for index2 in enumerate(gj['features'][index[0]]['geometry']['coordinates']):   
        geo1: dict = {'type': 'Polygon',
            'coordinates': gj['features'][index[0]]['geometry']['coordinates'][index2[0]] }
        polygon1: Polygon = shape(geo1)
        if polygon1.intersects(polygon2): # if land mask polygon iterative (polygon1) intersects grid bounds (polygon2)
            if polygon1.intersection(polygon2).type=='MultiPolygon':
              intersection=polygon1.intersection(polygon2)
              for polygon in intersection.geoms:
                if polygon.intersects(polygon2): 
                    mpath = Path(polygon.exterior.coords)
                    # create binary mask
                    mask_flat = mpath.contains_points(xi2yi2_flat)
                    mask=mask_flat.reshape(xi2.shape)
                    print('using multipolygon mask '+str(index[0])+' '+str(index2[0]))
                    # iterate through every row,col of gridded data to check if point is in land mask polygon iterative, and if so, assign mask value
                    for indexRow in enumerate(xi2yi2):
                        for indexCol in enumerate(xi2yi2[indexRow[0]]):
                            for indexDay in enumerate(ziArrayAll2):
                                for indexLyr in enumerate(ziArrayAll2[indexDay[0]]):
                                    #if mpath.contains_point(xi2yi2[indexRow[0]][indexCol[0]]) or math.isnan(ziArrayAll2[indexDay[0]][indexLyr[0]][indexRow[0]][indexCol[0]]):
                                    if mask[indexRow[0]][indexCol[0]]==True or math.isnan(ziArrayAll2[indexDay[0]][indexLyr[0]][indexRow[0]][indexCol[0]]):
                                        # assign mask value to every layer and day for point
                                        ziArrayAll2[indexDay[0]][indexLyr[0]][indexRow[0]][indexCol[0]]=-32767
                            """
                            #masking for day 0
                            for indexLyr in enumerate(ziArrayAll2):
                              if mask[indexRow[0]][indexCol[0]]==True or math.isnan(ziArrayAll2[indexLyr[0]][indexRow[0]][indexCol[0]]):
                                    # assign mask value to every layer and day for point
                                    ziArrayAll2[indexLyr[0]][indexRow[0]][indexCol[0]]=-32767
                            """

            else:
              mpath = Path(gj['features'][index[0]]['geometry']['coordinates'][index2[0]][0]) # the vertices of the polygon
              # create binary mask
              mask_flat = mpath.contains_points(xi2yi2_flat)
              mask=mask_flat.reshape(xi2.shape)
              print('using mask '+str(index[0])+' '+str(index2[0]))
              # iterate through every row,col of gridded data to check if point is in land mask polygon iterative, and if so, assign mask value
              for indexRow in enumerate(xi2yi2):
                  for indexCol in enumerate(xi2yi2[indexRow[0]]):
                      for indexDay in enumerate(ziArrayAll2):
                          for indexLyr in enumerate(ziArrayAll2[indexDay[0]]):
                              #if mpath.contains_point(xi2yi2[indexRow[0]][indexCol[0]]) or math.isnan(ziArrayAll2[indexDay[0]][indexLyr[0]][indexRow[0]][indexCol[0]]):                              if mask[indexRow[0]][indexCol[0]]==True or math.isnan(ziArrayAll2[indexDay[0]][indexLyr[0]][indexRow[0]][indexCol[0]]):
                              if mask[indexRow[0]][indexCol[0]]==True or math.isnan(ziArrayAll2[indexDay[0]][indexLyr[0]][indexRow[0]][indexCol[0]]):
                                  # assign mask value to every layer and day for point
                                  ziArrayAll2[indexDay[0]][indexLyr[0]][indexRow[0]][indexCol[0]]=-32767
                      """
                      #masking for day 0
                      for indexLyr in enumerate(ziArrayAll2):
                        if mask[indexRow[0]][indexCol[0]]==True or math.isnan(ziArrayAll2[indexLyr[0]][indexRow[0]][indexCol[0]]):
                              # assign mask value to every layer and day for point
                              ziArrayAll2[indexLyr[0]][indexRow[0]][indexCol[0]]=-32767
                      """

for indexDay in enumerate(ziArrayAll2):

    print('creating file for day '+str(indexDay[0]))

    # concatenate all rows in each layer array
    ziArrayAll2Concat=[]
    for indexLyr in enumerate(ziArrayAll2[indexDay[0]]):
        ziArrayAll2ConcatLayer=np.concatenate(ziArrayAll2[indexDay[0]][indexLyr[0]])
        ziArrayAll2Concat.append(ziArrayAll2ConcatLayer)
    ziArrayAll2Concat2=np.asarray(ziArrayAll2Concat)

    # filename='temp3D_covjson_'+str(indexDay[0])+'.json'

    # file_path_covjson=os.path.join(os.path.dirname('__file__'),'masked_covjson/'+filename)
    file_path_png=os.path.join(os.path.dirname('__file__'),'masked_png/')

    json_response={}

    layers=[]
    for indexLyr in enumerate(ziArrayAll2Concat2):
        json_response_layer = {
          "layer_id": str(indexDay[0])+'_'+str(indexLyr[0]),
          "type": "Coverage",
          "domain": {
            "type" : "Domain",
            "domainType": "Grid",
            "axes": {
              "x": {
                "values": xi.tolist()
              },
              "y": {
                "values": yi.tolist()
              }
            },
            "referencing": [{
              "coordinates": ["x", "y"],
              "system": {
                "type": "GeographicCRS",
                "id": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
              }
            }]
          },
            "parameters": {
              "sst": {
                "type": "Parameter",
                "description": {
                  "en": "Sea Surface Temperature"
                },
                "unit": {
                  "label": {
                    "en": "degree_C"
                  }
                },
                "symbol": {
                  "value": "degree_C",
                  "type": "http://www.opengis.net/def/uom/UCUM/"
                },
                "observedProperty": {
                  "label": {
                    "en": "Sea Surface Temperature"
                  }
                }
              }
          },
          "ranges": {
            "sst": {
              "type": "NdArray",
              "dataType": "float", 
              "axisNames": ["y", "x"],
              "shape": [yi.shape[0],xi.shape[0]],
              "values": ziArrayAll2Concat2[indexLyr[0]].tolist()
            }
          }
        }
        layers.append(json_response_layer)

        # create masked interpolated png plots for all days, all layers
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.contourf(xi,yi,ziArrayAll2[indexDay[0]][indexLyr[0]],np.arange(zMin,zMax,0.01))
        #plt.plot(x,y,'k.')
        #plt.plot(xi,yi,'k.')
        plt.xlabel('xi',fontsize=16)
        plt.ylabel('yi',fontsize=16)
        plt.savefig(file_path_png+'interpolated'+str(indexDay[0])+'_'+str(indexLyr[0])+'.png',dpi=100)
        plt.close(fig)
"""
    json_response = {
      "layers" : layers,
      "tempMax" : zMax,
      "tempMin" : zMin
    }
"""
    # json.dump(json_response,codecs.open(file_path_covjson, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)            
    # del json_response