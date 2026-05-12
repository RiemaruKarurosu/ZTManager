<h1 align="center"> ZeroTier-GTK </h1>
<h3 align="center"> GTK4 + Libadwaita client for ZeroTier </h3>
<p align="center"><img src="data/icons/hicolor/scalable/apps/io.github.riemarukarurosu.ZeroTierGTK.svg" width="100" height="100"></p> 
<div align="center">
     
  <a href="">[![Licence](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)</a>
  <a href="">[![Version](https://img.shields.io/badge/Version-2.0.0--BETA-green)](https://github.com/RiemaruKarurosu/ZeroTier-GTK/releases)</a>
    
</div>

ZeroTier-GTK is a modern GTK4/Libadwaita client for ZeroTier, specifically designed for GNOME users. It provides a seamless way to manage your virtual private networks with a premium look and feel.

## Features
- [x] Modern GTK4 / Libadwaita interface.
- [x] Detect and manage the ZeroTier service status.
- [x] Automatic token retrieval (Host Mode) or manual entry.
- [x] Join and leave networks easily.
- [x] View detailed network information (MAC, MTU, IPs).
- [x] Real-time node/peer visualization.
- [x] Auto-refreshing status and network list.
- [x] Secure authentication with masked token input.

## Installation
To build and install locally:

```bash
flatpak-builder build-dir io.github.riemarukarurosu.ZeroTierGTK.json --user --install --force-clean
```

## Screenshots


![Screenshot 1](https://i.imgur.com/ipBgTwA.png)
![Screenshot 2](https://i.imgur.com/MRC9oKS.png)
![Screenshot 3](https://i.imgur.com/Z1pqvhK.png)
![Screenshot 4](https://i.imgur.com/tSo3VBH.png)

## License
GPL-3.0-or-later
