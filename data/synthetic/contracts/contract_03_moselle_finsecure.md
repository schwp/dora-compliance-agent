# ICT SERVICE AGREEMENT

**Agreement Reference:** ICT-R00089-724500DE-2024

---

**Between:**

**The Financial Entity ("Client")**
Moselle Reinsurance S.A.
4, Rue Jean Monnet, L-2180 Luxembourg
CSSF Registration: R00089
LEI: 529900STUVWX234YZA67
Entity Type: Reinsurance Undertaking

**And:**

**The ICT Service Provider ("Provider")**
FinSecure Solutions B.V.
Amsterdam, Netherlands
LEI: 724500DEFGH678IJKLM9
Provider Type: Managed Security Service Provider

**Date of Agreement:** 2024-01-01
**Effective Date:** 2024-01-01
**Expiry Date:** 2026-12-31
**Governing Law:** Laws of the Grand Duchy of Luxembourg

---

## Article 1 — Scope of Services

1.1. The Provider shall supply the following ICT service to the Client:

**Service Name:** Managed Detection and Response (MDR)

**Description:** 24/7 security monitoring, threat detection, incident response, and vulnerability management services including SIEM operation and endpoint detection.

1.2. The service supports a **critical or important function** of the Client, namely: *ICT security and cyber resilience*.

1.3. The ESA service type classification for this arrangement is: `ICT-SS-008`.

1.4. **Annual Cost:** EUR 120,000 (exclusive of VAT), payable in quarterly instalments.

## Article 2 — Subcontracting

2.1. The Provider shall not subcontract any part of the service to third parties without prior written approval from the Client.

## Article 3 — Data Location and Processing

3.1. All Client data shall be processed and stored within the following locations:

| Purpose | Country | Region |
|---|---|---|
| Primary processing | France (FR) | EU |
| Disaster recovery / backup | Luxembourg (LU) | EU |

3.2. No Client data shall be transferred to, processed in, or stored in any location outside the European Economic Area without the prior written consent of the Client.

3.3. The Provider shall notify the Client at least **90 calendar days** in advance of any planned change to the data processing or storage locations specified in this Article.

## Article 4 — Data Protection and Security

4.1. The Provider shall implement and maintain appropriate technical and organisational measures to ensure the **availability, authenticity, integrity, and confidentiality** of all Client data processed under this Agreement.

4.2. These measures shall include, at a minimum:
- Encryption of data at rest (AES-256) and in transit (TLS 1.2+);
- Multi-factor authentication for administrative access;
- Regular vulnerability scanning and remediation;
- Logical segregation of Client data from other customers' data;
- Annual SOC 2 Type II audit reports provided to the Client.

4.3. The Provider shall process personal data exclusively in accordance with Regulation (EU) 2016/679 (GDPR) and any applicable data processing agreement between the Parties.

## Article 5 — Data Access, Recovery and Return

5.1. Upon termination or expiry of this Agreement, or in the event of the Provider's insolvency, resolution, or discontinuation of business operations, the Provider shall:

(a) Ensure the Client has continuous access to its data throughout any transition period;

(b) Return all Client data in an easily accessible, standard, machine-readable format (CSV, JSON, or SQL dump) within **30 calendar days**;

(c) Provide reasonable migration assistance for a period of **6 months** following termination;

(d) Securely delete all Client data from its systems within **90 calendar days** of the completed data return, and provide written certification of deletion.

5.2. The Provider shall maintain adequate business continuity arrangements to ensure data accessibility in the event of its own operational disruption or insolvency proceedings.

## Article 7 — Cooperation with Competent Authorities

7.1. The Provider shall cooperate fully with the Commission de Surveillance du Secteur Financier (CSSF), the European Central Bank (ECB), the European Supervisory Authorities (EBA, EIOPA, ESMA), and any resolution authority exercising supervisory or resolution powers over the Client.

7.2. This cooperation shall include, without limitation, providing information, granting access to premises, and facilitating inspections as required by applicable law or regulatory request.

## Article 8 — Termination

8.1. Either Party may terminate this Agreement by providing **6 months'** written notice prior to the expiry date.

8.2. The Client may terminate this Agreement with immediate effect in the event that:

(a) The Provider commits a material breach of this Agreement that is not remedied within 30 calendar days of written notice;

(b) The Provider undergoes insolvency, liquidation, or administration proceedings;

(c) The competent authority requires such termination;

(d) The Provider's performance consistently fails to meet the agreed service levels over a period of 3 consecutive months.

8.3. The minimum notice period for ordinary termination shall be **6 months**.

## Article 9 — Service Level Agreement

9.1. The Provider shall meet the following quantitative performance targets:

| Metric | Target | Measurement Period | Penalty |
|---|---|---|---|
| Service availability | ≥ 99.95% | Monthly | 2% credit per 0.01% below target |
| Mean time to respond (P1 incidents) | ≤ 15 minutes | Per incident | EUR 5,000 per hour of delay |
| Mean time to resolve (P1 incidents) | ≤ 4 hours | Per incident | EUR 10,000 per hour of delay |
| Recovery Time Objective (RTO) | ≤ 4 hours | Per incident | Contractual escalation |
| Recovery Point Objective (RPO) | ≤ 1 hour | Per incident | Contractual escalation |
| Scheduled maintenance windows | ≤ 8 hours/month | Monthly | Prior notice required |

9.2. The Provider shall deliver a monthly service performance report to the Client by the 5th business day of the following month.

9.3. If any service level is not met for 3 consecutive months, the Client may invoke the remediation procedure under Article 8.2(d).

## Article 10 — Business Contingency and ICT Security

10.1. The Provider shall implement, maintain, and regularly test business contingency plans relevant to the service.

10.2. The Provider shall conduct at least **one full disaster recovery test per year** and provide the test results and remediation plan to the Client within 30 calendar days of the test.

10.3. The Provider shall maintain ICT security measures, tools, and policies that provide a level of security appropriate to the regulatory requirements applicable to the Client, including DORA and applicable CSSF circulars.

## Article 12 — Audit and Inspection Rights

12.1. The Client, any third party appointed by the Client, and the competent authority (CSSF) shall have **unrestricted rights of access, inspection, and audit** of the Provider's premises, systems, and documentation relevant to the service.

12.2. The Provider shall make available copies of all relevant documentation on-site during any such inspection.

12.3. These rights shall not be impeded, limited, or restricted by any other contractual arrangement or implementation policy of the Provider.

12.4. The Provider shall cooperate with pooled audits where the Client participates in a joint audit arrangement with other financial entities using the same Provider.

## Article 13 — Exit Strategy and Transition

13.1. The Parties agree to the following exit strategy to enable an orderly transition:

(a) **Transition period:** 12 months from the date of termination notice;

(b) **Data migration:** The Provider shall actively support migration of all Client data and configurations to a successor provider or in-house solution;

(c) **Knowledge transfer:** The Provider shall provide documentation, training, and technical support necessary for the Client to operate independently or transition to an alternative provider;

(d) **Parallel running:** During the transition period, the Provider shall continue to operate the service at full agreed service levels;

(e) **No lock-in:** The Provider shall ensure the service is delivered using industry-standard formats and protocols that facilitate portability.

13.2. The costs of the exit strategy shall be borne by the Provider, except where migration requires bespoke development, in which case costs shall be agreed in advance.

---

## Signatures

**For the Client — Moselle Reinsurance S.A.**

Name: _________________________
Title: Chief Operating Officer
Date: 2024-01-01

**For the Provider — FinSecure Solutions B.V.**

Name: _________________________
Title: Managing Director
Date: 2024-01-01

---
*This Agreement constitutes the entire agreement between the Parties with respect to the subject matter hereof.*
