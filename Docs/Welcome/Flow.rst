Flow
====

Summary
-------

Using this setup we always seamless travel between maps.
A base setup is loaded as a client (GameMode, Character etc...)
The requirements for a maps are defined in an "Experience" (ULyraExperienceDefinition)
which will add gameplay features (components to actors, Widget, etc...) when needed.


Setup Overview
--------------

* Configuration
   * Game Default Map
      * L_LyraFrontEnd
   
   * Sever Default Map
      * L_Expanse
   
   * World Settings Class: contains the ``ULyraExperienceDefinition`` to load when the map is activated
      * LyraWorldSettings > AWorldSettings

   * Game Instance
      * B_LyraGameInstance > LyraGameInstance > UCommonGameInstance > UGameInstance 

   * LyraLocalPlayer: Stay active across maps
      * UCommonLocalPlayer > ULocalPlayer > UPlayer
      * ILyraTeamAgentInterface > IGenericTeamAgentInterface

   * GameUser Settings Class:
      * ULyraSettingsLocal > UGameUserSettings > UObject

   * Default Input Component Class
      * ULyraInputComponent > UEnhancedInputComponent
   
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
         * In the ``L_LyraFrontEnd`` case this is ``B_LyraFrontEndExperience``
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
               * **ILoadingProcessInterface**
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

* ``Game/Environments/B_LoadRandomLobbyBackground.uasset``
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
         * In the ``L_Expanse`` case this is ``B_ShooterGame_Elimination``
      * ``TryDedicatedServerLogin``
         * This only gets triggered if the experience is not valid
           It then loads ``B_LyraDefaultExperience`` as fall back.
      * ``OnMatchAssignmentGiven(ExperienceId, ExperienceIdSource)``
         * GameState::ULyraExperienceManagerComponent->SetCurrentExperience **ILoadingProcessInterface**
            * Add Feature ShooterCore (``LyraStarterGame/Plugins/GameFeatures/ShooterCore/Content/ShooterCore.uasset``)
               * Add Components:
                  * Add component B_EliminationFeedRelay to GameStateBase (Client & Server)
                     * B_EliminationFeedRelay > UGameplayMessageProcessor
                  * Add component LyraEquipmentManagerComponent to LyraCharacter (Client & Server)
                     * ULyraEquipmentManagerComponent > UPawnComponent > UGameFrameworkComponent
                  * Add component LyraIndicatorManagerComponent to LyraCharacter (Client only)
                     * ULyraIndicatorManagerComponent > UControllerComponent > UGameFrameworkComponent
                  * Add component B_HandleShooterReplays to LyraPlayerController (Client Only)
                     * B_HandleShooterReplays > UControllerComponent
                  * Add component LyraInventoryManagementComponent to Controller (Client & Server)
                     * ULyraInventoryManagerComponent > UActorComponent
                  * Add component LyraWeaponStateComponent to Controller (Client & Server)
                     * LyraWeaponStateComponent > UControllerComponent > UGameFrameworkComponent
                  * Add component B_AimAssistTargetManager to LyraGameState (Client Only)
                     * B_AimAssistTargetManager > UAimAssistTargetManagerComponent > UGameStateComponent
               * Registry Data to preload
               * Add Gameplay Cue Path
                  * GameplayCues
                  * Weapons
                  * Items
               * Add Input Mapping
                  * IMC_Default (Move, WeaponFire, Jump, Crouch, Reload, Dash, AutoRun, Mouse)
                  * IMC_ShooterGame (Show Scoreboard, ADS, Greante, Emote, Quickslots, Melee, QuickSlot Cycle)
               * Asset Manager
                  * Lyra Experience Definition
                  * Lyra UserFacing Experience Definition 
                  * LyraExperience Action Set 
                  * Map 
                  * PlayerMappableInputConfig
            * Default Pawn Data
               * Pawn Class
               * Abilities
                  * Ability Set
                     * Granted Ability 
                        * GA_Hero_Jump, level 1, InputTag.Jump
                        * GA_Hero_Death, level 1, None
                        * GA_Hero_Dash, level 1, InputTag,Ability.Dash
                        * GA_Emote, Level 1, InputTag.Ability.Emote
                        * GA_QuickbarSlots, Level1 , InputTag.Ability.Quickslot
                        * GA_ADS, Level 1, InputTag.Weapon.ADS
                        * GA_Grenade, Level 1, InputTag.Weapon.Grenade
                        * GA_DropWeapon, Level 1, InputTag.Ability.Quickslot.Drop
                        * GA_Melee, Level 1, InputTag.Ability.Melee
                        * GA_SpawnEffect, Level 1, None
                        * LyraGameplayAbility_Reset, 1, None
                     * Granted GameplayEffect
                        * GE_IsPlayer, Effect Level 1
                     * Attribute Sets, None
               * Tag Relationship Mapping (FLyraAbilityTagRelationship)
                  * This is an extension to the ASC, it moves the requirement tags out of the GameplayAbility
                     * ULyraAbilitySystemComponent::SetTagRelationshipMapping(ULyraAbilityTagRelationshipMapping* NewMapping)
                     * TagRelationshipMapping->GetAbilityTagsToBlockAndCancel(AbilityTags, &ModifiedBlockTags, &ModifiedCancelTags);
                  * Tag => (*Containers)
                  * Ability.Type.Action => Blocked by Dead or Dying
                  * Ability.Type.Action.WeaponFire
                     * Block Reload & Emote
                     * Cancel Reload & Emote
                  * Ability.Type.Action.Melee
                     * Block emote, reload, weapon fire
                     * cancel emote, reload
                  * Ability.Type.Action.Dash
                     * Block Ability.Type.Action
                     * Cancel Ability.Type.Action
                  * Ability.Type.Emote
                     * Blocks Movement.Mode.Falling
               * Input Configuration  (ULyraInputConfig)
                  * Called in ``ULyraHeroComponent::InitializePlayerInput``
                     * ULyraInputComponent::AddInputMappings(InputConfig, Subsystem)
                     * LyraIC->BindAbilityActions(InputConfig, this, &ThisClass::Input_AbilityInputTagPressed, &ThisClass::Input_AbilityInputTagReleased, /*out*/ BindHandles);
                     * LyraIC->BindNativeAction(InputConfig, LyraGameplayTags::InputTag_Move, ETriggerEvent::Triggered, this, &ThisClass::Input_Move, /*bLogIfNotFound=*/ false);
                  * Native Input Actions
                     * Input Action IA_Move => InputTag.Move
                     * Input Action IA_LookMouse => InputTag.Look.Mouse
                     * Input Action IA_Look_Stick => InputTag.Look.Stick
                     * Input Action IA_Crouch => InputTag.Crouch
                     * Input Action IA_AutoRun => InputTag.AutoRun
                  * Ability Input Actions
                     * Input Action IA_Jump => InputTag.Jump
                     * Input Action IA_Weapon_Reload => InputTag.Weapon.Realod
                     * Input Action IA_Ability_Heal => InputTag.Ability.Heal
                     * Input Action IA_Ability_Dash => InputTag.Ability.Dash
                     * Input Action IA_Weapon_Fire => InputTag.Weapon.Fire
                     * Input Action IA_Weapon_Fire_Auto => InputTag.Weapon.FireAuto
               * Camera Mode
                  * ULyraCameraMode_ThirdPerson >  ULyraCameraMode > UObject
                  * ULyraCameraMode_TopDownArenaCamera > ULyraCameraMode
                  * ULyraCameraComponent > UCameraComponent
                     * Has a new attribute ULyraCameraModeStack that can push/pop camera modes
            * Action Sets: ULyraExperienceActionSet
               * LAS_ShooterGame_SharedInput
                  * Add Input BindHandles
                     * Input Configs -> InputData_ShooterGame_Addons
                        * IA_ShowScoreboard => InputTag.Ability.ShowLeaderboard
                        * IA_ADS => InputTag.Ability.ADS
                        * IA_Grenade => InputTag.Ability.Grenade 
                        * IA_Emote => InputTag.Ability.Emote 
                        * IA_DropWeapon => InputTag.Ability.QuickSlot.Drop
                        * IA_Melee => InputTag.Ability.Melee
                  * Add Input Mapping (already done by ShooterCore)
                     * IMC_Default
                     * IMC_ShooterGame
                  * Enable ShooterCore Feature (Already good, ignored)
               * LAS_ShooterGame_StandardComponents
                  * Add Component B_NiagaraNumberPopComponent to LyraPlayerController (client)
                     * B_NiagaraNumberPopComponent > ULyraNumberPopComponent_NiagaraText > ULyraNumberPopComponent > UControllerComponent > UGameFrameworkComponent
                  * Add component B_QuickBarComponent to Controller (Client & Server)
                     * B_QuickBarComponent > ULyraQuickBarComponent > UControllerComponent > UGameFrameworkComponent
                  * Add component NameplateManagerComponent to Controller (Client)
                     * Manage a widget that will show the player name
                     * NameplateManagerComponent > UControllerComponent
                     * UIndicatorDescriptor
                     * Listen For Gameplay Messages
                        * Gameplay.Message.Nameplace.Add
                        * Gameplay.Message.Nameplace.Remove
                  * Add component NameplaceSource to B_Hero_ShooterMannequin  (Client)
                     * B_Hero_ShooterMannequin > B_Hero_Default > Character Default > Lyra Character
                     * NameplaceSource > UControllerComponent
                        * Broadcast Message: Gameplay.Message.Nameplate.Add
                  * Enable ShooterCore Feature (Already good, ignored)
               * LAS_ShooterGame_StandardHUD
                  * Add Widgets
                     * Layout: UI.Layer.Game => W_ShooterHUDLayout
                        * W_ShooterHUDLayout > ULyraHUDLayout > ULyraActivatableWidget > UCommonActivatableWidget > UCommonUserWidget > UUserWidget
                     * Widgets
                        * HUD.Slot.EliminationFeed => W_EliminationFeed
                           * Listen for GameplayMessage: Lyra.AddNotification.KillFeed
                        * HUD.Slot.Equipment => W_QuickBar
                        * HUD.Slot.TopAccolades => W_AccoladeHostWidget
                        * HUD.Slot.Reticle => W_WeaponReticleHost
                        * HUD.Slot.PerfStats.Graph => W_PerfStatContainer_GraphOnly
                        * HUD.Slot.PerfStats.Text => W_PerfStatContainer_TextOnly
                        * HUD.Slot.LeftSideTouchInputs => W_OnScreenJoystick_Left
                        * HUD.Slot.RightSizeTouchInputs => W_OnScreenJoystick_Right
                        * HUD.Slot.RightSizeTouchInputs => W_FireButton
                        * HUD.Slot.RightSideTouchRegion => W_TouchRegion_Right
                        * HUD.Slot.LeftSideTouchRegion => W_TouchRegion_Left
                  * Enable ShooterCore Feature (Already good, ignored)
               * EAS_BasicShooterAcolades
                  * Add component B_ElimChainProcessor to GameStateBase (Server only)
                     * B_ElimChainProcessor > UElimChainProcessor > UGameplayMessageProcessor
                  * Add component B_ElimStreakProcessor to GameStateBase (Server only)
                     * B_ElimStreakProcessor > UElimStreakProcessor > UGameplayMessageProcessor
                  * Add component AssistProcessor to GameState (Server only)
                     * UAssistProcessor > UGameplayMessageProcessor
                  * Add component B_AccoladeRelay to GameState (Server 7 Client)
                     * B_AccoladeRelay > UGameplayMessageProcessor
            * Actions
               * Add Abilities
                  * Add ability LyraPlayerState
                     * GA_ShowLeaderBoard_TDM, Level 1, InputTag.Ability.ShowLeaderboard
                     * GA_AutoRespawn
               * Add Components
                  * Add component B_TeamDeathMatchScoring to LyraGameState (Client & Server)
                     * B_TeamDeathMatchScoring > B_ShooterGameScoring_Base > UGameStateComponent
                  * Add component B_MusicManagerComponent_Elimination to LyraGameState (Client)
                     * B_MusicManagerComponent_Elimination > B_MusicManagerComponent_Base > UActorComponent
                  * Add component B_ShooterBotSpawner to LyraGameState (Server)
                     * B_ShooterBotSpawner > ULyraBotCreationComponent > UGameStateComponent
                  * add component B_TeamSetup_TwoTeams to LyraGameState (Server)
                     * B_TeamSetup_TwoTeams > ULyraTeamCreationComponent > UGameStateComponent
                  * add component B_TeamSpawningRules to LyraGameState (Server)
                     * B_TeamSpawningRules > UTDM_PlayerSpawningManagmentComponent > ULyraPlayerSpawningManagerComponent > UGameStateComponent
                  * Add component B_PickRandomCharacter to Controller (Server)
                     * B_PickRandomCharacter > ULyraControllerComponent_CharacterParts > UControllerComponent
               * Add Widget
                  * HUD.Slot.TeamScore => W_ScoreWidget_Elimination
         * OnExperienceLoaded_HighPriority.Broadcast(CurrentExperience);
         * OnExperienceLoaded.Broadcast(CurrentExperience);
         * OnExperienceLoaded_LowPriority.Broadcast(CurrentExperience);


Final State
-----------

* GameState: LyraGameState

* LocalPlayer

* Player Controller

* CharacterL B_Hero_ShooterMannequin
   * Components
      * Camera Component
      * Character Movement
      * Pawn Ext Component
      * Health Component
      * Lyra Hero
      * AIPerception StimuliSource
      * LyraContextEffect
      * PawnCosmeticsComponent
   * Attachments:
      * ALyraTaggedActor
      * B_Pistol > B_Weapon > Actor

* Player State



.. comment::

   Seamless travel

      * UGameMapsSettings::TransitionMap 
      * AGameModeBase::bUseSeamlessTravel  = true
      * AGameModeBase::GetSeamlessTravelActorList 
      * Actors that persist
         * GameMode (server)
         * PlayerController with PlayerState (server)



Cosmetics
---------

* B_MannesingPawnCosmectics > ULyraPawnComponent_CharacterParts
