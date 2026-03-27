[![Molecular+](https://github.com/u3dreal/molecular-plus/actions/workflows/release.yml/badge.svg)](https://github.com/u3dreal/molecular-plus/actions/workflows/release.yml)

# Molecular Plus – Advanced Particle Simulation for Blender

**Molecular Plus** is an advanced particle simulation addon for Blender (4.2 – 5.1+) that brings molecular dynamics and soft-body physics to your 3D scenes. Originally based on the molecular addon by pyroevil, this extended version adds powerful scene creation tools and a completely rewritten high-performance simulation engine.

[![Video Thumbnail](https://img.youtube.com/vi/u3Eq1POk_Bc/maxresdefault.jpg)](https://www.youtube.com/watch?v=u3Eq1POk_Bc)
*Animation by [The Marble Mechanic](https://www.youtube.com/@TheMarbleMechanic)*



https://github.com/user-attachments/assets/3c65f569-e341-4140-b5a7-9933dffe702d
*1 Million Particles simulation by u3dreal*

![Molecular Simulation](https://github.com/u3dreal/molecular-plus/blob/main/doc/molecular-3.jpg)
*Image by tinkerboy123*

![Molecular Plus](https://github.com/u3dreal/molecular-plus/blob/main/doc/molecular-plus.png)

## Key Features

- **Fast Scene Setup**: Integrated create panel for rapid scene configuration
- **Physics Tab Integration**: Cleanly organized in Blender's physics section where it belongs
- **N-Panel Access**: Quick access to simulation controls and settings
- **Collision Detection**: Advanced self-collision and object-collision systems
- **Link System**: Create molecular bonds and structural links between particles
- **Material Presets**: Pre-configured matter types (sand, water, iron, custom)
- **Multi-Platform Support**: Windows (x64), macOS (ARM64 & Universal), Linux (x64)

## What's New in Version 1.21.9

**Complete Spatial Hash Engine Rewrite**: The latest version features a ground-up replacement of the KD-tree spatial search algorithm with a **spatial hash grid implementation**, delivering:

- **2-4x faster** simulation setup
- **1.5-3x faster** neighbor queries
- **O(1) average query time** vs O(log n) for the previous KD-tree
- **Better multi-threading** with lock-free parallel construction
- **Improved cache performance** through contiguous memory access
- **More consistent frame times** with predictable performance

## Technical Highlights

- **Cython-based core** for maximum performance
- **Multi-threaded simulation** utilizing all available CPU cores
- **O(n) construction time** for spatial data structures
- **Dynamic neighbor lists** with exponential growth strategy
- **Block-based memory allocation** for reduced fragmentation

## Use Cases

- Soft body simulations
- Granular materials (sand, gravel)
- Fluid-like behaviors
- Molecular structures
- Destructible objects
- Cloth and fabric simulation

## Downloads

Get the latest release with pre-compiled wheels for all supported platforms:

**[Download Molecular Plus](https://github.com/u3dreal/molecular-plus/releases)**

## Community & Support

Join the community on [Discord](https://discord.gg/tAwvNEAfA3) for support and discussions. 
More information available at [q3de.com/research/molecular/](http://q3de.com/research/molecular/).

Follow on X (Twitter): [@u3dreal](https://twitter.com/u3dreal)

## Support Development

If you find this addon helpful and want to support future development, please consider making a donation:

[![Donate](https://www.paypalobjects.com/en_US/DK/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=J7W7MNCKVBYAA)

## License

GPL-3.0-or-later
