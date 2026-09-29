# Research notes: POPIA compliance for a small South African private company

This research was done in September 2026 and is what the app's content is based on. It is not legal advice.

## Profile assumed

- A private company (Pty) Ltd with employees.
- It processes employee and HR data, and customer and supplier data (including contact persons at other companies).
- It has some special personal information (employee health information, possibly biometrics or race for Employment Equity).
- It uses overseas cloud services (email, file storage, possibly Hetzner hosting).
- It does no significant direct marketing.

## The legal framework

| Instrument | What it requires of the business | Status (Sep 2026) |
| --- | --- | --- |
| **POPIA** (Act 4 of 2013) | Eight conditions for lawful processing (s8–25); special personal information (s26–33); children (s34–35); Information Officer (s55–56); prior authorisation (s57–58); direct marketing (s69); automated decisions (s71); cross-border transfers (s72); administrative fines up to R10 million (s109) | Fully in force since 1 July 2021 |
| **POPIA Regulations** (2018, amended by GN 6126 with effect from 17 April 2025) | Reg 4: the Information Officer must develop, implement, monitor, maintain and **continuously improve** a compliance framework, ensure an impact assessment is done, set up request-handling systems and run awareness sessions. Objections (Form 1) and correction or deletion requests (Form 2) can use "substantially similar" forms, arrive by any channel and are **free**. Direct-marketing consent must be "substantially similar" to Form 4, free and specific, and **an opt-out is not consent**. | In force |
| **Health Information Regulations** under s32(6) | Detailed rules for processing health information by insurers, medical schemes, pension funds, administrative bodies **and employers**. They stress confidentiality (s32(2)), safeguards and transparency. | Published in Government Gazette 54268 and in force from 6 March 2026, with no transition period |
| **Guidance Note on Direct Marketing** (Dec 2024) | Electronic marketing (email, SMS, and in the Regulator's view all phone calls) requires opt-in consent or an existing-customer relationship, and every message needs an opt-out | Non-binding guidance |
| **Security compromise reporting** | s22 notifications to the Regulator must be made on the **eServices portal** (form SCN1). Email is no longer accepted. | Since 1 April 2025 |
| **PAIA** (Act 2 of 2000) | s51 manual for **every** private body; the small-business exemption ended 31 Dec 2021. s83(4) annual report due on the eServices portal between **1 April and 30 June**, covering 1 April to 31 March. Access decisions within 30 days (s56), extendable once by 30 days (s57). | In force; the Regulator confirms the annual report is mandatory for all private bodies |
| **Transborder flows guidance note** | Will cover s72 transfers and cloud computing | Under development in the Regulator's 2025/26 plan and **not yet published**, so the app records a s72 basis per operator |

## Enforcement climate

- The Regulator received 2,374 security compromise notifications in 2024/25, and monthly notifications rose about 40% year on year in early 2025/26. It is consolidating breach expertise, and its 2025/26 plan signals tougher enforcement of POPIA and PAIA.
- The largest fines so far are R5 million each, against the Department of Justice (2021 ransomware attack, then failing to comply with an enforcement notice) and the Department of Basic Education. The DBE's notices were set aside on appeal in December 2025, and leave to appeal was refused in June 2026.
- In 2026 the Regulator has issued enforcement notices to both public and private bodies for contraventions of POPIA and PAIA.

## Decisions made in the app

- **The Information Officer defaults to the head of the business.** This follows POPIA s1 and PAIA s1. The app records IO registration because s55(2) says the IO only takes up duties after registration.
- **The breach test has no risk threshold.** POPIA s22 triggers on "reasonable grounds to believe … accessed or acquired by any unauthorised person", unlike GDPR's risk-based test. The app therefore treats every confirmed or suspected unauthorised access as notifiable.
- **Retention periods.** Statutory minimums come from BCEA s31 (3 years), LRA s205 (3 years), the UIF Act (5 years), COIDA (4 years), Tax Administration Act s29/s32 (5 years from submission of the return), Companies Act s24 (7 years, with founding records kept indefinitely) and the OHS General Administrative Regulations (3 years). Policy periods are marked as such, for example 6 months for unsuccessful applicants, which matches EEA s10's 6-month window for referring disputes. **Confirm these with your accountant.**
- **Hosting.** Hetzner has no South African region. Choosing its German or Finnish locations makes the transfer defensible under s72(1)(a), because the recipient is bound by GDPR. The app seeds Hetzner as a draft operator with instructions to accept the Hetzner DPA. Running the app locally avoids the transfer entirely.
- **Juristic persons.** POPIA protects existing companies as data subjects, so B2B contact and supplier records are in scope.

## Sources

- Information Regulator: [eServices portal](https://eservices.inforegulator.org.za), [PAIA annual report](https://inforegulator.org.za/paia-annual-report/), [Fact sheet: handling of security compromises (Aug 2025)](https://inforegulator.org.za/2025/08/19/fact-sheet-handling-of-security-compromises/), [Contact](https://inforegulator.org.za/contact-us/), [Complaints](https://inforegulator.org.za/complaints/)
- Bowmans: [POPIA Regulations get a makeover](https://bowmanslaw.com/insights/south-africa-popia-regulations-get-a-makeover-what-you-need-to-know/); [POPIA Health Information Regulations cross the finish line](https://bowmanslaw.com/insights/south-africa-popia-health-information-regulations-cross-the-finish-line/); [Timeous submission of annual PAIA reports](https://bowmanslaw.com/insights/south-africa-organisations-should-ensure-the-timeous-submission-of-their-annual-paia-reports/); [Online portal for registration of information officers](https://bowmanslaw.com/insights/south-africa-online-portal-for-the-registration-of-information-officers-is-now-live/)
- Baker McKenzie / Global Compliance News: [Amendments to the POPIA regulations: key changes](https://www.globalcompliancenews.com/2025/05/19/https-insightplus-bakermckenzie-com-bm-data-technology-south-africa-amendments-to-the-popia-regulations-key-changes-you-need-to-know_05062025/)
- Cliffe Dekker Hofmeyr: [Important POPIA amendments to note (May 2025)](https://www.cliffedekkerhofmeyr.com/en/news/publications/2025/Sectors/Technology-Communications/Technology-and-Communications-Alert-21-May-Important-POPIA-amendments-to-note)
- Michalsons: [POPIA Amendment Regulations commence](https://www.michalsons.com/blog/popia-amendment-regulations-commence/77824); [PAIA s83(4) report](https://www.michalsons.com/blog/paia-section-834-report-for-private-bodies/65629); [Guidance note on transborder flows](https://www.michalsons.com/blog/guidance-note-on-cross-border-transfers-to-from-south-africa/77246)
- Moonstone: [Amended regulations tighten direct marketing](https://www.moonstone.co.za/amended-popia-regulations-tighten-the-screws-on-direct-marketing/); [Regulator signals tougher enforcement](https://www.moonstone.co.za/information-regulator-signals-tougher-popia-and-paia-enforcement/); [Health information regulations in force](https://www.moonstone.co.za/new-popia-regulations-on-health-information-now-in-force/)
- Werksmans: [Information Regulator's 2025/26 Annual Performance Plan](https://werksmans.com/south-africas-information-regulator-what-the-2025-26-annual-performance-plan-means-for-business-as-presented-to-the-portfolio-committee-on-5-may-2026/)
- Fasken: [Health data under the microscope (Apr 2026)](https://www.fasken.com/en/knowledge/2026/04/health-data-under-the-microscope-new-popia-regulations)
- Lexology: [Certain private bodies exempt from PAIA manual (historic exemption)](https://www.lexology.com/library/detail.aspx?g=5611203c-f83a-44fe-ae1f-10fe2a5c4dd9); SAICA: [All private bodies must prepare a PAIA manual](https://www.saica.org.za/news/saica-reminds-all-private-bodies-to-prepare-a-paia-manual/)
- Enforcement: [Bowmans: first R5 million fine](https://bowmanslaw.com/insights/south-africa-beware-information-regulator-issues-first-fine-of-zar-5-million-under-popia/); [MJ Kotze: enforcement tracker](https://mjkinc.co.za/popia/enforcement-tracker)
- Cross-border: [popia.co.za: s72](https://popia.co.za/section-72-transfers-of-personal-information-outside-republic/); [CMS: managing cross-border data transfers](https://cms.law/en/zaf/publication/managing-cross-border-data-transfers)
- Retention: [SARS: record keeping](https://www.sars.gov.za/client-segments/record-keeping/)
