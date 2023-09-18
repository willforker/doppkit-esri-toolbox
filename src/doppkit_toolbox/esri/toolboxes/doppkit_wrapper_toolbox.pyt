import arcpy
import os
import pathlib
from doppkit.app import Application
from doppkit.grid import Grid
from doppkit.cli.sync import sync
import asyncio

from typing import NamedTuple


class SyncParameters(NamedTuple):
    grid_server: arcpy.Parameter
    token: arcpy.Parameter
    aoi_pk: arcpy.Parameter
    directory: arcpy.Parameter
    add_to_map: arcpy.Parameter


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "GRiD Access"
        self.alias = "grid access"

        # List of tool classes associated with this toolbox
        self.tools = [
            FetchExport,
        ]


class FetchExport:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "GRiD Sync"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        grid_server = arcpy.Parameter(
            displayName="GRiD Server",
            name="grid_server",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        # specify the default server
        grid_server.value = "https://grid.nga.mil/grid"

        grid_access_token = arcpy.Parameter(
            displayName="GRiD Access Token",
            name="grid_access_token",
            datatype="GPStringHidden",  # not actually encrypted!!
            parameterType="Required",
            direction="Input",
        )
        aoi_name = arcpy.Parameter(
            displayName="AOI Key",
            name="aoi_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        dl_directory = arcpy.Parameter(
            displayName="Download Directory",
            name="dl_directory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
        )
        add_to_map = arcpy.Parameter(
            displayName="Add Files to Map?",
            name="add_to_map",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input",
        )
        add_to_map.value = True
        return [grid_server, grid_access_token, aoi_name, dl_directory, add_to_map]

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        named_parameters = SyncParameters(
            *parameters
        )

        token = named_parameters.token.valueAsText
        url = named_parameters.grid_server.valueAsText
        log_level = "DEBUG"

        # no event loop in ESRI toolboxes?
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


        aoi_url = named_parameters.aoi_pk.valueAsText
        aoi_pk = aoi_url[-7:].strip("/")

        arcpy.AddMessage(f"AOI PK: {aoi_pk}")

        output_dir = os.fsdecode(
            named_parameters.directory.valueAsText
        ).replace(os.sep, "/")

        arcpy.AddMessage(f"Saving to {output_dir}")

        arcpy.AddMessage(
            f"Add to map: {named_parameters.add_to_map.value}"
        )

        app = Application(
            token,
            url=url,
            log_level=log_level,
            run_method='ESRI',
            threads=20,
            directory=output_dir,
            override=True
        )
        contents = asyncio.run(sync(app, aoi_pk))
        files_to_render = [
            os.fsdecode(content.target) 
            for content in contents 
            if isinstance(content.target, pathlib.Path)
        ]

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        active_map = aprx.activeMap
        arcpy.env.addOutputsToMap = True
        if active_map is None:
            arcpy.AddMessage("Active Map is None")

        elif named_parameters.add_to_map.value:
            for f in files_to_render:
                try:
                    active_map.addDataFromPath(f)
                    arcpy.AddMessage(f"{f} added to map.")
                except RuntimeError:
                    arcpy.AddWarning(
                        f"{f} cannot be added to the map."
                    )
        return None

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
