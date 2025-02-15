$destination = "$env:USERPROFILE\Desktop\Cleaned" # Define destination folder
if (!(Test-Path -Path $destination)) {
    New-Item -ItemType Directory -Path $destination
}

# File extensions to clean up
$extensions = @("*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.pdf", "*.docx", "*.xlsx", "*.zip", "*.mp4")

# Move each file type into the Cleaned folder
foreach ($ext in $extensions) {
    Get-ChildItem "$env:USERPROFILE\Desktop\" -Filter $ext | Move-Item -Destination $destination -Force
}

Write-Host "Desktop cleanup complete. Files moved to: $destination"
