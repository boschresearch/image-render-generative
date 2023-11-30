
$ModelPath = './models'
if (-Not (Test-Path -Path $ModelPath)) {
    mkdir $ModelPath
}
cd $ModelPath

if (Test-Path -Path './sd-controlnet-depth') {
    return $true
}

git clone https://huggingface.co/lllyasviel/sd-controlnet-depth
if (-Not $?) {
    Write-Output "Error cloning Control Net Depth"
    cd ..
    return $false
}

cd sd-controlnet-depth
git checkout 35e42a3ea49845b3c76f202f145f257b9fb1b7d4
cd ..

return $true
