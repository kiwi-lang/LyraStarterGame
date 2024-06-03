Replication Graph
=================


* UReplicationGraph: Top level driver
   * Route Actors to their Replication Node
      * ``RouteAddNetworkActorToNodes``
         * ``UReplicationGraphNode::NotifyAddNetworkActor``
      * ``RouteRemoveNetworkActorToNodes``
         * ``UReplicationGraphNode::NotifyRemoveNetworkActor``


* ``UReplicationGraphNode::GatherActorListsForConnection``: gets called on every replication tick
   * It procudes a list of actors that should replicate for a given connection


The speedup actor replication, one should create groups of actors in such a way that
the viewer can know quickly if the actors are relevant or not.


* UReplicationGraphNode_GridSpatialization2D
   * Replicates actors that are close to the viewer
* UReplicationGraphNode_ActorList
   * Always replicate the actors
* ULyraReplicationGraphNode_PlayerStateFrequencyLimiter
   * This replicates a small rolling set of player states (currently 2/frame).
* ULyraReplicationGraphNode_AlwaysRelevant_ForConnection
   * Set of actors that only replicates to a specific connection

.. code-block:: cpp

   int32 UReplicationGraph::ServerReplicateActors(float DeltaSeconds) {

      for (UNetReplicationGraphConnection* ConnectionManager: Connections) {

         FNetViewerArray ConnectionViewers;
         UNetConnection* const NetConnection = ConnectionManager->NetConnection;
         APlayerController* const PC = NetConnection->PlayerController;
         FPerConnectionActorInfoMap& ConnectionActorInfoMap = ConnectionManager->ActorInfoMap;

         const bool bIsSelectedForHeavyComputation =
            HeavyComputationConnectionSelector == ConnectionManager->ConnectionOrderNum
            || CVar_RepGraph_ConnectionHeavyComputationAmortization == 0;

         FGatheredReplicationActorLists GatheredReplicationListsForConnection;
         const FConnectionGatherActorListParameters Parameters(
            ConnectionViewers,
            *ConnectionManager,
            ConnectionManager->GetCachedClientVisibleLevelNames(),
            FrameNum,
            GatheredReplicationListsForConnection,
            bIsSelectedForHeavyComputation);

         
			for (UReplicationGraphNode* Node : GlobalGraphNodes)
			{
				Node->GatherActorListsForConnection(Parameters);
			}

			for (UReplicationGraphNode* Node : ConnectionManager->ConnectionGraphNodes)
			{
				Node->GatherActorListsForConnection(Parameters);
			}

			ConnectionManager->UpdateGatherLocationsForConnection(ConnectionViewers, DestructionSettings);

         ReplicateActorListsForConnections_Default(ConnectionManager, GatheredReplicationListsForConnection, ConnectionViewers);
         ReplicateActorListsForConnections_FastShared(ConnectionManager, GatheredReplicationListsForConnection, ConnectionViewers);