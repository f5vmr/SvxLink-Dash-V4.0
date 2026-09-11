# SvxLink-Dash V4.0

SvxLink-Dash V4.0 is a Flask-based configuration and runtime dashboard for SvxLink 26.05.1.

It provides a guided environment for configuring, building and operating simplex, repeater and multi-port SvxLink installations. It is suitable for independently operated nodes and is not restricted to a particular reflector network, region or deployment model.

SvxLink 26.05.1 is developed by Tobias Blömberg, SM0SVX.

## Principal features

- Guided SvxLink configuration
- Single-port and multi-port installations
- SimplexLogic and RepeaterLogic configuration
- Local port-to-port links
- SvxReflector connection and authentication
- Federation-family and independent reflector routes
- EchoLink and METAR module configuration
- GPIO, serial, HIDRAW and audio-interface configuration
- Installation-wide courtesy, idle and closedown tones
- Public node information and optional LocationInfo generation
- Configuration review before deployment
- Managed configuration deployment and SvxLink restart
- Protected runtime configuration editing
- Live service, radio and reflector status
- Talkgroup monitoring and DTMF control
- Local RF CTCSS talkgroup selection
- Hardware and system telemetry
- Live SvxLink log viewing

## Intended installations

SvxLink-Dash V4.0 is intended for:

- New or existing SvxLink operators who require guided configuration.
- Appliance-style installations using Raspberry Pi or NanoPi Neo hardware.
- Generic Debian-based Linux computers running SvxLink.
- Single-channel radio interfaces.
- Independent dual-USB radio interfaces.
- Supported ICS-CTRLS 1X, 2X, 4X and 8X hardware.

The dashboard is currently presented in English.

## Configuration builder

The guided workflow covers:

- Platform and hardware selection
- Radio-port selection
- Simplex and repeater roles
- Audio and control interfaces
- Squelch detection
- Identification and CW
- Courtesy, idle and closedown tones
- Repeater operating settings
- SvxReflector access
- Local and reflector-link topology
- EchoLink and METAR modules
- Node information
- Final configuration review and deployment

## Runtime dashboard

The runtime dashboard provides:

- SvxLink service status
- Reflector connection state
- Radio and squelch status
- Active and monitored talkgroups
- EchoLink activity
- Reflector activity
- DTMF talkgroup controls
- Manual DTMF command entry
- Host and operating-system information
- CPU temperature where available
- Memory and disk utilisation
- Live SvxLink log output

## Protected editing

Authenticated runtime pages allow authorised operators to update supported settings without repeating the initial setup workflow.

Protected facilities include:

- Talkgroup controls
- Monitoring talkgroups
- Local RF CTCSS talkgroup mappings
- EchoLink configuration
- METAR configuration
- Macro configuration
- Node information
- Live log viewing
- Guided reconfiguration

Saved changes are presented for review before the managed configuration is rebuilt and deployed.

## Supported platforms

The configuration model recognises:

- Raspberry Pi
- NanoPi Neo
- Generic Linux server

Runtime architecture reporting recognises:

- 32-bit ARM (`armhf`)
- 64-bit ARM (`arm64`)
- 64-bit x86 (`amd64`)

The dashboard is intended for Debian-based operating systems on which SvxLink 26.05.1 is already installed and operational.

Platform recognition and hardware-profile support are separate. Not every hardware profile is appropriate for every platform.

## Hardware profiles

Available hardware profiles include:

- Generic Single Channel
- Dual USB Sound Fob Interfaces
- ICS-CTRLS 1X
- ICS-CTRLS 2X
- ICS-CTRLS 4X
- ICS-CTRLS 8X

Some hardware profiles require additional preparation, device-tree overlays, ALSA configuration or a system reboot. The guided workflow identifies those requirements when the profile is selected.
## Installation

### Prerequisites

Before installing SvxLink-Dash V4.0, confirm that:

* SvxLink 26.05.1 is installed and operational.
* `svxlink.service` is available.
* The `svxlink` user and group exist.
* `/etc/svxlink` is present.
* The computer is connected to the local network.
* You have local administrative access through `sudo`.

SvxLink-Dash configures and operates an existing SvxLink installation. It does not install SvxLink itself.

### Download and run the installer

Clone the repository into a temporary directory and run the executable installer:

```bash
cd /tmp

git clone \
https://github.com/f5vmr/SvxLink-Dash-V4.0.git

cd SvxLink-Dash-V4.0

sudo ./install/install-dashboard.sh
```

The installer places the operational dashboard in:

```text
/opt/dashboard
```

Dashboard runtime data and managed backups are stored beneath:

```text
/var/lib/svxlink-dash
```

The dashboard service runs as:

```text
svxlink:svxlink
```

### Confirm the installation

Check that the dashboard service is running:

```bash
sudo systemctl status \
svxlink-dash.service \
--no-pager
```

The service should report:

```text
active (running)
```

### First access

Open the dashboard from a browser on the same network:

```text
http://<dashboard-hostname-or-address>:5000/
```

Where local hostname resolution is available, the default hostname may be used:

```text
http://svxlink.local:5000/
```

The initial workflow collects the dashboard credentials and guides the operator through the installation configuration.

## Authentication

Runtime monitoring is publicly accessible on the local network. Configuration and management functions require dashboard authentication.

Protected facilities include:

* Talkgroup controls
* Monitoring talkgroups
* Local RF CTCSS talkgroup mappings
* EchoLink configuration
* METAR configuration
* Macro configuration
* Node information
* Guided reconfiguration
* Live log viewing

Dashboard credentials are created during the initial setup workflow.

### Forgotten credentials

Dashboard credentials can be reset from the Linux console:

```bash
sudo /opt/dashboard/tools/reset_dashboard_auth.py
```

After resetting the credentials, follow the command’s displayed instructions and sign in again.

## Service management

The installer creates and enables:

```text
svxlink-dash.service
```

The dashboard runs as the `svxlink` user so that it can access dashboard-managed configuration, runtime controls and SvxLink operational information.

### View dashboard status

```bash
sudo systemctl status \
svxlink-dash.service \
--no-pager
```

### Restart the dashboard

```bash
sudo systemctl restart \
svxlink-dash.service
```

### View dashboard service messages

```bash
sudo journalctl \
-u svxlink-dash.service \
-n 100 \
--no-pager
```

### Restart SvxLink

```bash
sudo systemctl restart \
svxlink.service
```

## SvxLink log detection

The dashboard automatically locates the configured SvxLink log.

It first checks the `LOGFILE` setting in:

```text
/etc/default/svxlink
```

It can also recognise the standard locations:

```text
/var/log/svxlink.log
/var/log/svxlink
```

The protected live-log page displays the detected log output.

## Default manual DTMF commands

The runtime dashboard can send DTMF commands through the configured SvxLink control FIFO.

### Talkgroup selection

Prefix the talkgroup number with `91` and terminate the command with `#`.

Example for talkgroup 235:

```text
91235#
```

### EchoLink

Open the default EchoLink module:

```text
2#
```

Enter the required EchoLink node number followed by `#`:

```text
<node-number>#
```

Exit the EchoLink module:

```text
##
```

### METAR

Open the default METAR module:

```text
5#
```

Select a configured airport entry:

```text
1#
```

Exit the METAR module:

```text
#
```

Module identifiers and macros may differ when the operator changes the generated configuration.

## Troubleshooting

### Dashboard does not start

Check the service status:

```bash
sudo systemctl status \
svxlink-dash.service \
--no-pager
```

View its recent service messages:

```bash
sudo journalctl \
-u svxlink-dash.service \
-n 100 \
--no-pager
```

### Dashboard page does not open

Confirm that `svxlink-dash.service` is active and use the Linux computer’s current IP address:

```bash
hostname -I
```

Open the first reported address on port 5000:

```text
http://<ip-address>:5000/
```

### Live log viewer has no output

Check the configured SvxLink log path:

```bash
grep '^LOGFILE=' \
/etc/default/svxlink
```

If `/var/log/svxlink.log` is in use, inspect it directly:

```bash
tail -f \
/var/log/svxlink.log
```

### DTMF controls do not work

Confirm that the appropriate SvxLink DTMF control FIFO exists:

```text
/dev/shm/simplex_dtmf_ctrl
/dev/shm/repeater_dtmf_ctrl
```

The required FIFO depends on the configured radio logic. It must be writable by the `svxlink` user.

Also confirm that SvxLink is active:

```bash
sudo systemctl status \
svxlink.service \
--no-pager
```


## Guided configuration sequence

The configuration workflow establishes the available hardware, configures every enabled radio port and identifies the primary installation identity before creating any local or reflector links.

The normal sequence is:

1. Select the hardware platform.
2. Select the hardware profile and enable the required radio ports.
3. Assign each enabled port as `SimplexLogic` or `RepeaterLogic`.
4. Configure the node, interface, squelch, identification and CW settings for each enabled port.
5. Select the installation-wide courtesy, idle and closedown tones.
6. Complete the repeater settings for any repeater ports.
7. Select the primary installation port. A single-port installation selects its only port automatically.
8. Select whether the installation will use a reflector.
9. Configure the reflector route and authentication method when required.
10. Assign every enabled port to independent operation, a local link or the reflector link.
11. Validate and review the complete configuration.
12. Build and deploy the generated SvxLink configuration.

The reflector route follows primary-port selection so that `ReflectorLogic` uses the correct installation callsign. This is especially important for Protocol 3, where the callsign forms part of the certificate identity.

Link topology is configured after the available ports, their logic types and the reflector route are known.

## Primary installation identity

Every multi-port installation has one selected primary port.

The callsign assigned to that port becomes the primary callsign of the installation. Port number and configuration order do not override the selected primary identity.

The primary callsign is used where one callsign must represent the complete installation, including:

* `ReflectorLogic`
* Node information
* Dashboard installation identification
* The system login display or MOTD

A single-port installation automatically uses the callsign of its only configured radio logic.

When reflector operation is enabled:

* The primary port is included in the reflector link.
* `ReflectorLogic` uses the primary installation callsign.
* Additional ports may participate in the same reflector link.
* Additional ports may use the same or different callsigns.
* A secondary port never replaces the selected primary identity merely because it has a lower port number or was configured first.

For example:

```text
Port 1 — RepeaterLogic — AK6BL — Primary
Port 2 — SimplexLogic — KO6IL-L
```

Both ports may participate in the reflector link:

```ini
[LinkToReflector]
CONNECT_LOGICS=RepeaterLogic1:9,SimplexLogic2:9,ReflectorLogic
DEFAULT_ACTIVE=1
TIMEOUT=300
```

The reflector identity remains:

```ini
[ReflectorLogic]
CALLSIGN=AK6BL
```

For Protocol 3 operation, the `ReflectorLogic` callsign determines the X.509 client-certificate identity. Changing the primary callsign may therefore require a new certificate request and approval by the reflector administrator.

When reflector operation is disabled, the primary port may remain independent or participate in a local link. It continues to provide the installation identity.

## Installation-wide tone settings

Courtesy, idle and closedown tones are shared installation settings. They are not configured independently for each port because SvxLink produces them through common event-handling files.

The available settings are:

* Courtesy tone
* Courtesy beep frequency
* Repeater idle tone
* Repeater closedown tone

Courtesy behaviour is applied through the shared `Logic.tcl` event handling.

Idle and closedown behaviour is applied through the shared `RepeaterLogicType.tcl` event handling and affects every configured repeater logic.

Courtesy choices are:

* None
* Beep
* Morse T
* Morse K

Repeater idle-tone choices are:

* None
* Pip
* Chime

Repeater closedown-tone choices are:

* None
* Biboop
* VA

`None` is a valid deliberate selection in every case. A courtesy tone is commonly used for repeater operation, but it is not mandatory.

The dashboard applies each shared event-file customisation once, regardless of the number of configured radio ports.

## Logic and link topology

SvxLink-Dash supports single-port and multi-port installations containing `SimplexLogic`, `RepeaterLogic` and, when selected, `ReflectorLogic`.

Every enabled port has its own radio logic. The topology determines whether that logic operates independently or participates in a local or reflector link.

### Logic declaration

Every configured logic is declared in the `[GLOBAL]` section of the generated `svxlink.conf`.

Example:

```ini
[GLOBAL]
LOGICS=SimplexLogic1,RepeaterLogic2,SimplexLogic3,SimplexLogic4,ReflectorLogic
LINKS=LinkToReflector,LocalLink1
```

`LOGICS` determines which logic instances SvxLink creates.

`LINKS` identifies the link sections that join selected logic instances. Declaring a logic does not automatically connect it to another logic.

### Link membership

A link section uses `CONNECT_LOGICS` to define its exact membership.

Example reflector link:

```ini
[LinkToReflector]
CONNECT_LOGICS=SimplexLogic1:9,RepeaterLogic2:9,ReflectorLogic
DEFAULT_ACTIVE=1
TIMEOUT=300
```

In this example:

* `SimplexLogic1` participates in the reflector link.
* `RepeaterLogic2` participates in the reflector link.
* The `:9` suffix allows DTMF reflector talkgroup control.
* Other declared radio logics remain outside this link.

A declared radio logic that is not included in a link remains independently operational.

## Single-port topology

A single-port installation does not require a separate topology-selection page.

Without reflector access, its `SimplexLogic` or `RepeaterLogic` operates independently.

When reflector access is enabled, the radio logic is linked automatically to `ReflectorLogic`.

Example:

```ini
[LinkToReflector]
CONNECT_LOGICS=SimplexLogic:9,ReflectorLogic
DEFAULT_ACTIVE=1
TIMEOUT=300
```

## Multi-port topology

Every enabled port in a multi-port installation is assigned to one of these dispositions:

* Independent operation
* A named local link
* The reflector link

A local link joins two or more radio ports.

A reflector link joins one or more selected radio ports to the installation’s single `ReflectorLogic`.

For example:

```text
Ports 1 and 2 — Reflector link
Ports 3 and 4 — Local link
Ports 5, 6, 7 and 8 — Independent
```

Ports 1 and 2 share the same reflector connection and reflector talkgroup state. Ports 3 and 4 communicate through their separate local link. Ports 5 to 8 remain operational without participating in either link.

Example local link:

```ini
[LocalLink1]
CONNECT_LOGICS=SimplexLogic3,RepeaterLogic4
DEFAULT_ACTIVE=1
TIMEOUT=300
```

The operator selects the required connectivity. The dashboard generates the appropriate logic names and validates the resulting topology before configuration can be built.

## Strict port-membership rule

A radio port may belong to no more than one link.

For example, this arrangement is invalid:

```ini
[LinkToReflector]
CONNECT_LOGICS=RepeaterLogic1:9,SimplexLogic2:9,ReflectorLogic

[LocalLink1]
CONNECT_LOGICS=SimplexLogic2,RepeaterLogic3
```

`SimplexLogic2` appears in both links. That overlap would unintentionally connect the local group to the reflector group.

A port already assigned to one link must be removed from that link before it can be assigned elsewhere.

## Topology validation

Before the configuration can be built, the dashboard verifies that:

* Every enabled port has a completed radio-logic configuration.
* Every enabled port has an explicit topology disposition.
* Every link member refers to an enabled radio port or `ReflectorLogic`.
* Every local link contains at least two radio ports.
* The reflector link contains at least one radio port and `ReflectorLogic`.
* No radio port appears in more than one link.
* `ReflectorLogic` appears only in the reflector link.
* Every radio logic connected to `ReflectorLogic` receives the required `:9` suffix.
* A reflector link is not created when reflector operation is disabled.
* No more than one `ReflectorLogic` and one reflector destination are configured.

The final review identifies every enabled port as:

* Connected to the reflector
* Connected through a named local link
* Independent

## Incomplete and disabled ports

An incomplete port cannot be used to build the final configuration. The dashboard identifies its missing configuration and returns the operator to the required setup stage.

A port that was not enabled during hardware selection cannot be assigned to a link. It must first be enabled and configured through the hardware workflow because additional audio devices, GPIO preparation or device-tree changes may be required.

## Independent ports

An independent port has a valid `SimplexLogic` or `RepeaterLogic` declaration but does not appear in a link section.

It remains locally operational and retains its own radio, squelch, identification and logic settings.

Independent operation is useful when one computer supports several unrelated radio systems that do not need to exchange audio or signalling.

## Reflector topology limit

One installation supports no more than one `ReflectorLogic` and one reflector destination.

Multiple radio ports may share that reflector connection, subject to the strict port-membership rule.

Other enabled ports may operate independently or form separate local groups. Simultaneous connections to multiple independent reflectors are outside the supported configuration scope.

## Reconfiguration behaviour

Initial setup follows the complete guided sequence:

```text
Configure the installation
→ Configure reflector access and topology
→ Review
→ Build and deploy
```

When an existing setting is opened from the protected reconfiguration menu, saving it returns directly to the Build page:

```text
Runtime dashboard
→ Reconfiguration
→ Selected configuration page
→ Build
→ Deploy
```

The operator is not sent through unrelated initial-setup pages. The Build page remains the common point for reviewing, rendering and deploying the revised configuration.

## Rebuild warning

The dashboard manages generated SvxLink configuration and event files.

A Rebuild can overwrite manual changes made directly to managed files. Before rebuilding, review the proposed configuration and preserve any manual work that must remain outside dashboard management.

Specialist configuration that is not guided by the dashboard should be maintained only in documented, manually managed sections or files.

## Reflector configuration and security

SvxLink-Dash V4.0 supports four distinct reflector routes:

* No reflector
* Federation Family reflector using Protocol 2
* Independent reflector using Protocol 2
* Reflector using Protocol 3 and X.509 certificates

Before configuring reflector access, confirm the required connection and authentication method with the destination reflector administrator.

## No reflector

The installation operates without `ReflectorLogic`.

A single-port radio logic remains independently operational. Multi-port installations may contain independent ports and local port-to-port links.

No reflector connection, authentication or talkgroup-routing configuration is generated.

## Federation Family reflector

The Federation Family comprises:

* UK-Wide
* North America
* Australia
* YorkshireNet

The dashboard supplies the predefined connection information for the selected reflector, including its hostname, port, website and suggested monitoring talkgroups.

Federation Family access uses SvxReflector Protocol 2 callsign-and-password authentication.

The operator must enter the network password issued for the node callsign. This password must contain exactly 16 characters.

The 16-character requirement applies specifically to the Federation Family route. It is not a general Protocol 2 requirement.

## Independent Protocol 2 reflector

An independently operated Protocol 2 reflector uses connection information supplied by its administrator.

The operator must obtain:

* Reflector name
* Hostname or IP address
* Port number
* Authentication password
* Any recommended default or monitoring talkgroups

The password is rendered as the `AUTH_KEY` in `ReflectorLogic`.

The dashboard accepts the password specified by the reflector administrator. It does not apply the Federation Family’s 16-character password rule to an independent Protocol 2 reflector.

Protocol 2 uses a shared authentication password. It does not use the Protocol 3 certificate-request and approval process.

## Protocol 3 reflector

Protocol 3 uses X.509 client-certificate authentication rather than a shared reflector password.

The operator must obtain:

* Reflector name
* Hostname or IP address
* Port number
* Any identity information required by the reflector administrator
* Any recommended default or monitoring talkgroups

The dashboard generates the required `ReflectorLogic` certificate settings using the primary installation callsign.

SvxLink then performs the client-certificate process:

1. Create the client private key.
2. Create a Certificate Signing Request.
3. Obtain the reflector’s CA bundle.
4. Submit the certificate request to the reflector.
5. Wait for approval by the reflector administrator.
6. Retrieve the signed client certificate.
7. Authenticate to the reflector using that certificate.

The private key must remain on the node and must not be shared.

The reflector administrator must inspect and approve the pending request before the node can complete certificate authentication.

Successful Protocol 3 operation also depends on the reflector having:

* A valid root, issuing and server certificate chain
* A CA bundle containing the active root certificate
* A server certificate covering the hostname or IP address used by the client
* A working certificate-request review and approval process

The hostname or IP address entered in the dashboard must match an identity contained in the reflector’s server certificate. A certificate issued for a DNS hostname will not validate when the node connects using an unrelated IP address.

The client dashboard cannot repair or bypass an incorrectly configured reflector certificate system.

### Certificate identity and reapproval

The primary installation callsign becomes the `ReflectorLogic` callsign and the Protocol 3 client-certificate identity.

Changing that callsign changes the node’s certificate identity. A deliberate primary-callsign change may therefore require:

* A new private key and Certificate Signing Request
* A new approval by the reflector administrator
* A new signed client certificate

Changing the primary installation identity should not be treated as an ordinary cosmetic change on a Protocol 3 installation.

## Common reflector behaviour

The reflector callsign is taken from the primary installation identity. It does not need to be entered again during routine reflector setup.

Standard certificate paths, filenames and safe connection defaults are generated automatically where applicable.

Default and monitoring talkgroups remain specific to the selected reflector and installation. They may be configured after the reflector connection has been established.

In a multi-port installation, the operator selects which enabled radio ports participate in the reflector link.

Each participating radio logic is added to `CONNECT_LOGICS` with the required `:9` DTMF control suffix.

A port assigned to the reflector link cannot also belong to a local port-to-port link.

SvxLink-Dash supports one `ReflectorLogic` and one reflector destination within an installation. Multiple selected radio ports may share that connection.

## Scope limitations

The initial SvxLink-Dash V4.0 release does not provide guided configuration for:

* Browser audio streaming
* Complete RemoteTrx deployment
* NetRx or NetTx deployment
* MultiRx or MultiTx specialist deployment
* Complete RTL-SDR installation and calibration
* LADSPA filter design
* Audio compressor design
* Automatic reflector-account approval
* Automatic Protocol 3 certificate approval
* External network validation beyond safe connection checks

Relevant upstream-compatible configuration sections may remain available for manual administration.

A dashboard Rebuild can overwrite manual changes made to dashboard-managed files. Preserve specialist configuration in documented manually managed sections or files.

## Credits

SvxLink 26.05.1 is developed by Tobias Blömberg, SM0SVX.

SvxLink-Dash V4.0 is developed by Chris Jackson, G4NAB.

Additional assistance with Python, Flask, configuration rendering, testing, debugging and documentation was provided through ChatGPT by OpenAI.

## Licence

SvxLink-Dash V4.0 is free software distributed under the GNU General Public License version 3.

You may use, modify and redistribute it under the terms contained in the repository’s [`LICENSE`](LICENSE) file.

SvxLink itself is developed and licensed separately by Tobias Blömberg, SM0SVX. Files derived from or supplied by SvxLink retain their original copyright and licensing terms.