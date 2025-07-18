# Adapted from < https://stackoverflow.com/questions/68100663/how-do-i-install-winget-on-windows-server-2019> 
# Install VCLibs
Add-AppxPackage ' https://aka.ms/Microsoft.VCLibs.x64.14.00.Desktop.appx'

# Install Microsoft.UI.Xaml.2.7.3 from NuGet
#Invoke-WebRequest -Uri https://www.nuget.org/api/v2/package/Microsoft.UI.Xaml/2.7.3 -OutFile .\microsoft.ui.xaml.2.7.3.zip
# Expand-Archive .\microsoft.ui.xaml.2.7.3.zip
# Add-AppxPackage .\microsoft.ui.xaml.2.7.3\tools\AppX\x64\Release\Microsoft.UI.Xaml.2.7.appx
Add-AppxPackage -Path https://github.com/microsoft/microsoft-ui-xaml/releases/download/v2.8.5/Microsoft.UI.Xaml.2.8.x64.appx

# Install the latest release of Microsoft.DesktopInstaller from GitHub
# Invoke-WebRequest -Uri https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle -OutFile .\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle
# Add-AppxPackage .\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle
IWR -Uri https://github.com/microsoft/winget-cli/releases/download/v1.6.2771/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle -OutFile .\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle
IWR -Uri https://github.com/microsoft/winget-cli/releases/download/v1.6.2771/27abf0d1afe340e7a64fb696056b2672_License1.xml -OutFile .\27abf0d1afe340e7a64fb696056b2672_License1.xml
Add-AppxProvisionedPackage -Online -PackagePath .\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle -LicensePath .\27abf0d1afe340e7a64fb696056b2672_License1.xml -Verbose
