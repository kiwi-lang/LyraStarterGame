Flow
====

Summary
-------

Using this setup we always seamless travel between maps.
A base setup is loaded as a client (GameMode, Character etc...)
The requirements for a maps are defined in an "Experience" (ULyraExperienceDefinition)
which will add gameplay features (components to actors, Widget)

Setup Overview
--------------

* Configuration
   * Game Default Map
      * L_LyraFrontEnd
   
   * Sever Default Map
      * L_Expanse
   
   * World Settings Class: contains the `ULyraExperienceDefinition` to load when the map is activated
      * LyraWorldSettings
         * AWorldSettings

   * Game Instance
      * B_LyraGameInstance
         * LyraGameInstance > UCommonGameInstance > UGameInstance 

   * LyraLocalPlayer: Stay active across maps
      * UCommonLocalPlayer > ULocalPlayer > UPlayer
      * ILyraTeamAgentInterface > IGenericTeamAgentInterface

   * GameUser Settings Class:
      * ULyraSettingsLocal > UGameUserSettings > UObject

   * Default Game Mode
      * B_LyraGameMode
         * LyraGameMode > AModularGameModeBase > AGameModeBase
      * LyraGameSession
         * AGameSession
      * LyraGameState
         * AModularGameStateBase > AGameStateBase
         * IAbilitySystemInterface
      * LyraPlayerController 
         * ACommonPlayerController > AModularPlayerController > APlayerController
         * ILyraCameraAssistInterface
         * ILyraTeamAgentInterface > IGenericTeamAgentInterface
      * LyraPlayerState
         * AModularPlayerState > APlayerState
         * IAbilitySystemInterface
         * ILyraTeamAgentInterface > IGenericTeamAgentInterface
      * LyraCharacter > AModularCharacter
         * IAbilitySystemInterface
         * IGameplayCueInterface
         * IGameplayTagAssetInterface
         * ILyraTeamAgentInterface > IGenericTeamAgentInterface
      * LyraHUD
         * AHUD
      * LyraReplayController
         * ALyraPlayerController
            * ACommonPlayerController > AModularPlayerController > APlayerController
            * ILyraCameraAssistInterface
            * ILyraTeamAgentInterface > IGenericTeamAgentInterface
      * SpectatorPawn

   * UGameUIManagerSubsystem
      * DefaultGame.ini
         * [/Script/LyraGame.LyraUIManagerSubsystem]
           DefaultUIPolicyClass=/Game/UI/B_LyraUIPolicy.B_LyraUIPolicy_C
      
      * In turn ``B_LyraUIPolicy_C`` defines Layout Class to be ``W_OverallUILayout``.
        The layout is a simple Widget with an overlay and widget stacks
         * GameLayer: HUD (tag: ``UI.Layer.Game``)
         * GameMenu: Inventory (tag: ``UI.Layer.GameMenu``)
         * MenuStack: Setting Screen (tag: ``UI.Layer.Menu``)
         * ModalStack: Confirmation (tag: ``UI.Layer.Modal``)


Client Flow
-----------

* UGameInstance::CreateLocalPlayer
   * UCommonGameInstance::AddLocalPlayer
      * UGameUIManagerSubsystem::NotifyPlayerAdded
         * CreateLayoutWidget
            * Class: /GameUI/W_OverallUILayout
   
* Open(/Game/System/FrontEnd/Maps/L_LyraFrontEnd.umap)
   * This loads the menu map as authority 
   * ``InitGame``
   * ``HandleMatchAssignmentIfNotExpectingOne``
      * ``ALyraWorldSettings->GetDefaultGameplayExperience()``
         * In the `L_LyraFrontEnd` case this is `B_LyraFrontEndExperience`
      * ``OnMatchAssignmentGiven(ExperienceId, ExperienceIdSource)``
         * GameState::ULyraExperienceManagerComponent->SetCurrentExperience
            * resolve ``FPrimaryAssetId ExperienceId`` to an actual asset
            * ``StartExperienceLoad()``
            * Load assets associated with the experience
            * OnExperienceLoadComplete
               * Gather GameFeaturePluginURLs
               * for each GameFeature
                  * UGameFeaturesSubsystem::Get().LoadAndActivateGameFeaturePlugin
                     * OnGameFeaturePluginLoadComplete
                        * NumberOfFeaturesToLoad -= 1
                        * if NumberOfFeaturesToLoad == 0
                           * OnExperienceFullLoadCompleted
            * OnExperienceFullLoadCompleted
            * Execute Actions
               * for each Actions
                  * Action->OnGameFeatureRegistering();
                  * Action->OnGameFeatureLoading();
                  * Action->OnGameFeatureActivating(Context);
            * OnExperienceLoaded_HighPriority.Broadcast(CurrentExperience);
            * OnExperienceLoaded.Broadcast(CurrentExperience);
            * OnExperienceLoaded_LowPriority.Broadcast(CurrentExperience);
            * ULyraSettingsLocal::Get()->OnExperienceLoaded();

      * ``OnExperienceLoaded``
         * RestartPlayer(PlayerController)


* Front End Experience
   * Actions
      * Disable Split Screen
      * Add Component B_LyraFrontEndStateComponent to LyraGameState (Client Only)
         * B_LyraFrontEndStateComponent
            * ULyraFrontendStateComponent > UGameStateComponent > UGameFrameworkComponent > UActorComponent
               * ILoadingProcessInterface
            * ExperienceComponent->CallOrRegister_OnExperienceLoaded_HighPriority(FOnLyraExperienceLoaded::FDelegate::CreateUObject(this, &ThisClass::OnExperienceLoaded));
            * OnExperienceLoaded
               * Flow
                  * Wait for User init
                  * Show Press Start Screen
                     * UPrimaryGameLayout -> push (FrontendTags::TAG_UI_LAYER_MENU, PressStartScreenClass)
                  * Join / Request Session
                     * Join / Rejoin a session might cancel showing the main menu altogether
                  * Show MainScreen
                     * UPrimaryGameLayout -> push (FrontendTags::TAG_UI_LAYER_MENU, MainScreenClass)

      * Add Component B_MusicManagerComponent_FE to LyraGameState (Client Only)
      * Use Frontend Perf Settings
         * UApplyFrontendPerfSettingsAction > UGameFeatureAction > UObject
            * OnGameFeatureActivating
               * ULyraSettingsLocal::Get()->SetShouldUseFrontendPerformanceSettings(true);
                  * UpdateEffectiveFrameRateLimit
      * Add Widgets: this does not do anything because we have no HUD to add this widget to
         * Widgets
            * Class: W_PerfStatContainer_FrontEnd
            * Slot: HUD.Slot.PerfStats.Text
         * UGameFeatureAction_AddWidgets > UGameFeatureAction_WorldActionBase > UGameFeatureAction
            * AddExtensionHandler(HUDClass, &ThisClass::HandleActorExtension)
               *  UUIExtensionSubsystem* ExtensionSubsystem = HUD->GetWorld()->GetSubsystem<UUIExtensionSubsystem>();
                  ActorData.ExtensionHandles.Add(ExtensionSubsystem->RegisterExtensionAsWidgetForContext(Entry.SlotID, LocalPlayer, Entry.WidgetClass.Get(), -1));

* `Game/Environments/B_LoadRandomLobbyBackground.uasset`
   * Fetch a list of assets matching LyraLobbyBackground
   * Load one random asset from the list
   * Travel to the map


* Play Lyra
   * Push Widget W_ExperienceSelectionScreen
   * Quick Play
      * Login for Online Play
      * Select experience to host from W_Experience_list
         * ``LyraStarterGame/Plugins/GameFeatures/ShooterMaps/Content/System/Playlists/DA_Expanse_TDM.uasset``
         * Map ID
         * Experience ID
         * Title
         * Loading Screen
      * Create Hosting Request
      * QuickPlaySession
         * Join or Host session
            * HostSession
               * CreateOnlineSessionInternal(LocalPlayer, Request);
               * CreateOnlineSessionInternalOSSv1
               * IOnlineSessionPtr Sessions->CreateSession


Server Flow
-----------

* Open(/LyraStarterGame/Plugins/GameFeatures/ShooterMaps/Content/Maps/L_Expanse.umap)
   * ``InitGame``
   * ``HandleMatchAssignmentIfNotExpectingOne``
      * ``ALyraWorldSettings->GetDefaultGameplayExperience()``
         * In the `L_Expanse` case this is `B_ShooterGame_Elimination`
      * ``TryDedicatedServerLogin``
         * This only gets triggered if the experience is not valid
           It then loads `B_LyraDefaultExperience` as fall back.
      * ``OnMatchAssignmentGiven(ExperienceId, ExperienceIdSource)``




.. comment::

   Seamless travel


      * UGameMapsSettings::TransitionMap 
      * AGameModeBase::bUseSeamlessTravel  = true
      * AGameModeBase::GetSeamlessTravelActorList 
      * Actors that persist
         * GameMode (server)
         * PlayerController with PlayerState (server)