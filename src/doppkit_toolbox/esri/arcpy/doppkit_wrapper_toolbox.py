# -*- coding: utf-8 -*-
r""""""
__all__ = ['Fetch_Export', 'Subprocess_Sync']
__alias__ = 'grid access'
from arcpy.geoprocessing._base import gptooldoc, gp, gp_fixargs
from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject

# Tools
@gptooldoc('Fetch_Export', None)
def Fetch_Export(grid_access_token=None, aoi_name=None, dl_directory=None, add_to_map=None):
    """Fetch_Export(grid_access_token, aoi_name, dl_directory, add_to_map)

     INPUTS:
      grid_access_token (String):
          GRiD Access Token
      aoi_name (String):
          AOI URL
      dl_directory (Folder):
          Download Directory
      add_to_map (Boolean):
          Add Files to Map?"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.Fetch_Export(*gp_fixargs((grid_access_token, aoi_name, dl_directory, add_to_map), True)))
        return retval
    except Exception as e:
        raise e

@gptooldoc('Subprocess_Sync', None)
def Subprocess_Sync(grid_access_token=None, aoi_name=None, dl_directory=None, add_to_map=None):
    """Subprocess_Sync(grid_access_token, aoi_name, dl_directory, add_to_map)

     INPUTS:
      grid_access_token (String):
          GRiD Access Token
      aoi_name (String):
          AOI URL
      dl_directory (Folder):
          Download Directory
      add_to_map (Boolean):
          Add Files to Map?"""
    from arcpy.geoprocessing._base import gp, gp_fixargs
    from arcpy.arcobjects.arcobjectconversion import convertArcObjectToPythonObject
    try:
        retval = convertArcObjectToPythonObject(gp.Subprocess_Sync(*gp_fixargs((grid_access_token, aoi_name, dl_directory, add_to_map), True)))
        return retval
    except Exception as e:
        raise e


# End of generated toolbox code
del gptooldoc, gp, gp_fixargs, convertArcObjectToPythonObject