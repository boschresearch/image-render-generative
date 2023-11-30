# Image Render Generative

**Check out the `stable` branch for the latest stable version**

This catharsys plugin adds functionality for using generative models to
enhance or create new synthetic data based on renderings from catharsys.

## Purpose of the project

This software is a research prototype, originally developed for use in rendering automation.

The software is not ready for production use. It has neither been developed nor tested for a specific use case. However, the license conditions of the applicable Open Source licenses allow you to adapt the software to your needs. Before using it in a safety relevant setting, make sure that the software fulfills your requirements and adjust it according to any applicable safety standards (e.g. ISO 26262).

## Contributing to the project

Please read the conditions you need to comply with in order to contribute to this project in the [CONTRIBUTING](CONTRIBUTING.md) file. 

## License

The `image-render-generative` package is licenced under the Apache-2.0 license. See the [LICENSE](LICENSE.md) file for more details.


## Overview

This catharsys plugin adds functionality for using generative models to
enhance or create new synthetic data based on renderings from catharsys.

Currently, the following methods are available:
- Takuma's Multi Control net for diffusers
- (Control Net Nightly, deprecated)

Since the dependencies of the methods differ from each other and from
catharsys, for each method a separate and new conda environment has
to be created. To do so, call the respective scripts.


## Install the Action

To use the generative actions, you need to install them into your Catharsys workspace. If you have a development installation change into the `image-render-generative` folder and execute the command `pip install -e .`. Otherwise, execute `pip install .` from within the folder. Now the actions are available from Catharsys configurations.


## Takuma Multi Control Net

This model is based on the implementation of github user takuma104:

https://github.com/takuma104/diffusers/tree/multi_controlnet

This implementation is a fork of the popular python package diffusers.
To setup the conda environment, download and install the repository
and download all the needed model files, simply call

    bash scripts/get_takuma_diffusers.sh

This also downloads additional networks into the ./models folder with
git lfs. Make sure git lfs is available before calling the script.
Also, consider to remove the .git folder in the models folder to save.
Also you can directly point to a different location in your catharsys
config files.

However, we suggest to perform the steps manually one after another and
also store the additional model files not directly in this module, but
at a central location and reuse it from there.

To use takumas multi control net, you need to first add a pose painting
step to your actions and then add the generative step.

### Create open pose images by paint pose action

To add pose painting to your config, add the following in the respective files:

manifest.json5:

    // ...
    paint_pose: {
        sDTI: "manifest/action:1",
        lConfigs: [
            { sId: "paint_pose_config", sDTI: "/catharsys/generative/paint_pose_data:1", sForm: "file/json", bAddToPath: false }
        ],
        lDeps: [ "label" ] // <- this should be the name of the action you use for  labeling
    },
    // ...

trial.json5:

    // ...
    mConfigs: {
        ... 
        paint_pose_config: [ "../generative/openpose"],
        ...
    },
    // ...

launch.json5:

    // ...
    "paint_pose": {
        sDTI: "/catharsys/launch/action:1.0",
        sActionDTI: "/catharsys/action/generative/paint_pose:1.0",
        mConfig: {
            sDTI: "/catharsys/launch/args:1.1",
            sInfo: "Create an open pose pose image for processing with multi control nets",
            sExecFile: "../exec/py_std_v1",
            iConfigGroups: 1,
            iFrameGroups: 1
        }     
    },
    // ...

INPORTANT: Copy the file openpose.json5 from the examples folder from this repository to generative/openpose.json5 in your config.


Finally, you can call the action to generate the pose image needed by the multi control net:

    cathy ws launch -c config/your_workspace -a paint_pose


### Add control net action to your catharsys config

For using Takuma's control net, you now have to add the following parts to your config files.

manifest.json5:

    // ...
    generative: {
        sDTI: "manifest/action:1",
        lConfigs: [
            { sId: "cnet_model", sDTI: "/catharsys/generative/model-id:1", sForm: "value", bAddToPath: true },
            { sId: "cnet_config", sDTI: "/catharsys/generative/data:1", sForm: "file/json", bAddToPath: true  }
        ],
        lDeps: [ "render/std" ] // <- this should be your standard render action
    },
    // ...

trial.json5:

    // ...
    mConfigs: {
        // ...
        cnet_model: ["Takuma-Diffusers"],
        cnet_config: ["generative/example" ],
        // ...
    },
    // ...

launch.json5:

    "generative": {
        sDTI: "/catharsys/launch/action:1.0",
        sActionDTI: "/catharsys/action/generative/apply:1.0",
        mConfig: {
            sDTI: "/catharsys/launch/args:1.1",
            sInfo: "Perform generative action using control net.",
            // sExecFile: "../exec/py_lsf_v1", // <- use this when using lsf
            sExecFile: "../exec/py_std_v1",
            iConfigGroups: 1,
            iFrameGroups: 1
        }     
    },

Finally, you need a config file generative/example.json5. Here, several control nets are added as examples. Use the ones you are interested in:

    {
        sDTI: "/catharsys/generative/data:1",

        __locals__: {
            sModelPath: "/path/to/your/models" // <- add here the path to the models folder
        },

        mInputs: {
            // here, all relative path to the outputs of previous results should be added
            // these will be referenced in the sInput to the control nets below
            Depth: "Depth",
            OpenPose: "AT_Label/asp_skeleton/PoseImage",
            SemSeg: "AT_Label/semseg_only/Preview"

        },

        mConfig: {
            mParams: {
                pretrained_model_name_or_path: "${sModelPath}/stable-diffusion-v1-5",
                local_files_only: true,
            },        
            mControlNets: {
                Depth: {
                    // these parameters are directly passed to from_pretrained
                    mParams: {
                        pretrained_model_name_or_path: "${sModelPath}/sd-controlnet-depth",
                        local_files_only: true,
                    },
                    fWeight: 0.6,
                    sInput: "Depth",
                    mPreprocess: [
                        "Normalize",
                        "Invert",
                    ]
                },
                OpenPose: {
                    mParams: {
                        pretrained_model_name_or_path: "${sModelPath}/control_v11p_sd15_openpose",
                        local_files_only: true,
                    },
                    fWeight: 1.0,
                    sInput: "OpenPose",
                },
                SemSeg: {
                    // these parameters are directly passed to from_pretrained
                    mParams: {
                        pretrained_model_name_or_path: "${sModelPath}/control_v11p_sd15_seg",
                        local_files_only: true,
                    },
                    fWeight: 0.75,
                    sInput: "SemSeg",
                },               
            },
            sPrompt: "men in black suits with ties and dark sunglasses (as in the film men in black or FBI agents)",
            sNegativePrompt: "bad quality, low res"
        }
    }

Now, you have everything to perform the generative action:

    cathy ws launch -c config/your_workspace -a generative

Have fun!

## Futher remarks

Prompt engineering is the new art. For getting more realistic results, consider these sources:
* https://stable-diffusion-art.com/realistic-people/


Prompt Free Diffusion
==============
This plugin provides an interface to use Prompt-free-Diffusion within Catharsys.

Installation. Run scripts/get_prompt_free_diffusion.sh 

Using the PFD Action
==============
To use this action, integrate it into your workspace accordingly.

manifest.json5:
```
    promptfreediffusion: {
      std:{
        sDTI: "manifest/action:1",
        lConfigs: [       
            // add the input image even if it is not used, mainly to get the frames etc
            { sId: "cnet_model", sDTI: "/catharsys/generative/model-id:1", sForm: "value", bAddToPath: false },
            { sId: "cnet_config", sDTI: "/catharsys/generative/data:1", sForm: "file/json", bAddToPath: true},          
        ],
        lDeps: [ "render/std" ]
      },
    }, 
```
trial.json5:

```
    cnet_model: ["Prompt-Free-Diffusion"],
    cnet_config: ["generative/example_pfd_config"],
```

launch.json5:
```
    "promptfreediffusion": {
        std: {
          sDTI: "/catharsys/launch/action:1.0",
          sActionDTI: "/catharsys/action/promptfreediffusion/apply:1.0",
          mConfig: {
              sDTI: "/catharsys/launch/args:1.1",
              sInfo: "Perform generative action using control net.",
              // sExecFile: "../exec/py_lsf_v1",
              sExecFile: "../exec/py_std_v1",
              // sExecFile: "../exec/py_auto",
              iConfigsPerGroup: 40,
              iFramesPerGroup: 1,
              iRangeCount:1,
              iRenderQuality: 4,
          }     
        },
    }
```

Finally, a config file defining the arguments for prompt free diffusion we already referred to in the trial.json above is needed:

```
{
    sDTI: "/catharsys/generative/data:1",

    mInputs: {
        Depth: "Depth",
    },

    mConfig: {
        mParams: {
            prompt_free_diffusion_root_path: "path to the prompt free diffusion repo",
            reference_image: "Path to the reference image to be used"
            // Diffusers supported by prompt free diffusion
            sDiffuser_id: "Deliberate-v2.0",
                // Possible Values:
                // 'SD-v1.5'             
                // 'OpenJouney-v4'       
                // 'Deliberate-v2.0'     
                // 'RealisticVision-v2.0'
                // 'Anything-v4'         
                // 'Oam-v3'              
                // 'Oam-v2'
            // Seecoders supported by prompt free diffusion
            sSeecoder_id: "SeeCoder",
                // 'SeeCoder'      
                // 'SeeCoder-PA'   
                // 'SeeCoder-Anime'             
            iSeed: 20,
            fCFGScale: 2.0
        },        
        mControlNets: {
            Depth: {
                sInput: "Depth",
                mPreprocess: [
                    "Normalize",
                    "Invert",
                ]
            },
        },
    }
}
```
