$proj = (Get-Location).Path
$dest = Join-Path $proj 'resources'
if(-not (Test-Path $dest)){
    New-Item -ItemType Directory -Path $dest | Out-Null
}

# Locate 7z / 7za
$p = Get-Command 7za -ErrorAction SilentlyContinue
if(-not $p){ $p = Get-Command 7z -ErrorAction SilentlyContinue }
if(-not $p){ $p = Get-Command '7z.exe' -ErrorAction SilentlyContinue }
if($p){
    Copy-Item $p.Source (Join-Path $dest '7za.exe') -Force
    Write-Output "COPIED_7Z:$($p.Source)"
} else {
    Write-Output "7Z_NOT_FOUND"
}

# Locate unrar
$u = Get-Command unrar -ErrorAction SilentlyContinue
if($u){
    Copy-Item $u.Source (Join-Path $dest 'unrar.exe') -Force
    Write-Output "COPIED_UNRAR:$($u.Source)"
} else {
    Write-Output "UNRAR_NOT_FOUND"
}
