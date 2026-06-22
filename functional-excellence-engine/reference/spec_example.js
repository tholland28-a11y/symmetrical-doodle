/**
 * spec_example.js — a gold-standard filled spec for the Cybersecurity function.
 *
 * Use this as the worked reference when writing Stage-4 specs, and as the
 * ground-truth fixture for the build/validate/gate loop. Every case here is a
 * real, named, dated event with a verifiable source — the standard the engine
 * enforces. Counts match the contract: 6 axioms, 4 pillars, 8 metrics,
 * 10 diagnostics, 6 interventions, 8 cases.
 */

module.exports = {
  title: "Cybersecurity",

  control:
    "Cybersecurity is the function that protects the confidentiality, integrity, and " +
    "availability of the systems and data the business runs on. For the board, the question " +
    "is not whether an incident will occur but whether the organization will detect it early, " +
    "contain it fast, and recover without losing customer trust or violating its obligations. " +
    "Excellence here is measured in dwell time, blast radius, and the credibility of the " +
    "controls that survive an audit.",

  landscape:
    "The threat landscape is adversarial and professionalized: ransomware-as-a-service, " +
    "supply-chain compromise, and credential theft dominate, while regulators (FTC, state AGs, " +
    "SEC disclosure rules, GDPR) raise the cost of failure. Attack surface expands with cloud, " +
    "SaaS sprawl, and remote work. The defender's advantage is asymmetric only when identity, " +
    "logging, and patching are disciplined.",

  economics:
    "The economics are dominated by tail risk: most spend prevents low-probability, " +
    "high-severity loss. The 2024 IBM Cost of a Data Breach report put the global average " +
    "breach at USD 4.88M, with breaches contained in under 200 days costing materially less. " +
    "The levers are prevention (patch, MFA, segmentation), detection (logging, monitoring), and " +
    "response (rehearsed playbooks) — each cheaper than the breach it averts.",

  axioms: [
    "Assume breach: design controls for when prevention fails, not only to prevent.",
    "Identity is the perimeter; multi-factor authentication on every privileged path is non-negotiable.",
    "You cannot defend what you cannot see — asset inventory and logging precede everything.",
    "Patch velocity beats patch perfection; known-exploited vulnerabilities are the priority queue.",
    "Segment to contain: a flat network turns one compromise into an enterprise outage.",
    "Rehearsed response beats a written plan; the runbook you never drilled will fail under load.",
  ],

  pillars: [
    { name: "Identity & Access", detail: "Strong authentication, least-privilege, and just-in-time access for administrators; rapid de-provisioning." },
    { name: "Visibility & Detection", detail: "Complete asset inventory, centralized logging, and monitoring tuned to known attacker behavior." },
    { name: "Resilience & Recovery", detail: "Immutable, tested backups and rehearsed incident response so recovery time is predictable." },
    { name: "Supply-Chain & Third-Party Risk", detail: "Inventory of vendors and software dependencies with vetting proportionate to the access they hold." },
  ],

  metricsIntro:
    "Track a small set of metrics that map to detection, containment, and hygiene. Targets are " +
    "starting points to calibrate against the organization's size and risk appetite.",

  metrics: [
    { name: "Mean time to detect (MTTD)", definition: "Median time from intrusion to detection.", target: "< 24 hours" },
    { name: "Mean time to respond (MTTR)", definition: "Median time from detection to containment.", target: "< 72 hours" },
    { name: "MFA coverage", definition: "Share of accounts (esp. privileged) protected by phishing-resistant MFA.", target: "100% of privileged, > 95% overall" },
    { name: "Critical patch latency", definition: "Time to remediate known-exploited vulnerabilities.", target: "< 14 days (CISA KEV)" },
    { name: "Backup restore success", definition: "Share of recovery drills that meet RTO/RPO.", target: "> 99%" },
    { name: "Phishing report rate", definition: "Share of simulated phish reported by employees.", target: "> 70%" },
    { name: "Privileged account count", definition: "Number of standing admin accounts.", target: "Minimized; trend down quarter over quarter" },
    { name: "Third-party assessment coverage", definition: "Share of high-access vendors with a current security review.", target: "100% of critical vendors" },
  ],

  metricsNote:
    "Metrics measure the program, not the adversary. A clean dashboard during a quiet quarter is " +
    "not proof of safety; pair quantitative metrics with red-team findings and audit results.",

  bestPractices: [
    "Enforce phishing-resistant MFA (FIDO2/WebAuthn) on all administrative and remote access.",
    "Maintain immutable, offline backups and rehearse full restoration at least quarterly.",
    "Prioritize remediation using the CISA Known Exploited Vulnerabilities catalog, not raw CVSS.",
    "Segment networks so OT, payment, and corporate environments cannot pivot freely.",
    "Run tabletop exercises with executives and legal, not just the security team.",
  ],

  failureRefs: [
    "Flat networks that let an initial foothold reach crown-jewel systems unimpeded.",
    "Backups connected to the production domain, encrypted alongside everything else in a ransomware event.",
    "Unpatched internet-facing systems with publicly known exploits.",
    "Shared or non-MFA administrator credentials reused across environments.",
    "Incident plans that exist as documents but have never been drilled under realistic pressure.",
  ],

  diagnostics: [
    "What is our mean time to detect, and how do we know the number is real rather than aspirational?",
    "Which of our internet-facing systems carry vulnerabilities on the CISA KEV list today?",
    "Are our backups immutable and isolated, and when did we last fully restore from them?",
    "Is phishing-resistant MFA enforced on every privileged and remote-access path, without exception?",
    "How many standing administrator accounts exist, and who reviews that list?",
    "If our largest software vendor is compromised, what is our blast radius?",
    "When did the executive team last sit through a ransomware tabletop, and what failed?",
    "Do we have a current, accurate inventory of every asset and data store we are obligated to protect?",
    "What is our regulatory disclosure clock, and who owns the decision to notify?",
    "Which single control, if it failed silently, would hurt us most — and how would we know it failed?",
  ],

  interventions: [
    { name: "Close the MFA gaps", detail: "Inventory every authentication path and enforce phishing-resistant MFA on all privileged and remote access within one quarter." },
    { name: "Isolate and test backups", detail: "Move backups to immutable, offline storage and run a full restoration drill, measuring against RTO/RPO." },
    { name: "Stand up a KEV-driven patch cadence", detail: "Establish a 14-day SLA for remediating known-exploited vulnerabilities on internet-facing systems." },
    { name: "Segment the network", detail: "Separate payment, OT, and corporate zones with enforced controls so one compromise cannot become all of them." },
    { name: "Drill the response", detail: "Run quarterly tabletop exercises that include executives, legal, and communications, capturing and closing gaps." },
    { name: "Govern third-party access", detail: "Inventory vendors by the access they hold and require current security assessments for all critical ones." },
  ],

  plan: [
    { horizon: "0-30 days", actions: [
      "Build or refresh the asset and identity inventory.",
      "Enable phishing-resistant MFA on all administrator accounts.",
      "Confirm at least one isolated, immutable backup of crown-jewel systems.",
    ] },
    { horizon: "31-60 days", actions: [
      "Remediate all CISA KEV-listed vulnerabilities on internet-facing systems.",
      "Run a full backup-restoration drill and record RTO/RPO results.",
      "Begin network segmentation of the highest-value environment.",
    ] },
    { horizon: "61-90 days", actions: [
      "Conduct an executive tabletop exercise and close the top three gaps.",
      "Complete security assessments for all critical third-party vendors.",
      "Report MTTD, MTTR, MFA coverage, and patch latency to the board.",
    ] },
  ],

  cases: [
    {
      name: "data breach", entity: "Wawa", date: "2019-2024",
      context: "Convenience-store and fuel retailer operating point-of-sale and fuel-dispenser systems across the US East Coast.",
      situation: "Malware on point-of-sale and fuel-dispenser systems exposed payment-card data for roughly 34 million cards over about nine months before discovery.",
      approach: "Wawa disclosed the breach, engaged forensics, and ultimately settled multistate litigation; EMV chip transactions were unaffected.",
      result: "An USD 8M multistate settlement was reached in 2024, alongside earlier consumer and financial-institution settlements.",
      lesson: ["Monitor POS and edge devices as first-class assets.", "EMV/chip adoption limits blast radius.", "Long dwell time multiplies the records exposed."],
      source: "https://www.pcworld.com/article/394903/wawa-data-breach.html", tier: 2,
    },
    {
      name: "data breach", entity: "Equifax", date: "2017",
      context: "One of the three major US consumer credit bureaus, holding sensitive data on most American adults.",
      situation: "Attackers exploited an unpatched Apache Struts vulnerability (CVE-2017-5638) for which a fix had been available for months, exposing data on ~147 million people.",
      approach: "Equifax patched belatedly, disclosed after a delay, and entered a global settlement with the FTC, CFPB, and states.",
      result: "A 2019 settlement of up to USD 700M; the breach became the canonical case for patch discipline on known vulnerabilities.",
      lesson: ["Patch known-exploited vulnerabilities on a hard SLA.", "Asset inventory must map which systems run the vulnerable component.", "Disclosure delay compounds regulatory exposure."],
      source: "https://www.ftc.gov/enforcement/refunds/equifax-data-breach-settlement", tier: 1,
    },
    {
      name: "POS breach", entity: "Target", date: "2013-2017",
      context: "Major US big-box retailer at peak holiday shopping season.",
      situation: "Attackers entered through an HVAC vendor's network credentials and pivoted to point-of-sale systems, stealing ~40 million card numbers and ~70 million customer records.",
      approach: "Target contained the incident, overhauled segmentation and vendor access, and accelerated chip-card adoption.",
      result: "An USD 18.5M multistate settlement in 2017 plus large bank and consumer settlements; the case reshaped third-party access controls.",
      lesson: ["Treat vendor credentials as a primary attack path.", "Segment payment systems away from corporate IT.", "Third-party risk is your risk."],
      source: "https://www.nytimes.com/2017/05/23/business/target-security-breach-settlement.html", tier: 2,
    },
    {
      name: "ransomware shutdown", entity: "Colonial Pipeline", date: "2021",
      context: "Operator of the largest refined-fuels pipeline on the US East Coast, supplying ~45% of the region's fuel.",
      situation: "DarkSide ransomware, entering via a single compromised VPN password without MFA, led Colonial to shut the pipeline, triggering regional fuel shortages.",
      approach: "Colonial paid a ~USD 4.4M ransom; the DOJ later clawed back about USD 2.3M of the bitcoin.",
      result: "Operations resumed within days; the incident prompted a TSA security directive for pipeline operators in 2021.",
      lesson: ["Enforce MFA on every remote-access path.", "Disable dormant VPN accounts.", "Operational shutdowns can exceed the direct ransom in cost."],
      source: "https://www.cisa.gov/news-events/news/darkside-ransomware-best-practices-preventing-business-disruption-ransomware-attacks", tier: 1,
    },
    {
      name: "supply-chain compromise", entity: "SolarWinds", date: "2020-2021",
      context: "Maker of the widely deployed Orion IT-management platform used by thousands of enterprises and US agencies.",
      situation: "Nation-state actors implanted a backdoor (SUNBURST) into Orion software updates, distributing it to ~18,000 customers and breaching multiple federal agencies.",
      approach: "Affected organizations hunted for the implant, rotated credentials, and rebuilt trust in their software supply chains; the SEC later charged SolarWinds over disclosures.",
      result: "The incident drove the 2021 US Executive Order 14028 on software supply-chain security and SBOM requirements.",
      lesson: ["Software updates are an attack vector.", "Maintain a software bill of materials.", "Assume trusted vendors can be compromised."],
      source: "https://www.cisa.gov/news-events/news/cisa-issues-emergency-directive-mitigate-solarwinds-orion-code-compromise", tier: 1,
    },
    {
      name: "Log4Shell vulnerability", entity: "CVE-2021-44228", date: "2021",
      context: "A critical remote-code-execution flaw in Apache Log4j, a logging library embedded in countless Java applications.",
      situation: "The vulnerability allowed trivial remote code execution and was present transitively in software organizations did not even know they ran.",
      approach: "CISA issued emergency guidance; organizations scrambled to inventory dependencies and patch or mitigate within days.",
      result: "Added to the CISA KEV catalog immediately; it became the textbook example of why a software bill of materials matters.",
      lesson: ["You must be able to find a dependency to patch it.", "Transitive dependencies hide risk.", "Maintain an SBOM for rapid response."],
      source: "https://www.cisa.gov/news-events/alerts/2021/12/10/apache-log4j-vulnerability-guidance", tier: 1,
    },
    {
      name: "NotPetya wiper", entity: "Maersk", date: "2017",
      context: "The world's largest container-shipping company, dependent on integrated global IT for port and logistics operations.",
      situation: "The NotPetya wiper, spread via a compromised Ukrainian tax-software update, destroyed Maersk's domain controllers and most of its endpoints worldwide.",
      approach: "Maersk rebuilt its IT from a single surviving domain-controller copy and ran operations manually during recovery.",
      result: "Estimated losses of ~USD 300M; the case is a benchmark for resilient backups and segmentation.",
      lesson: ["Keep at least one isolated copy of critical infrastructure.", "Segment to stop self-propagating malware.", "Rehearse manual fallback operations."],
      source: "https://www.wired.com/story/notpetya-cyberattack-ukraine-russia-code-crashed-the-world/", tier: 2,
    },
    {
      name: "cloud misconfiguration breach", entity: "Capital One", date: "2019",
      context: "Large US bank that had migrated significant infrastructure to public cloud.",
      situation: "A misconfigured web-application firewall allowed an attacker to exploit a server-side request forgery flaw and access ~100 million customer records in cloud storage.",
      approach: "Capital One disclosed promptly, cooperated with law enforcement (the attacker was arrested), and remediated cloud configurations.",
      result: "An USD 80M OCC penalty in 2020 and a USD 190M consumer settlement; a landmark cloud-misconfiguration case.",
      lesson: ["Cloud security is a shared-responsibility model.", "Audit WAF and IAM configurations continuously.", "SSRF against metadata endpoints is a known cloud risk."],
      source: "https://www.occ.treas.gov/news-issuances/news-releases/2020/nr-occ-2020-101.html", tier: 1,
    },
  ],

  ceoPriorities: [
    "Own the disclosure decision: know the regulatory clock and who pulls the trigger before an incident, not during one.",
    "Fund resilience, not just prevention — tested backups and rehearsed response are the difference between an incident and a crisis.",
    "Hold the organization to MFA and patch SLAs as board-level commitments with reported metrics.",
  ],

  maintenance:
    "Review MTTD, MTTR, MFA coverage, and patch latency at every board meeting; refresh the asset " +
    "and vendor inventories quarterly; run an executive tabletop and a backup-restoration drill at " +
    "least twice a year; and treat every real incident as a post-mortem that updates the runbook.",

  sources: [
    { label: "IBM Cost of a Data Breach Report 2024", url: "https://www.ibm.com/reports/data-breach" },
    { label: "CISA Known Exploited Vulnerabilities Catalog", url: "https://www.cisa.gov/known-exploited-vulnerabilities-catalog" },
    { label: "FTC Equifax data breach settlement", url: "https://www.ftc.gov/enforcement/refunds/equifax-data-breach-settlement" },
    { label: "Executive Order 14028 on Improving the Nation's Cybersecurity", url: "https://www.federalregister.gov/documents/2021/05/17/2021-10460/improving-the-nations-cybersecurity" },
  ],
};
