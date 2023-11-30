
$ModelPath = './models'
if (-Not (Test-Path -Path $ModelPath)) {
    mkdir $ModelPath
}
cd $ModelPath

if (Test-Path -Path './control_v11p_sd15_seg') {
    return $true
}

git clone https://huggingface.co/lllyasviel/control_v11p_sd15_seg
if (-Not $?) {
    Write-Output "Error cloning Control Net SemSeg"
    cd ..
    return $false
}

cd control_v11p_sd15_seg
git checkout 210682041b41097834006a910b8773f423343900
cd ..

return $true
