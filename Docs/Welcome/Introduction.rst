Introduction
============

Features
--------

* Multiplayer
* Replay
* Teams


Project Structure
-----------------

.. code-block:: text

   LyraStarterGame
   ├── Source
   │   ├── LyraEditor               <= Editor Customization
   │   ├── LyraGame                 <= Game Code
   │   ├── LyraClient.Target.cs     <= Client only target
   │   ├── LyraEditor.Target.cs     <= Editor target
   │   ├── LyraGame.Target.cs       <= Game target
   │   ├── LyraGameEOS.Target.cs 
   │   └── LyraServer.Target.cs     <= Dedicated server target
   └── Plugins
       ├── AsyncMixin 
       ├── CommonGame 
       ├── CommonLoadingScreen
       ├── CommonUser
       ├── GameFeatures
       ├── GameplayMessageRouter
       ├── GameSettings
       ├── GameSubtitles
       ├── LyraExampleContent
       ├── LyraExtTool
       ├── ModularGameplayActors
       ├── PocketWorlds
       └── UIExtension


Getting Started
---------------

.. code-block:: text

   git clone --recurse-submodules -j8 init https://github.com/kiwi-lang/LyraStarterGame.git
   cd LyraStarterGame
   uecli ubt regenerate --vscode
   code LyraStarterGame.code-workspace

   # Run without debugger: ctrl+shift B
   # Run with    debugger: F5

