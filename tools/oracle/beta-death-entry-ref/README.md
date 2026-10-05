# Death entry extraction — deferred harness

`extract_beta_death_entry.ps1` copies five original CanDie/Kill/waiting/IsActive
methods and checks exact IL after serialization. Ten dependency callbacks
replace getters, power setter and MarkAsWaitingToDie; their original bodies are
not executed. The source Assembly-CSharp is read as metadata only.

The extracted DLL is prepared; Program.cs/harness has not been written.
Do not run this project or infer executed death fixtures from the extraction.
Further oracle work was deferred when the user requested visible gameplay
development and fewer tests. Current preview lifecycle is in duelLiveCard.ws
and duelSession.ws and is not full original death/ExecutionStack acceptance.
