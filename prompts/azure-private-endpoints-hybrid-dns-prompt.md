# Build an Azure private endpoint and hybrid DNS learning lab

## Mission

Act as my Azure implementation engineer and lab instructor. Build a working,
reproducible lab in an Azure lab subscription and create **`lab-guide.md`**
that teaches me to implement and troubleshoot it through both **Infrastructure
as Code (IaC)** and the **Azure portal**.

This is an implementation request, not just a request for an architecture
proposal. Discover the environment, establish the constraints, create the
artifacts, obtain deployment approval, deploy the approved scope, exercise it,
and document the actual results. If blocked, preserve the completed work and
state exactly what permission, decision or capability is missing.

This prompt is self-contained. Do not assume access to the originating
conversation, its filesystem, PAI tooling, personal memory or transcripts.
Do not create unrelated wiki pages or expand into a full Azure landing zone.

## Learning context and scope

I want a realistic, bounded private-access/DNS lab while completing AZ-104
and AZ-305. I may pursue comprehensive AZ-700 knowledge later, but this lab
must not become a full AZ-700 implementation project.

The customer-style scenario is:

> A workload needs authenticated access to Azure Storage without using the
> storage service's public network endpoint. Azure clients and a corporate
> network must resolve the ordinary service hostname correctly. Azure
> workloads must also resolve names hosted by corporate DNS.

The source material consists of these three videos:

| Source | Teaching contribution |
| --- | --- |
| [John Savill: Private Endpoint DNS Exploration](https://www.youtube.com/watch?v=rXbamGNz-xQ) | Normal service hostname, CNAME chain, private versus public answers, Azure Private DNS versus custom DNS. Published November 24, 2021. |
| [Jeremy Wallace: Mastering Azure Private Endpoints: Configuration and DNS Setup Guide](https://www.youtube.com/watch?v=ABzp8uQajcU) | Private endpoint provisioning, Azure Files example, DNS integration and manually maintained AD DNS records. |
| [John Savill: Azure DNS Private Resolver Deep Dive](https://www.youtube.com/watch?v=V8ChsYAyxTc) | Inbound endpoints, outbound endpoints, forwarding rulesets, VNet links and hybrid DNS. Recorded during preview. |

If supplied, local files map as follows: `transcript.txt` is the Private
Resolver video; `transcript 2.txt` is Wallace; `transcript 3.txt` is DNS
Exploration. `transcript 4.txt`, if present, is a broader 2021 AZ-700 guide,
not the scope or current coverage authority for this lab.

Use current Microsoft documentation for deployable behavior, supported
configurations, API versions, sizing, pricing and portal procedures:

- https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns-integration
- https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-dns
- https://learn.microsoft.com/en-us/azure/private-link/tutorial-private-endpoint-storage-portal
- https://learn.microsoft.com/en-us/azure/dns/private-resolver-hybrid-dns
- https://learn.microsoft.com/en-us/azure/dns/private-resolver-endpoints-rulesets
- https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints
- https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/az-104
- https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/az-305
- https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/az-700

Resolve conflicts in favor of current official guidance and record material
differences from the videos. The videos are explanations, not specifications.

## Read-only discovery and deployment approval

Read the destination repository instructions and existing files first.
Preserve unrelated work. Inspect the authenticated Azure context without
printing credentials or access tokens.

Establish:

- The intended tenant and subscription, subscription state, effective
  deployment permissions, and ability to assign the required data-plane roles.
- Allowed regions, Azure Policy constraints, provider registration status,
  VM quotas/SKU availability, and Private Resolver regional availability.
- Existing networking and DNS relevant to the lab: address-space conflicts,
  managed private DNS zones, automatic zone-group policies and shared resources.
- Available Azure CLI, Bicep and shell tooling; usable private VM management
  access; and how the agent environment can reach lab data-plane endpoints.
- A small region-specific cost estimate for Stage A, Stage B and both together,
  including one working session and an accidentally retained month.

Recommend an isolated deployment with nonoverlapping address spaces and
lab-owned resource groups. Do not modify subscription-wide policy, shared
VNets, shared DNS, customer workloads or tenant settings to make the lab work.
If policy requires shared integration, explain the conflict and obtain
approval before changing the design.

Before creating billable resources, present one consolidated approval request:
subscription, region, topology/address spaces, chosen VM access and bootstrap
egress, resource inventory, estimated costs, which stage to deploy now, and
the teardown plan. Discover what can be discovered rather than asking me to
look it up. Clearly separate creating local artifacts from deploying resources.

Use **Bicep with Azure CLI** by default. If the repository already mandates
another IaC tool, surface the conflict and agree on the choice; do not build
parallel Bicep and Terraform implementations. Use the shell appropriate to
the destination environment and document it.

## Architecture

Use one region and two stages. Stage A must work independently. Stage B adds
the managed hybrid DNS behavior without replacing Stage A.

### Stage A: Azure-native private access

Create:

- One lab VNet with separate workload and private-endpoint subnets.
- One small Linux client VM with a system-assigned managed identity.
- One standard, locally redundant StorageV2 account, a private Blob container
  and a harmless sample object. Keep hierarchical namespace disabled.
- One private endpoint targeting the storage account's **blob** subresource.
- One Azure Private DNS zone, `privatelink.blob.core.windows.net`, linked to
  the lab VNet, with autoregistration disabled.
- A private DNS zone group associating the endpoint with that zone, so Azure
  manages the endpoint's A record rather than scripts duplicating it.
- The least-privilege Blob data roles needed by the exercise identities,
  scoped to the container where supported.

Disable storage **public network access** and anonymous Blob access. Explain
that these are different controls. Use managed identity for sample data
operations; do not introduce account keys or long-lived SAS tokens.

Keep the VM without a public IP by default. Choose an approved management
method, such as Azure Run Command or an appropriate Bastion option, after
checking capabilities and costs. Do not assume that the operator's laptop
or Cloud Shell has a private network path to Storage.

Plan explicit outbound connectivity if guest provisioning needs repositories,
packages or other public services. Do not rely on implicit/default outbound
internet access. Account for its cost and distinguish bootstrap egress from
the private Storage data path.

Start with Blob Storage to avoid mixing SMB and domain-authentication
requirements into the DNS lesson. Azure Files may be a documented optional
follow-on, not a required deployment.

### Stage B: simulated corporate network and managed hybrid DNS

Extend the lab with:

- A second VNet named and described as **corporate simulation**.
- Direct, bidirectional VNet peering between it and the lab VNet.
- One small Linux DNS VM in the corporate-simulation VNet, using a supported
  DNS server such as BIND. It may also be the corporate test client.
- A reserved test namespace such as `corp.example.test`, authoritative on
  that DNS server, with a sample record pointing to a known private address.
- Azure DNS Private Resolver in the lab VNet, with separate dedicated,
  correctly delegated inbound and outbound endpoint subnets.
- A forwarding ruleset associated with the outbound endpoint, linked to the
  lab VNet, forwarding `corp.example.test.` to the corporate DNS server.
- A corporate conditional forwarder for `blob.core.windows.net` directed
  at the Private Resolver inbound endpoint.

Use current supported subnet sizes and IP-allocation options. Prefer stable
addresses for DNS targets and expose the actual assigned addresses as outputs.
Constrain UDP and TCP 53 access and DNS recursion to the required lab networks.

Azure clients should use Azure-provided DNS. The corporate-side test client
must use the corporate DNS service. Link the Storage private DNS zone to
the resolver's lab VNet, **not** to the corporate-simulation VNet. Do not link
the Azure forwarding ruleset to the corporate-simulation VNet. This preserves
the intended forwarding path and avoids accidentally making the exercise
work through a shortcut.

If the corporate DNS VM also performs Blob data operations, give its identity
only the required container-scoped data role. Do not assume network access
grants authorization.

Explain these three independent flows:

1. Azure client -> Azure-provided DNS -> linked private zone -> endpoint IP.
2. Corporate client -> corporate DNS -> conditional forwarder -> resolver
   inbound endpoint -> Azure Private DNS -> endpoint IP.
3. Azure client -> Azure-provided DNS -> linked forwarding ruleset ->
   resolver outbound endpoint -> corporate DNS -> corporate record.

Then show that application traffic to Storage goes directly to the private
endpoint over the appropriate VNet/peering path; it does not traverse the
DNS resolver.

This is a real Azure deployment with a **simulated on-premises side**, not
an actual VPN/ExpressRoute hybrid network or a production HA reference design.
Document how real corporate connectivity would replace the simulated
transport, but do not deploy VPN Gateway, ExpressRoute, Azure Firewall, AD DS,
multi-region infrastructure or a full hub-and-spoke routing platform.

## Technical invariants

- Applications use the ordinary `account.blob.core.windows.net` hostname,
  not a hard-coded private IP or a replacement connection hostname.
- Ordinary CNAME chaining is not a weighted-priority mechanism.
- Private endpoint creation does not disable public network access.
- A standard private endpoint does not provide reverse connectivity from
  the PaaS service into the VNet.
- DNS resolution, IP reachability, storage network policy and authorization
  are separate requirements.
- `168.63.129.16` is Azure's platform DNS address, not a directly usable
  on-premises forwarding target.
- Follow the service's recommended public-zone conditional forwarding
  suffix; for Blob, use `blob.core.windows.net`, not just `privatelink...`.
- Do not override the public service namespace with a locally authoritative
  zone or mix Azure DNS and custom DNS as interchangeable fallback servers.
- Do not duplicate the same private endpoint records in AD/BIND and Azure
  Private DNS. A manual-record comparison can be explanatory only.
- Prevent forwarding loops. Corporate DNS is authoritative for the test
  corporate zone; it must not forward that zone back to Azure.
- Peering provides connectivity, not automatic private DNS zone linkage.
  Distinguish private-zone links from forwarding-ruleset links.
- If an exercise uses NSGs or UDRs on a private-endpoint subnet, explicitly
  configure the appropriate private endpoint network policy and demonstrate
  effective behavior. Do not assume every route or NSG automatically applies.

## Required deliverables

Keep the project small and coherent:

| Artifact | Required content |
| --- | --- |
| `README.md` | Purpose, prerequisites, quick start, file map, deployment status, and how to enter either learning track. |
| `lab-guide.md` | The complete learning experience specified below. |
| `infra/` | Complete modular Bicep, documented parameters/example configuration, outputs and dependencies for both stages. |
| `scripts/` | Environment-appropriate preflight, deploy, validate, fault/recovery and cleanup helpers. Avoid needless wrapper layers. |
| `.gitignore` | Exclude secrets, local account-specific configuration, generated outputs and private operational evidence. |

Use parameterized subscription selection, region, unique naming, address
spaces, VM sizing and stage selection. Give every taggable resource `repo`,
`project`, `deployment`, `owner` and `expiresOn` tags using verified or
approved values. Treat `expiresOn` as metadata, not automatic deletion.

Make deployments repeatable. Do not produce pseudocode, missing modules,
unimplemented TODOs, destructive replacement defaults or success-shaped
fallbacks. Keep secrets out of source, outputs, logs and screenshots; never
overwrite existing secret files. Do not create reusable passwords for the
lab; use the approved authentication/management approach.

Provide explicit extension teardown. In incremental Bicep deployments,
changing a creation flag to false does **not** delete previously created
resources. Handle Stage B deletion and any peering/link references without
deleting Stage A or leaving billable resources behind. Separate stage-owned
resource groups if that makes lifecycle management clearer.

## Requirements for lab-guide.md

Write for an experienced IT practitioner learning Azure-specific behavior.
Explain why each component exists, not merely which button to press.

Include:

1. Scenario, objectives, prerequisites and scope; a bill of materials with
   region-specific pricing sources, access date and stated assumptions.
2. Renderable architecture and DNS/application-flow diagrams, plus an
   address/subnet/DNS inventory and deployment dependency order.
3. An initial mental-model lesson and a short comparison with the three videos.
4. Two genuinely usable, end-to-end tracks: **IaC** and **Azure portal**.
5. Stage A exercises, followed by Stage B exercises; each should state the
   starting state, action, expected observation, explanation and recovery.
6. A common troubleshooting and fault-injection section.
7. Cleanup, cost verification, knowledge checks with answers, and references.
8. A concise mapping to relevant current AZ-104, AZ-305 and AZ-700 objectives,
   without claiming that this lab covers an entire exam.

### IaC track

Show prerequisite checks, parameter preparation, Bicep module walkthroughs,
build/validation, what-if, staged deployments, outputs, exercises, repeat
deployment and cleanup. Explain which resources each module creates and
which portal blades show the resulting configuration.

Use deployment outputs in commands rather than copying sample resource IDs
or private IPs into scripts. Make commands executable in the documented shell.
Run data-plane exercises from clients with the intended private path, including
sample-object creation after identity and role assignment propagation.

### Azure portal track

Provide manual resource-creation steps in dependency order, with the important
fields and settings spelled out. A link to "Deploy a custom template" is not
a manual portal track. Cover VNets/subnets, VM identities, data roles, Storage
settings, private endpoint/zone group/zone link, peering, resolver endpoints,
ruleset association/link, and the DNS-server guest configuration.

For guest configuration or commands with no portal-native editor, show how
to run them through the approved VM access or Run Command path. Clearly
distinguish portal resource configuration from in-guest DNS configuration.

Provide a resource-by-resource mapping between portal choices and IaC
parameters/resources. Both tracks must reach equivalent behavior.

Keep track instances distinct: use different lab identifiers/resource groups,
or fully tear down one track before starting the other. Do not tell me to
manually edit an IaC-managed deployment as though it were a separate portal
build. Document how intentional fault-induced drift is restored.

Date the portal instructions. If browser interaction is unavailable, cross-check
resource settings against current documentation and live APIs, but explicitly
label the click-through path as not personally exercised. Do not invent
screenshots or claim automated deployment proves the portal procedure.

## Exercises and evidence

Produce a pass/fail/blocked matrix with expected versus observed results.
At minimum, cover:

| Exercise | What it must establish |
| --- | --- |
| Azure-side DNS | The ordinary Blob hostname resolves through its CNAME to the intended private endpoint IP. |
| Azure-side data access | An authorized managed identity can write/read the sample Blob through the private path. |
| Public network restriction | Storage public network access is disabled; where a suitable outside client and valid authorization are available, demonstrate rejection through the public path. |
| Corporate-to-Azure DNS and data | The corporate client obtains the private answer through its DNS forwarder and the resolver inbound endpoint, then accesses the Blob over peering. |
| Azure-to-corporate DNS | An Azure client resolves the corporate test record through the outbound endpoint/ruleset. |
| Broken zone linkage | Predict and observe how removing the lab's private-zone link changes resolution or access, then restore it. |
| Incorrect corporate forwarding | Introduce a controlled wrong target or suffix, isolate the cause, and recover. |
| Disabled outbound rule | Break corporate-name resolution without confusing it with Storage private-zone resolution, then recover. |
| Network denial | Introduce a narrow, effective lab-only NSG block that prevents the intended data connection while preserving diagnostic access, then recover. |
| Authorization denial | Demonstrate a data-role failure while DNS and network connectivity remain correct, then recover. |
| Repeat deployment and cleanup | Reapplying the approved configuration produces no unintended drift; the cleanup path removes only this lab's resources. |

Use observable query/server output, resource configuration, effective network
rules, data-plane results and DNS-server diagnostics where available to
establish the actual paths. A successful deployment or `nslookup` alone is
not sufficient.

Do not interpret every HTTP 403 as a network failure. Use the service error
details and controlled identity/network state. Do not treat an unauthenticated
request's rejection as proof of public network isolation. If an outside-path
test cannot be performed, mark it untested instead of weakening policy.

Use lab-only fault injection with clear confirmation, a captured baseline,
one failure at a time and explicit restoration. Account for DNS caches, TTLs,
identity tokens and RBAC propagation; use bounded retries with diagnostic
errors rather than arbitrary sleeps or indefinite loops. Finish in a known,
healthy state unless I explicitly choose teardown.

For each learning objective, include a short "explain / configure / diagnose"
checkpoint. Watching a video or running a script is not the completion gate.

## Cost, safety and completion

Do not assume CSA credits make the deployment free. Identify all ongoing
charges, including resolver endpoints, VMs/disks, private endpoints, chosen
egress/access services and any diagnostics. Explain that VM deallocation
does not stop every charge and that budget alerts are not hard spending caps.

Provide a cleanup dry-run listing exact subscription, resource groups and
resource IDs. Require explicit confirmation for deletion, restrict it to
verified lab-owned resources, handle cross-resource references, and inspect
remaining resources afterward. Do not claim billing records update instantly.
Do not use wildcard name matches as deletion authority.

After implementation, report:

- What was created, the approved configuration and the lab-guide entry points.
- Which stage and learning track were actually deployed and exercised.
- The observed acceptance results and any untested/blocked items.
- What remains running, its estimated ongoing cost, and exact teardown steps.
- Any documented deviations from the requested architecture and why.

Do not stop after writing IaC. Once deployment is approved, carry the agreed
scope through deployment, real exercises and correction of lab-caused failures.
Do not claim completion of a stage that has not been exercised. Conversely,
do not deploy a second paid copy just to validate portal parity without approval.
