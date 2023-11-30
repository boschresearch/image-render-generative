
$ModelPath = './models'
if (-Not (Test-Path -Path $ModelPath)) {
    mkdir $ModelPath
}
cd $ModelPath

if (Test-Path -Path './control_v11p_sd15_openpose') {
    return $true
}

git clone https://huggingface.co/lllyasviel/control_v11p_sd15_openpose
if (-Not $?) {
    Write-Output "Error cloning Control Net OpenPose"
    cd ..
    return $false
}

cd control_v11p_sd15_openpose
git checkout e2d5e1447ed025eb05932704c6dc6c0677cec7c0
cd ..

return $true
