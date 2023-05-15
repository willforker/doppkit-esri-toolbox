import arcpy
import os
import pathlib
from doppkit.app import Application
from doppkit.grid import Api
from doppkit.sync import sync
import asyncio
import subprocess
import time

from typing import NamedTuple


class SyncParameters(NamedTuple):
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
            # let's hide it for now...
            # SubprocessSync
        ]


class FetchExport:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "GRiD Sync"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        grid_access_token = arcpy.Parameter(
            displayName="GRiD Access Token",
            name="grid_access_token",
            datatype="GPString",
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
        return [grid_access_token, aoi_name, dl_directory, add_to_map]

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
        url = "https://grid.nga.mil/grid"
        log_level = "DEBUG"

        # no event loop in ESRI toolboxes?
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        app = Application(token, url, log_level, 20)

        api = Api(app)

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

        # Alex, I'll take 'What is Monkey Patching?' for $500
        app.start_id = 0
        app.timeout = 20
        app.command = "sync"
        app.overwrite = True
        app.directory = pathlib.Path(output_dir)
        app.filter = ""
        app.pk = aoi_pk
        app.disable_ssl_verification = False

        sync(app, aoi_pk)

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        active_map = aprx.activeMap
        arcpy.env.addOutputsToMap = True
        if active_map is None:
            arcpy.AddMessage("Active Map is None")

        elif named_parameters.add_to_map.value:
            only_files = [
                f
                for f in os.listdir(output_dir)
                if os.path.isfile(os.path.join(output_dir, f))
            ]
            for f in only_files:
                try:
                    active_map.addDataFromPath(os.path.join(output_dir, f))
                    arcpy.AddMessage(f"{os.path.join(output_dir, f)} added to map.")
                except:
                    arcpy.AddWarning(
                        f"{os.path.join(output_dir, f)} cannot be added to the map."
                    )
        return None

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return


class SubprocessSync:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "GRID Sync (Subprocess) [DO NOT USE]"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        grid_access_token = arcpy.Parameter(
            displayName="GRiD Access Token",
            name="grid_access_token",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
        )
        aoi_name = arcpy.Parameter(
            displayName="AOI URL",
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
        params = [grid_access_token, aoi_name, dl_directory, add_to_map]

        add_to_map.value = True

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

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
        token = parameters[0].valueAsText
        url = "https://grid.nga.mil/grid"

        aoi_url = parameters[1].valueAsText
        aoi_pk = aoi_url[-6:].strip("/")
        arcpy.AddMessage(f"AOI PK: {aoi_pk}")

        directory = parameters[2].valueAsText

        # make unique folder for outputs
        current_time = time.localtime(time.time())
        timestamp = "%d-%02d-%02d_%02d-%02d-%02d" % (
            current_time.tm_year,
            current_time.tm_mon,
            current_time.tm_mday,
            current_time.tm_hour,
            current_time.tm_min,
            current_time.tm_sec,
        )

        output_dir = os.path.join(directory, f"GRID-AOI_{aoi_pk}_{timestamp}")
        arcpy.AddMessage(f"Fetching contents of AOI and downloading to {output_dir}")
        subprocess.run(
            [
                "doppkit",
                "--token",
                f"{token}",
                "sync",
                f"{aoi_pk}",
                "--directory",
                f"{output_dir}",
            ],
            capture_output=True,
        )

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        activeMap = aprx.activeMap
        arcpy.env.addOutputsToMap = True
        if activeMap is not None and parameters[3].value:
            # TODO: redo this with os.walk
            onlyfiles = [
                f
                for f in os.listdir(output_dir)
                if os.path.isfile(os.path.join(output_dir, f))
            ]
            for f in onlyfiles:
                try:
                    activeMap.addDataFromPath(os.path.join(output_dir, f))
                    arcpy.AddMessage(f"{os.path.join(output_dir, f)} added to map.")
                except:
                    arcpy.AddWarning(
                        f"{os.path.join(output_dir, f)} cannot be added to the map."
                    )

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
