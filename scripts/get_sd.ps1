
$ModelPath = "$PSScriptRoot/../models"
if (-Not (Test-Path -Path $ModelPath)) {
    mkdir $ModelPath
}
cd $ModelPath

if (Test-Path -Path './stable-diffusion-v1-5') {
    return $true
}

git clone https://huggingface.co/runwayml/stable-diffusion-v1-5
if (-Not $?) {
    Write-Output "Error cloning Stable Diffusion"
    cd ..
    return $false
}

cd stable-diffusion-v1-5
git checkout aa9ba505e1973ae5cd05f5aedd345178f52f8e6a
cd ..

return $true
