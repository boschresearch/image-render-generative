# start proxy
module load cntlm
cntlm-start


# create conda environment
conda create --prefix ./envs/Takuma-Diffusers pip
conda activate ./envs/Takuma-Diffusers

# install pytorch. See also https://pytorch.org/get-started/locally/
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

python -m pip install transformers 
# ensure that CUDA >= 11.7.0 is installed before installing xformers
# The pip install of xformers can take ages (> 1h)
python -m pip install xformers

# this is the conda install method
# conda install xformers -c xformers

# install opencv
python -m pip install opencv-python

# download and install takuma's diffusers variant
mkdir ./models
cd ./models/

git clone https://github.com/takuma104/diffusers.git Takuma-Diffusers -b multi_controlnet
cd Takuma-Diffusers
git reset --hard 6bd8854cbb050e938349ce4730249aae3800fc50
python -m pip install -e .[torch]
cd ..

# call to download stable diffusion and control net networks
# this will download lots of files, you might want to delete
# the .git folder afterwards in each repository

# This clone downloads a ca. 25GB from git lfs, which may take quite some time
git clone https://huggingface.co/runwayml/stable-diffusion-v1-5
cd stable-diffusion-v1-5
git checkout aa9ba505e1973ae5cd05f5aedd345178f52f8e6a
git lfs pull
cd ..

git clone https://huggingface.co/lllyasviel/sd-controlnet-depth
cd sd-controlnet-depth
git checkout 35e42a3ea49845b3c76f202f145f257b9fb1b7d4
git lfs pull
cd ..

# git clone https://huggingface.co/lllyasviel/sd-controlnet-openpose
# cd sd-controlnet-openpose
# git checkout df796456519d1ac5dbe674caa0653fcc9673bca8
# cd ..

git clone https://huggingface.co/lllyasviel/control_v11p_sd15_openpose
cd control_v11p_sd15_openpose
git checkout e2d5e1447ed025eb05932704c6dc6c0677cec7c0
git lfs pull
cd ..

git clone https://huggingface.co/lllyasviel/control_v11p_sd15_seg
cd control_v11p_sd15_seg
git checkout 210682041b41097834006a910b8773f423343900
git lfs pull
cd ..

cd ..
