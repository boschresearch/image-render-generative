#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \image-render-generative\src\catharsys\plugins\_ext_\python\actions\lib\cls_paint_pose.py
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

import cv2
import numpy as np


class CPaintPose:
    """This action loads human poses and paints it to a png image."""

    # The project configuration
    xPrjCfg: CProjectConfig = None
    dicConfig: dict = None
    dicData: dict = None

    # Config that describes which bones should be painted how
    sPaintPoseDataDti: str = "/catharsys/generative/paint_pose_data:1"

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
        print("Start Processing Pose Painting Action\n")

        sWhere: str = "pose paint action configuration"
        self.xPrjCfg = _xPrjCfg

        ##################################################################################
        # Get the current configuration
        self.dicConfig = cathcfg.GetDictValue(_dicCfg, "mConfig", dict, sWhere=sWhere)
        self.dicData = cathcfg.GetDictValue(self.dicConfig, "mData", dict, sWhere=sWhere)

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
        lPaintPoseData = cathcfg.GetDataBlocksOfType(self.dicData, self.sPaintPoseDataDti)
        if len(lPaintPoseData) == 0:
            raise Exception(
                "No paint pose configuration of type compatible to '{0}' given.".format(self.sPaintPoseDataDti)
            )
        # endif

        # Here we expect that there is only a single instance of the configuration data.
        # However, in principle there could be any number of configurations of the same type
        # included in the combined job configuration.
        dicExample: dict = lPaintPoseData[0]

        ##################################################################################
        # Obtain main source path from the parent action.
        self.pathSrcMain = GetParentConfigTargetPath(_dicCfg)

        # Get the image render source path from the current configuration settings
        pathDataSrc: Path = self.pathSrcMain / "Data"

        if not pathDataSrc.exists():
            raise RuntimeError(f"Source to labeling data does not exist: {(pathDataSrc.as_posix())}")
        # endif

        ##################################################################################
        # Create target path for this action
        pathImageTrg: Path = Path(self.sPathTrgMain) / "PoseImage"
        pathImageTrg.mkdir(parents=True, exist_ok=True)

        ##################################################################################
        # Print current config values
        print(f"Main project path: {(_xPrjCfg.pathMain.as_posix())}")
        print(f"Image source path: {(pathDataSrc.relative_to(_xPrjCfg.pathMain).as_posix())}")
        print(f"Generated main path: {(Path(self.sPathTrgMain).relative_to(_xPrjCfg.pathMain).as_posix())}")

        # Use the conversion functions from the module anybase.convert to read values
        # from dictionaries. They automatically convert the dictionary value types
        # to the expected output type and do proper error reporting.

        lLayers = dicExample["lLayers"]

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
            sFrameName: str = "Frame_{0:04d}".format(iTrgFrame)
            sFileImgSrc: str = f"{sFrameName}.json"

            pathDataSrcFile: Path = pathDataSrc / sFileImgSrc
            if not pathDataSrc.exists():
                print(f"Data '{pathDataSrc}' does not exist. Skipping...")

            else:
                sFileImgTrg: str = f"{sFrameName}.png"
                pathImgTrgFile: Path = pathImageTrg / sFileImgTrg
                if self.bDoOverwrite is False and pathImgTrgFile.exists():
                    print(f"Skipping image file as it already exists: {(pathImgTrgFile.as_posix())}")

                else:
                    print(f"Writing image to: {(pathImgTrgFile.as_posix())}")

                    if self.bDoProcess:
                        # TODO use proper catharsys code for this
                        with open(pathDataSrcFile, "r") as file:
                            dictSemseg = json.load(file)

                        width, height = dictSemseg["mCamera"]["lPixCntXY"]
                        CPaintPose._InitImageLayers(lLayers, height, width)

                        for dictType in dictSemseg["lTypes"]:
                            if dictType["sId"] == "Person":
                                for sPersonInstanceId, dictPersonInstance in dictType["mInstances"].items():
                                    dictBones = list(dictPersonInstance["mPoses3d"].values())[0]["mBones"]

                                    dictBoneCoords = CPaintPose._getBonePositions(dictBones)

                                    CPaintPose._DrawOnLayers(lLayers, dictBoneCoords, height, width)
                                # endfor
                            # endif
                        # endfor
                        image = CPaintPose._mergeLayers(lLayers, height, width)
                        cv2.imwrite(str(pathImgTrgFile), image)

                    # endif
                # endif
            # endif

            iTrgFrame += self.iFrameStep
            iTrgFrameIdx += 1
        # endwhile

    # enddef Process()


    def _InitImageLayers(lLayers, height, width):
        for mLayer in lLayers:
            image = mLayer.get("__image__", np.zeros((height, width, 3)))
            mLayer["__image__"] = image
        # endfor
    # enddef


    def _DrawOnLayers(lLayers, dictBoneCoords, height, width):
        for mLayer in lLayers:
            image = mLayer["__image__"]

            lLines = mLayer.get("lLines", [])
            lPoints = mLayer.get("lPoints", [])

            for dictLine in lLines:
                sP1 = dictLine["sP1"]
                sP2 = dictLine["sP2"]
                lColor = dictLine["lColor"][::-1]

                bP1UseTail = dictLine.get("bP1UseTail", False)
                bP2UseTail = dictLine.get("bP2UseTail", False)

                if bP1UseTail:
                    sP1 += "_tail"
                # endif

                if bP2UseTail:
                    sP2 += "_tail"
                # endif

                xyP1 = dictBoneCoords[sP1]
                xyP2 = dictBoneCoords[sP2]
                if xyP1 is not None and xyP2 is not None:
                    line_thickness = dictLine.get("iSize", 4)
                    bLine = dictLine.get("bLine", False)

                    if bLine:
                        cv2.line(
                            image,
                            xyP1,
                            xyP2,
                            lColor,
                            thickness=line_thickness,
                        )
                    else:
                        xyDirection = dictBoneCoords[sP1] - dictBoneCoords[sP2]
                        xyCenter = ((dictBoneCoords[sP1] + dictBoneCoords[sP2]) * 0.5).astype(np.int32)
                        fEllipseLength = np.linalg.norm(xyDirection)
                        axis = (int(fEllipseLength / 2.0), int(line_thickness))
                        iAngle = int(math.degrees(math.atan2(xyDirection[1], xyDirection[0])))
                        cv2.ellipse(image, xyCenter, axis, iAngle, 0, 360, lColor, thickness=-1)
                    # endif
                # endif
            # endfor

            for dictPoint in lPoints:
                sP = dictPoint["sP"]
                bPUseTail = dictPoint.get("bPUseTail", False)
                if bPUseTail:
                    sP += "_tail"
                # endif
                lColor = dictPoint["lColor"][::-1]
                radius = dictPoint.get("iSize", 4)
                cv2.circle(image, dictBoneCoords[sP], radius, lColor, thickness=-1)
            # endfor
        # endfor
        return lLayers

    # enddef

    def _mergeLayers(lLayers, height, width):
        """This merges a list of layers into a single image

        Parameters
        ----------
        lLayers : list
            list of dicts that describe the layers
        height : image height
            _description_
        width : image_width
            _description_

        Returns
        -------
        np.ndarray
            merged layers in a single image
        """
        image = np.zeros((height, width, 3))

        for mLayer in lLayers:
            fWeight = mLayer.get("fWeight", 1.0)
            image = image + mLayer["__image__"] * fWeight
            image = np.clip(image, 0, 255)
            image = image.astype(np.uint8)
        # endfor

        return image

    def _getBonePositions(mBones):
        dictBoneCoords = {}

        for sBoneName, dictBoneValues in mBones.items():
            lHead = dictBoneValues["mImage"]["lHead"]
            lTail = dictBoneValues["mImage"]["lTail"]

            xyHead = np.asarray(lHead, dtype=np.int32) if lHead is not None else None
            xyTail = np.asarray(lTail, dtype=np.int32) if lTail is not None else None
            # TODO check why self occlusion is not working
            # Note: This is not a problem with this code, but something else
            # should be changed in the future.
            bHeadInvisible = dictBoneValues["mImage"]["bHeadOccluded"]  # or (
            #    dictBoneValues["mImage"]["bHeadSelfOcc"] is True
            # )

            if bHeadInvisible:
                xyHead = None

            bTailInvisible = dictBoneValues["mImage"]["bTailOccluded"]  # or (

            if bTailInvisible:
                xyTail = None

            dictBoneCoords[sBoneName] = xyHead
            dictBoneCoords[sBoneName + "_tail"] = xyTail
        # endfor

        return dictBoneCoords

    # enddef


# endclass
