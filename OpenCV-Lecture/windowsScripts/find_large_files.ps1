$path = "C:\"  # Change to your preferred drive/folder
$sizeThresholdMB = 500  # Find files larger than 500MB

Get-ChildItem -Path $path -Recurse -File | 
    Where-Object { $_.Length -gt ($sizeThresholdMB * 1MB) } |
    Sort-Object Length -Descending |
    Select-Object FullName, @{Name="SizeMB";Expression={($_.Length/1MB) -as [int]}} |
    Format-Table -AutoSize
