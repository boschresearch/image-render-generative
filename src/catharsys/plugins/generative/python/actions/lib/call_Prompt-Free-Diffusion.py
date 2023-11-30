#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \call_Takuma-Diffusers.py
# Created Date: Wednesday, April 19th 2023, 4:18:46 pm
# Created by: Fortmeier Dirk (BEG/ESD1)
# <LICENSE id="All-Rights-Reserved">
# Copyright (c) 2023 Robert Bosch GmbH and its subsidiaries
# </LICENSE>
###

from cmath import e
import os
import sys

from PIL import Image
import numpy as np
import json

# import random
# import string

import numpy as np
# import torch

from pathlib import Path

import argparse


def main(args):
    # add the diffusers example directory to the system path
    # so the example code can be imported
    # sys.path.append(args.model_code_path + "/examples/community/")

    # import stable_diffusion_multi_controlnet as takuma

    # from diffusers.utils import load_image

    with open(args.config_list_path, "r") as file:
        lConfigs = json.load(file)


    for i, dicConfigListEntry in enumerate(lConfigs):
        mSDParameters = lConfigs[i]["mConfig"]["mParams"]
        
        sOutputImagePath = dicConfigListEntry["sOutputImagePath"]
        pathOutputImage = Path(sOutputImagePath)
        pathOutput = pathOutputImage.parent
        pathControl = pathOutput / "control"
        pathControl.mkdir(parents=True, exist_ok=True)

        dicConfig = dicConfigListEntry["mConfig"]
        dicCtrlNets = dicConfig["mControlNets"]

        # load the input images
        dicInputImages = {}
        for sKey, sFilename in dicConfigListEntry["mInputs"].items():
            pathFileSrc = Path(sFilename)
            xImage = Image.open(sFilename)  # load_image(sFilename)
            # xImage.save(f"{sKey}.png")
            xNImage = np.asarray(xImage)

            dicControlNet = dicCtrlNets[sKey]

            if "mPreprocess" in dicControlNet:
                for sPreprocessor in dicControlNet["mPreprocess"]:
                    print(f"Procssing {sPreprocessor} on {sKey} ...")
                    if sPreprocessor == "Normalize":
                        fMin = np.min(xNImage)
                        fMax = np.max(xNImage)
                        xNImage = (xNImage - fMin) / float(fMax - fMin) * 255.0
                    elif sPreprocessor == "Invert":
                        fMax = np.max(xNImage)
                        xNImage = np.ones(xNImage.shape) * fMax - xNImage
                    # endif
                # endfor
            # endif

            dicInputImages[sKey] = Image.fromarray(np.uint8(xNImage)).convert("RGB")
            pathFileTrg: Path = pathControl / f"{pathFileSrc.stem}_{sKey}.png"
            dicInputImages[sKey].save(pathFileTrg.as_posix())
        # endfor inputs

        iWidth = mSDParameters.get("iWidth", 832)
        iHeight = mSDParameters.get("iHeight", 512)
        iSeed = int(dicConfig.get("iSeed", 0))
        fCFGScale = float(mSDParameters.get("fCFGScale",2.0))
        sSeecoder_id=mSDParameters.get("sSeecoder_id","SeeCoder")
        sDiffuser_id = mSDParameters.get("sDiffuser_id", "Deliberate-v2.0")        

        pathConfigFile = pathControl / f"{pathFileSrc.stem}_config.json"
        with pathConfigFile.open("w") as xFile:
            json.dump(dicConfig, xFile, indent=4)
        # endwith


        # write prompt free diffusion root path in environment to be used by the pfd code
        pfd_root = mSDParameters["prompt_free_diffusion_root_path"]
        os.environ["pfd_root"] = pfd_root 
        # append path and import from app.py
        sys.path.append(pfd_root)
        
        os.chdir(pfd_root)
        from app import prompt_free_diffusion

        pfd_inference_manager = prompt_free_diffusion(
            fp16=True,
            # tag_ctx="SeeCoder",
            tag_ctx=sSeecoder_id,
            # tag_diffuser="Deliberate-v2.0",
            tag_diffuser=sDiffuser_id,
            tag_ctl="depth",
            rootpath=pfd_root,
        )

        xInput_image = Image.open(mSDParameters["reference_image"]).convert(mode="RGB")
        xControl_image = dicInputImages["Depth"]

        out = pfd_inference_manager.action_inference(
            xInput_image, 
            xControl_image,
            # preprocessing set to depth, but deactivated 
            "depth",    
            False, 
            iHeight, 
            iWidth, 
            fCFGScale,
            iSeed, 
            sSeecoder_id, 
            sDiffuser_id,
            # control net to be used 
            "depth"
        )

        
        out[0].save(sOutputImagePath)

    # endfor


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--model_code_path")
    parser.add_argument("--config_list_path")

    args = parser.parse_args()
    main(args)
