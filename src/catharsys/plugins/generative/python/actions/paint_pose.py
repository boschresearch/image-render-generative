#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \image-render-generative\src\catharsys\plugins\_ext_\python\actions\paint_pose.py
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
import json
from pathlib import Path

from catharsys.config.cls_config_list import CConfigList
from catharsys.plugins.std.action_class.manifest.cls_cfg_manifest_job import (
    CConfigManifestJob,
)


################################################################################
# Return action definition
def GetDefinition():
    return {
        # Define this action to be configured via a manifest base setup.
        # Currently, this is the only available type.
        "sDTI": "/catharsys/action-class/python/manifest-based:2.0",
        # This is the DTI of the action, which is used in the launch.json file
        # to reference this action.
        "sActionDTI": "/catharsys/action/generative/paint_pose:1.0",
        # This defines which execution configuration is needed for this action.
        "sExecuteDTI": "exec/python/*:*",
        # This defines which project class is used by this action.
        "sProjectClassDTI": "/catharsys/project-class/std/blender/render:1.0",
        # This defines how jobs can be distributed
        "sJobDistType": "frames;configs",
        # The following is a definition of obligatory arguments.
        # This is currently (v3.2) not used by Catharsys, but may be used in the future.
        "mArgs": {
            "iFrameFirst": {"sType": "int", "xDefault": 0},
            "iFrameLast": {"sType": "int", "xDefault": 0},
            "iRenderQuality": {"sType": "int", "xDefault": 4, "bOptional": True},
            "iConfigGroups": {"sType": "int", "xDefault": 1, "bOptional": True},
            "iFrameGroups": {"sType": "int", "xDefault": 1, "bOptional": True},
            "bDoProcess": {"sType": "bool", "xDefault": True, "bOptional": True},
        },
    }


# enddef


################################################################################
def ResultData(xJobCfg: CConfigManifestJob):
    # This function can return a database of its result data based on a configuration.
    # This is used by other tools, like the ipython API, to display the
    # result images of this action.
    # For an example see the tonemap action in
    #    image-render-actions-std/src/catharsys/plugins/std/python/actions/tonemap.py
    #
    return None


# enddef


################################################################################
# Call actual action from separate file, to avoid importing all modules
# when catharsys obtains the action definition.
def Run(_xCfg: CConfigList) -> None:
    from .lib.cls_paint_pose import CPaintPose
    from anybase import assertion

    # assertion.FuncArgTypes()

    xAction = CPaintPose()

    def Process(_xAction: CPaintPose):
        def Lambda(_xPrjCfg, _dicCfg, **kwargs):
            _xAction.Process(_xPrjCfg, _dicCfg, kwargs=kwargs)

        # enddef
        return Lambda

    # enddef

    # process all configs
    _xCfg.ForEachConfig(Process(xAction))


# enddef
