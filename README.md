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


## TSO Adapters
Default Names and location. Create your own location and setup, or utilize the following types.
The "share" modules contains help workflows to get module and adapter configurations in order to simplify product usage.

* Wokflow: 'Global-DEM-Shared:Configs:Get Adapter Name'
* Input: location, type
* Output: adapter name
* XPath: //adapter[@type="${type}"][@location="${location}"]/text()

```bash
<adapters>
  <adapter location="lab" type="csv">Base CSV File Adapter</adapter>
  <adapter location="lab" type="cmd">Base CmdLine Adapter</adapter>
  <adapter location="lab" type="file">Base File Adapter</adapter>
  <adapter location="lab" type="http">Base HTTP Adapter</adapter>
  <adapter location="lab" type="rest">Base REST Adapter</adapter>
  <adapter location="lab" type="powershell">Base PowerShell Adapter</adapter>
  <adapter location="lab" type="sccm">Expert SCCM Adapter</adapter>
  <adapter location="lab" type="smtp">Base SMTP Adapter</adapter>
  <adapter location="lab" type="sql">Base SQL Adapter</adapter>
  <adapter location="lab" type="ssh">Base SSH Adapter</adapter>
  <adapter location="lab" type="soap">Base WebServices Adapter</adapter>
  <adapter location="lab" type="wincmd">Base WinCmdLine Adapter</adapter>
  <adapter location="lab" type="tssa">Expert TSSA Adapter</adapter>
  <adapter location="lab" type="bppm">Expert TSIM Adapter</adapter>
  <adapter location="lab" type="ars">Expert ITSM Adapter</adapter>
  <adapter location="lab" type="atrium">Expert CMDB Adapter</adapter>
  <adapter location="lab" type="msad">Expert Active Directory</adapter>
  <adapter location="lab" type="vmware">Expert vSphere Adapter</adapter>
  <adapter location="lab" type="vdbsql">Value Dashboard SQL Adapter</adapter>
  <adapter location="lab" type="kafka">Expert Kafka Adapter</adapter>
  <adapter location="lab" type="adcli">Expert CmdLine Adapter</adapter>
  <adapter location="azure" type="file">Azure File Adapter</adapter>
  <adapter location="jira" type="http">Jira HTTP Adapter</adapter>
  <adapter location="gmail" type="smtp">Base SMTP GMail Adapter</adapter>
</adapters>
```
