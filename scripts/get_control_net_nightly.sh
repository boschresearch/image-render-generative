module load cntlm
cntlm-start
 
git clone https://github.com/lllyasviel/ControlNet-v1-1-nightly.git ./models/ControlNet-v1-1-nightly
 
cd ControlNet-v1-1-nightly

git reset --hard 3f324c008ce086ceea721c8eab8c74399fa68b4e
 
cd models
 
wget https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_depth.pth
 
wget https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_lineart.pth

wget https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.ckpt
 
cd ..
 
conda env create --prefix ./envs/control-v11-nightly -f models/ControlNet-v1-1-nightly/environment.yaml