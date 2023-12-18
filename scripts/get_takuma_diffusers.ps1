# start proxy

# You need to have cuda toolkit installed and cudnn.
# Here is a page with a step by step guide for pytorch: https://medium.com/@harunijaz/a-step-by-step-guide-to-installing-cuda-with-pytorch-in-conda-on-windows-verifying-via-console-9ba4cd5ccbef
# Install cuda toolkit: https://developer.nvidia.com/cuda-11-8-0-download-archive
# This may also help:
#   conda install -c conda-forge cudatoolkit

# create conda environment
$EnvPath = './envs/Takuma-Diffusers'
if (-Not (Test-Path -Path $EnvPath)) {
    conda create --prefix $EnvPath pip python=3.10
}
conda activate $EnvPath

# install pytorch with cuda 11.8 support 
pip3 install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118

# download and install takuma's diffusers variant
$ModelPath = './models'
if (-Not (Test-Path -Path $ModelPath)) {
    mkdir $ModelPath
}
cd $ModelPath

git clone https://github.com/takuma104/diffusers.git Takuma-Diffusers -b multi_controlnet
if (-Not $?) {
    Write-Output "Error cloning Takuma-Diffusers"
    cd ..
    return $false
}

cd Takuma-Diffusers

git reset --hard 6bd8854cbb050e938349ce4730249aae3800fc50

pip install -e .[torch]
pip3 install xformers==0.0.22.post4 --index-url https://download.pytorch.org/whl/cu118
pip3 install transformers
pip3 install opencv-python==4.6.0.66

cd ..

# call to download stable diffusion and control net networks
# this will download lots of files, you might want to delete
# the .git folder afterwards in each repository

& $PSScriptRoot/"get_sd.ps1"
& $PSScriptRoot/"get_sd_depth.ps1"
& $PSScriptRoot/"get_sd_openpose.ps1"
& $PSScriptRoot/"get_sd_semseg.ps1"

cd ..
