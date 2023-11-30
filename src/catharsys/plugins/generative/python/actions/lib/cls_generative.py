#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \image-render-generative\src\catharsys\plugins\_ext_\python\actions\lib\cls_generative.py
# Created Date: Tuesday, May 4th 2023, 8:45:00 am
# Author: Dirk Fortmeier (BEG/EOR1)
# <LICENSE id="Apache-2.0">
#
#   Image-Render Standard Actions module
#   Copyright 2022 Robert Bosch GmbH and its subsidiaries
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# </LICENSE>
###

import os
import math
from anybase import assertion, convert
from pathlib import Path

from catharsys.config.cls_project import CProjectConfig
import catharsys.util.config as cathcfg
import catharsys.util.file as cathfile
import catharsys.util.path as cathpath
from catharsys.plugins.std.blender.util.action import GetRenderFolder
from catharsys.action.util import GetParentConfigTargetPath


import json


class CGenerative:
    """This actions uses catharsys output files and passes them to
    generative models.
    """

    # The project configuration
    xPrjCfg: CProjectConfig = None
    dicConfig: dict = None
    dicData: dict = None

    # This contains the settings for this action.
    sExampleDti: str = "/catharsys/generative/data:1"

    # This is the generative model id, must match with
    # 1. The source folder name in models/
    # 2. The env folder name in envs/
    # 3. the call_ModelTypeId.py execution script
    sModelTypeDti: str = "/catharsys/generative/model-id:1"

    sPathTrgMain: str = None
    pathSrcMain: Path = None
    dicPathTrgAct: dict = None
    dicActDtiToName: dict = None
    lActions: list = None
    iFrameFirst: int = None
    iFrameLast: int = None
    iFrameStep: int = None
    bDoProcess: bool = None
    bDoOverwrite: bool = None
    iDoProcess: int = None
    iDoOverwrite: int = None

    ################################################################################
    def __init__(self):
        pass

    # enddef

    ################################################################################
    def Process(self, _xPrjCfg: CProjectConfig, _dicCfg: dict, **kwargs):
        assertion.FuncArgTypes()

        print("\n==============================")
        print("Start Processing Generative Action\n")

        sWhere: str = "generative action configuration"
        self.xPrjCfg = _xPrjCfg

        ##################################################################################
        # Get the current configuration
        self.dicConfig = cathcfg.GetDictValue(_dicCfg, "mConfig", dict, sWhere=sWhere)
        self.dicData = cathcfg.GetDictValue(self.dicConfig, "mData", dict, sWhere=sWhere)

        lConfigs = []

        ##################################################################################
        # Load set of parameters from given configuration into this class
        cathcfg.StoreDictValuesInObject(
            self,
            _dicCfg,
            [
                ("sPathTrgMain", str),
                ("dicPathTrgAct", dict),
                ("dicActDtiToName", dict),
                ("lActions", list),
                ("iFrameFirst", int, 0),
                ("iFrameLast", int, 0),
                ("iFrameStep", int, 1),
                ("iDoProcess", int, 1),
                ("bDoProcess", bool, True),
                ("iDoOverwrite", int, 1),
                ("bDoOverwrite", bool, True),
            ],
            sWhere="action configuration",
        )

        ##################################################################################
        # Can use these flags to enable/disable processing and image overwrite
        self.bDoProcess = self.bDoProcess and (self.iDoProcess != 0)
        self.bDoOverwrite = self.bDoOverwrite and (self.iDoOverwrite != 0)

        ##################################################################################
        # Extract the generative configuration data from the whole config.
        lExampleData = cathcfg.GetDataBlocksOfType(self.dicData, self.sExampleDti)
        if len(lExampleData) == 0:
            raise Exception("No generative configuration of type compatible to '{0}' given.".format(self.sExampleDti))
        # endif

        ##################################################################################
        # Extract the generative model identifier from the whole config.
        # currently, this has to be the same for this group
        lModelIds = cathcfg.GetDataBlocksOfType(self.dicData, self.sModelTypeDti)
        if len(set(lModelIds)) != 1:
            raise Exception(f"Exactly one model id should be given. Found: {set(lModelIds)}")
        # endif
        sModelId = lModelIds[0]

        if len(lExampleData) == 0:
            raise Exception("No generative configuration of type compatible to '{0}' given.".format(self.sExampleDti))
        # endif

        # Here we expect that there is only a single instance of the configuration data.
        # However, in principle there could be any number of configurations of the same type
        # included in the combined job configuration.
        dicExample: dict = lExampleData[0]

        ##################################################################################
        # Obtain main source path from the parent action.
        self.pathSrcMain = GetParentConfigTargetPath(_dicCfg)

        ##################################################################################
        # Create target path for this action

        pathImageTrg: Path = Path(self.sPathTrgMain)
        pathImageTrg.mkdir(parents=True, exist_ok=True)

        ##################################################################################
        # Print current config values
        print(f"Main project path: {(_xPrjCfg.pathMain.as_posix())}")
        print(f"Generated main path: {(Path(self.sPathTrgMain).relative_to(_xPrjCfg.pathMain).as_posix())}")
        print(f"Custom target path': {(pathImageTrg.relative_to(_xPrjCfg.pathMain).as_posix())}")

        # Use the conversion functions from the module anybase.convert to read values
        # from dictionaries. They automatically convert the dictionary value types
        # to the expected output type and do proper error reporting.
        # iExValue: int = convert.DictElementToInt(dicExample, "iValue", iDefault=0)
        # sModel: str = convert.DictElementToString(dicExample, "sModel", sDefault=None)

        mInputs: dict = dicExample.get("mInputs", {"Image": "Image"})
        mConfig: dict = dicExample.get("mConfig", {})

        ##################################################################################
        # Loop over all frames
        print("")

        iTrgFrame: int = self.iFrameFirst
        iTrgFrameIdx: int = 0
        iTrgFrameCnt: int = int(math.floor((self.iFrameLast - self.iFrameFirst) / self.iFrameStep)) + 1
        print(f"Processing {iTrgFrameCnt} frame(s).")

        while iTrgFrame <= self.iFrameLast:
            print(f"\nStart processing frame {iTrgFrame}...", flush=True)

            # Create name of file for current frame
            # TODO make other than .png input images acceptable
            sFrameName: str = "Frame_{0:04d}.png".format(iTrgFrame)

            sFileImgTrg: str = sFrameName

            pathImgTrgFile: Path = pathImageTrg / sFileImgTrg
            if self.bDoOverwrite is False and pathImgTrgFile.exists():
                print(f"Skipping image file as it already exists: {(pathImgTrgFile.as_posix())}")

            else:
                print(f"Writing image to: {(pathImgTrgFile.as_posix())}")

                if self.bDoProcess:
                    dictConf = {
                        "sOutputImagePath": pathImgTrgFile.as_posix(),
                        "mConfig": mConfig,
                    }

                    mInputImages = {
                        sKey: (self.pathSrcMain / sInputId / sFrameName).as_posix()
                        for sKey, sInputId in mInputs.items()
                    }

                    dictConf["mInputs"] = mInputImages
                    dictConf["sModelId"] = sModelId

                    lConfigs.append(dictConf)
                # endif
            # endif

            iTrgFrame += self.iFrameStep
            iTrgFrameIdx += 1
        # endwhile

        return lConfigs

    # enddef Process()


# endclass
