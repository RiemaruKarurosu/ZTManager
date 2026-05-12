<h1 align="center"> ZeroTier-GTK </h1>
<h3 align="center"> GTK + Libadwaita version of Zerotier GUI </h3>
<p align="center"><img src="https://raw.githubusercontent.com/RiemaruKarurosu/ZeroTier-GTK/master/data/icons/hicolor/scalable/apps/org.zerotier.ZerotierGTK.svg" width="100" height="100"></p> 
<div align="center">
    
  <a href="">[![Licence][licence]][licence-url]</a>
  <a href="">[![Latest][version]][version-url]</a>
    
</div>

[licence]: https://img.shields.io/badge/License-GPLv3-blue.svg
[version]: https://img.shields.io/badge/Version-1.4.4-red
[version-url]: https://github.com/RiemaruKarurosu/ZeroTier-GTK/releases
[licence-url]: https://www.gnu.org/licenses/gpl-3.0

ZeroTier-GTK is a GTK+ Libadwaita version of the ZeroTier GUI, specifically designed for GNOME users. It is a fork of the original ZeroTier-GUI project, modernized and improved for Flatpak environments.

## Features
The following features are supported in ZeroTier-GTK:

- [X] Detect if the zerotier-one service is running
- [X] Provide the option to start the service
- [X] Install ZeroTier-One natively from within the app (Host Mode)
- [X] Use custom API tokens for remote connectivity (Manual Mode)
- [X] Show networks
- [X] Add a new network
- [X] View detailed settings of a network
- [X] Disconnect from a network
- [X] Remove a network
- [X] Show peers

## Screenshots
Please keep in mind that the screenshots provided are a work in progress, and the final version may differ.

![Screenshot 1](https://i.imgur.com/ipBgTwA.png)
![Screenshot 2](https://i.imgur.com/MRC9oKS.png)
![Screenshot 3](https://i.imgur.com/Z1pqvhK.png)
![Screenshot 4](https://i.imgur.com/tSo3VBH.png)

## Dependencies & Architecture
**Important:** ZeroTier-GTK is designed to run as a Flatpak, but the ZeroTier service (`zerotier-one`) **must be installed on your host system**. Flatpaks cannot create the virtual network interfaces (TUN/TAP) required by ZeroTier due to sandbox limitations. 
The app provides an automatic get-token via `pkexec` when "Host Mode" is enabled. If you prefer, you can also connect to a remote ZeroTier node by providing your token in "Manual Mode".

## Download and Installation
ZeroTier-GTK can be compiled from source using `meson` and `flatpak-builder` (or via GNOME Builder).

To build the Flatpak via command line:
```bash
flatpak-builder build-dir org.zerotier.ZerotierGTK.json --user --install --force-clean
```

## How to Contribute
If you are interested in contributing to ZeroTier-GTK, please refer to the project's [contribution guidelines](https://github.com/RiemaruKarurosu/ZeroTier-GTK/wiki/How-to-contribute). Additionally, you can find documentation for the Zerotierlib used in this project [here](https://github.com/RiemaruKarurosu/ZeroTier-GTK/wiki/Zerotierlib-DOCS-v.1.4#zerotiernetwork/).

## Troubleshooting
As mentioned earlier, ZeroTier-GTK is still in development and should not be used for actual purposes. Therefore, troubleshooting guidance is not available at this time.

## Alternatives
If you require a working solution for managing ZeroTier networks, you can consider using the original [ZeroTier-GUI](https://github.com/tralph3/ZeroTier-GUI) project. It is a well-established and functional application that has undergone a rewrite.

## Special Thanks
Special thanks to the following individuals for their contributions to ZeroTier-GTK:
- [@tralph3](https://github.com/tralph3) - Creator of ZeroTier-GUI
- [@Ivan-Rosales](https://github.com/Ivan-Rosales)
