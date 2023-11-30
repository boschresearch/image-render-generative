# start proxy
module load cntlm
cntlm-start


# create conda environment
conda create --prefix ./envs/Prompt-Free-Diffusion python=3.10
conda activate ./envs/Prompt-Free-Diffusion

# python -m pip install torch==2.0.1+cu117 torchvision==0.15.1 --extra-index-url https://download.pytorch.org/whl/cu117 --force-reinstall

python -m pip install torch==2.0.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

mkdir ./models
cd ./models/

# clone pfd repo, patch it and install requirements
git clone https://github.com/SHI-Labs/Prompt-Free-Diffusion.git
cd Prompt-Free-Diffusion
git reset --hard ff5b50be8c0be0def0141f1493c90bdb2e2ee35f
git apply  ../../scripts/patches/0001-patch-app.py-to-perform-__main__-check-to-allow-impo.patch
git apply  ../../scripts/patches/0002-Enable-execution-from-any-folder-via-rootfolder-argu.patch
python -m pip install -r requirements.txt


cd ..


# this downloads the weights of the networks and sets up a symbolic link so that the weights can be found by pfd
git clone https://huggingface.co/shi-labs/prompt-free-diffusion
cd prompt-free-diffusion
git reset --hard b9b8a9079e2457f4c5af77d7e3261e03a5747e46
# does not seem to work...need to revisit this, using git lfs pull instead
# git lfs fetch -I pretrained/controlnet/control_sd15_depth_slimmed.safetensors
# git lfs fetch -I pretrained/pfd/diffuser/Deliberate-v2-0.safetensors
# git lfs fetch -I pretrained/pfd/seecoder/seecoder-v1-0.safetensors
# git lfs fetch -I pretrained/pfd/vae/sd-v2-0-base-autokl.pth
git lfs pull

cd ..

# Establish a symbolic link to create the folder structure expected py pfd
cd Prompt-Free-Diffusion
ln -s -T ../prompt-free-diffusion/pretrained pretrained



