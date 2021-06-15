# bmc.tso
BMC TrueSight Orchestrator
Basic TSO modules for Integration projects

## Core Workflows and purpose
- **w3rkstatt** base python functions for project support
- **w3rkstatt** encrypt the cleartext passwords

## Dependencies
- [ ] **Central Configuration Module**
- [ ] **TSO Adatpers**

## Supported Themes
- **IT Service Managament** Incident, Change, Worklog Integration
- **Event Managament** TrueSight Operations Manager, Kafka, 3rd party event managament systems
- **Network** Basic Network Functions
- **Microsoft** Interaction with the Microsoft Windows Platform
- **Service Deask Automation** End-To-End scenarios

Module Name prefix: Globa-DEM

## Base Modules
| Solution                  | API           | Worklfow      |
| :-------------            | :---:         | :---:         | 
| Configurations            | ⬜            | ⬜    | 
| Shared                    | ✅            | ✅    | 


## Solutions leveraging the base modules
| Solution                  | API           | Worklfow      |
| :-------------            | :---:         | :---:         | 
| BMC Control-M             | ✅            | 🔶    | 
| BMC Helix ITSM            | ✅            | ✅    | 
| BMC TrueSight             | ✅            | ✅    | 
| ServiceNOW                | ✅            | 🚧    | 


* ✅ — Supported
* 🔶 — Partial support
* 🚧 — Under development
* ⬜ - N/A ️

**ToDO**: 
- [x] Initial Core Configuration
- [ ] Donwlod *.roar file, import into DevStudio
- [ ] create TSO adapter, update module config
- [ ] adjust module config to match your environment
- [ ] utilize workflows for education purposes
- [ ] build custom content for your environment
