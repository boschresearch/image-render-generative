# start proxy


# create conda environment
$EnvPath = './envs/Takuma-Diffusers'
if (-Not (Test-Path -Path $EnvPath)) {
    conda create --prefix $EnvPath pip
}
conda activate $EnvPath

# install pytorch with cuda 11.8 support 
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

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
pip install transformers
pip install xformers

cd ..

# call to download stable diffusion and control net networks
# this will download lots of files, you might want to delete
# the .git folder afterwards in each repository

$PSScriptRoot/get_sd.ps1
$PSScriptRoot/get_sd_depth.ps1
$PSScriptRoot/get_sd_openpose.ps1
$PSScriptRoot/get_sd_semseg.ps1

cd ..
