#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: \ControlNet-v1-1-nightly.py
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

import random
import string

from pathlib import Path

import argparse

# change into the control net directory and append that path to the system path
# this is necessary as Contorl net is not a module per se, but contains several scripts that
# normally are executed on the command line.

parser = argparse.ArgumentParser()

parser.add_argument("--model_code_path")
parser.add_argument("--config_list_path")

args = parser.parse_args()

os.chdir(args.model_code_path)
sys.path.append("./")


def getLineArtCode():
    with open("gradio_lineart.py") as file:
        lCode = []
        for iLineNo, sLine in enumerate(file):
            if iLineNo > 81:
                break
            else:
                lCode.append(sLine)

        sCode = "\n".join(lCode)

    return sCode


sCode = getLineArtCode()

# load the module containing control net without the call to start gradio
exec(sCode)

with open(args.config_list_path, "r") as file:
    lConfigs = json.load(file)

for conf in lConfigs:
    print(conf)

for i, dictConfig in enumerate(lConfigs):
    # load the input image
    image_path = dictConfig["input_image_path"]
    input_image = Image.open(image_path)
    input_image = np.asarray(input_image)

    mConfig = dictConfig["config"]

    prompt = mConfig.get("sPrompt", "")
    num_samples = 1
    seed = mConfig.get("seed", 12345)
    det = mConfig.get("mode", "Lineart")
    image_resolution = mConfig.get("resolution", 512)
    strength = mConfig.get("strength", 1.0)
    guess_mode = mConfig.get("guess_mode", False)
    detect_resolution = mConfig.get("detect_resolution", 512)
    ddim_steps = mConfig.get("ddim_steps", 20)
    scale = mConfig.get("scale", 9.0)
    eta = mConfig.get("eta", 1.0)
    a_prompt = mConfig.get("additional_prompt", "best quality")
    n_prompt = mConfig.get("negative_prompt", "lowres, bad anatomy, bad hands, cropped, worst quality")

    ips = [
        det,
        input_image,
        prompt,
        a_prompt,
        n_prompt,
        num_samples,
        image_resolution,
        detect_resolution,
        ddim_steps,
        guess_mode,
        strength,
        scale,
        seed,
        eta,
    ]

    # call the process fuction from control net code
    xResult = process(*ips)

    # write out the result
    r = "".join(random.choices(string.ascii_lowercase, k=12))
    for i, xImage in enumerate(xResult):
        xImage = Image.fromarray(xImage)
        output_image_path = dictConfig["output_image_path"]
        # check if image output path needs to be created
        sBasePath = Path(output_image_path).parent
        sBasePath.mkdir(parents=True, exist_ok=True)

        xImage.save(output_image_path)
