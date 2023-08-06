from mapkit.RasterConverter import RasterConverter
from sqlalchemy import create_engine

# For pretty print functionality for debugging
# not recommended for production
# import xml.dom.minidom
import time

# Setup SQLAlchemy connection
engine = create_engine('postgresql://swainn:(|w@ter@localhost:5432/raster_test')
            
tableName = 'map_kit_rasters'
rasterId = 3
name = 'Texas Groundwater Elevation Gridded'
path = '/Users/swainn/projects/post_gis/large_rasters/waterelev_gridded.kml'

# Initialize raster converter
converter = RasterConverter(sqlAlchemyEngineOrSession=engine)
# colors = [(255, 0, 0),(0, 255, 0),(0, 0, 255)]
# converter.setCustomColorRamp(colors, 10)
converter.setDefaultColorRamp(RasterConverter.COLOR_RAMP_TERRAIN)

# Start timer
start = time.time()

kmlString = converter.getAsKmlGrid(tableName=tableName,
                                   rasterId=rasterId,
                                   documentName=name)

with open(path, 'w') as f:
#     pretty = xml.dom.minidom.parseString(kmlString)
#     f.write(pretty.toprettyxml())
    f.write(kmlString)

print 'KML CONVERSION TIME:', time.time()-start