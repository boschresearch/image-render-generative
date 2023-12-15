$EnvPath = "$PSScriptRoot/../envs/Takuma-Diffusers"
if (-Not (Test-Path -Path $EnvPath)) {
    Write-Output "Environment 'Takuma-Diffusers' not found"
}
conda activate $EnvPath
