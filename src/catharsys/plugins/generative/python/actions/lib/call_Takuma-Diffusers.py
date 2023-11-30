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
import cv2

import numpy as np
import json

import random
import string

import numpy as np
import torch

from pathlib import Path

import argparse

from diffusers.utils import load_image

import os.path as path


parser = argparse.ArgumentParser()

parser.add_argument("--model_code_path")
parser.add_argument("--config_list_path")

args = parser.parse_args()

# add the diffusers example directory to the system path
# so the example code can be imported
sys.path.append(args.model_code_path + "/examples/community/")

import stable_diffusion_multi_controlnet as takuma


def save_image(image: np.ndarray, sOutputImagePath: str, sOutputFormat: str):
    sOutputImagePathBase = path.splitext(sOutputImagePath)[0]

    if sOutputFormat == "f32tiff":
        # Output as tiff with single precision color chanels
        sOutputImagePathFinal = sOutputImagePathBase + "_" + sOutputFormat + ".tiff"
        image_converted_cv2 = cv2.cvtColor(image, cv2.CV_32F)
        cv2.imwrite(
            sOutputImagePathFinal, image_converted_cv2[:, :, [0, 1, 2]], params=(cv2.IMWRITE_TIFF_COMPRESSION, 1)
        )

    #  this does not work, I leave it in here as warning to my future self ;)
    # if sOutputFormat == "f16tiff":
    #     # Output as tiff with half precision color chanels
    #     sOutputImagePathFinal = sOutputImagePathBase + "_" + sOutputFormat + ".tiff"

    #     image_converted_cv2 = cv2.cvtColor(image, cv2.CV_32F)
    #     image_converted = image_converted_cv2[:, :, [0, 1, 2]].astype("float16")
    #     cv2.imwrite(sOutputImagePathFinal, image_converted, params=(cv2.IMWRITE_TIFF_COMPRESSION, 1))

    if sOutputFormat == "uint16tiff":
        # Output as tiff with uint16 color chanels
        sOutputImagePathFinal = sOutputImagePathBase + "_" + sOutputFormat + ".tiff"
        image_converted_cv2 = cv2.cvtColor(image, cv2.CV_32F)
        image_converted = (image_converted_cv2[:, :, [0, 1, 2]] * 255 * 255).round().astype("uint16")
        cv2.imwrite(sOutputImagePathFinal, image_converted)

    if sOutputFormat == "uint8png":
        sOutputImagePathFinal = sOutputImagePathBase + "_" + sOutputFormat + ".png"
        image_converted_cv2 = cv2.cvtColor(image, cv2.CV_32F)
        image_converted = (image_converted_cv2[:, :, [0, 1, 2]] * 255).round().astype("uint8")
        cv2.imwrite(sOutputImagePathFinal, image_converted)

    if sOutputFormat == "f32exr":
        # Output as tiff with single precision color chanels
        sOutputImagePathFinal = sOutputImagePathBase + "_" + sOutputFormat + ".exr"
        image_converted_cv2 = cv2.cvtColor(image, cv2.CV_32F)
        os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
        cv2.imwrite(sOutputImagePathFinal, image_converted_cv2[:, :, [0, 1, 2]].astype(np.float32))

    if sOutputFormat == "f16exr":
        # Output as tiff with half precision color chanels
        sOutputImagePathFinal = sOutputImagePathBase + "_" + sOutputFormat + ".exr"
        image_converted_cv2 = cv2.cvtColor(image, cv2.CV_32F)
        os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
        cv2.imwrite(
            sOutputImagePathFinal,
            image_converted_cv2[:, :, [0, 1, 2]].astype(np.float32),
            [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_HALF],
        )

    if sOutputFormat == "f32npy":
        # Output numpy array with single precision
        sOutputImagePathFinal = sOutputImagePathBase + "_" + sOutputFormat + ".npy"
        image_converted_cv2 = cv2.cvtColor(image, cv2.CV_32F)
        np.save(sOutputImagePathFinal, image_converted_cv2.astype(np.float32), allow_pickle=False)

    if sOutputFormat == "f16npy":
        # Output numpy array with half precision
        sOutputImagePathFinal = sOutputImagePathBase + "_" + sOutputFormat + ".npy"
        image_converted_cv2 = cv2.cvtColor(image, cv2.CV_32F)
        np.save(sOutputImagePathFinal, image_converted_cv2.astype(np.float16), allow_pickle=False)

    if sOutputFormat == "uint32npy":
        # Output numpy array as uint32
        sOutputImagePathFinal = sOutputImagePathBase + "_" + sOutputFormat + ".npy"
        image_converted_cv2 = cv2.cvtColor(image, cv2.CV_32F)
        image_converted = (image_converted_cv2[:, :, [0, 1, 2]] * 255 * 255 * 255 * 255).round().astype("uint32")
        np.save(sOutputImagePathFinal, image_converted_cv2.astype(np.uint32), allow_pickle=False)

    if sOutputFormat == "uint16npy":
        # Output numpy array as uint16
        sOutputImagePathFinal = sOutputImagePathBase + "_" + sOutputFormat + ".npy"
        image_converted_cv2 = cv2.cvtColor(image, cv2.CV_32F)
        image_converted = (image_converted_cv2[:, :, [0, 1, 2]] * 255 * 255).round().astype("uint16")
        np.save(sOutputImagePathFinal, image_converted_cv2.astype(np.uint32), allow_pickle=False)

    if sOutputFormat == "uint8npy":
        # Output numpy array as uint8
        sOutputImagePathFinal = sOutputImagePathBase + "_" + sOutputFormat + ".npy"
        image_converted_cv2 = cv2.cvtColor(image, cv2.CV_32F)
        image_converted = (image_converted_cv2[:, :, [0, 1, 2]] * 255).round().astype("uint8")
        np.save(sOutputImagePathFinal, image_converted_cv2.astype(np.uint32), allow_pickle=False)


with open(args.config_list_path, "r") as file:
    lConfigs = json.load(file)


mSDParameters = lConfigs[0]["mConfig"]["mParams"]

dicControlNetObjects = {}

# preload the models
print("Loading modules from pretrained ...")
print(mSDParameters["pretrained_model_name_or_path"])

# sd_datatype = torch.float16
sd_datatype = torch.float32

pipe = takuma.StableDiffusionMultiControlNetPipeline.from_pretrained(
    safety_checker=None, torch_dtype=sd_datatype, **mSDParameters
).to("cuda")

for sKey, dicNet in lConfigs[0]["mConfig"]["mControlNets"].items():
    dicControlNetParams = dicNet["mParams"]
    print(dicControlNetParams["pretrained_model_name_or_path"])
    dicControlNetObjects[sKey] = takuma.ControlNetModel.from_pretrained(
        torch_dtype=sd_datatype, **dicControlNetParams
    ).to("cuda")
# endfor

# weight_pose = 1.0  # alen: 1.0
# weight_depth = 1.0  # alen: 0.2 to 0.5

# alen: add original image
# alen denoising_strength: ab 0.9 photorelistic

# alen: 20 steps, noise scheduler euler a oder dpm++ 2m karras

# restore faces aus a1111

# w h:

# alen cfg scale:  7.0

# alen: control net 1.1.125 (new versoin)

# alen: start wann control net losgeht, aber noch nicht getestet

for i, dicConfigListEntry in enumerate(lConfigs):
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

    lProcessors = []
    # TODO maybe move this outside?
    for sKey, dicControlNet in dicCtrlNets.items():
        xControlNetObject = dicControlNetObjects[sKey]
        sInputImage = dicInputImages[sKey]
        fWeight = dicControlNet["fWeight"]
        xProcessor = takuma.ControlNetProcessor(xControlNetObject, sInputImage, fWeight)
        lProcessors.append(xProcessor)
    # endfor

    width = dicConfig.get("iWidth", 832)
    height = dicConfig.get("iHeight", 512)

    xLatents = None

    pathConfigFile = pathControl / f"{pathFileSrc.stem}_config.json"
    with pathConfigFile.open("w") as xFile:
        json.dump(dicConfig, xFile, indent=4)
    # endwith

    iSeed = int(dicConfig.get("iSeed", 0))
    iNumSteps = int(dicConfig.get("iNumSteps", 20))
    sPrompt = str(dicConfig.get("sPrompt"))
    sNegativePrompt = str(dicConfig.get("sNegativePrompt", ""))

    image = pipe(
        prompt=sPrompt,
        negative_prompt=sNegativePrompt,
        processors=lProcessors,
        generator=torch.Generator(device="cpu").manual_seed(iSeed),
        num_inference_steps=iNumSteps,
        width=width,
        height=height,
        latents=xLatents,
        output_type="np.array",
    ).images[0]

    lOutputFormats = dicConfig.get("lOutputFormats", ["uint8png"])

    for sFormat in lOutputFormats:
        save_image(image, sOutputImagePath, sFormat)
