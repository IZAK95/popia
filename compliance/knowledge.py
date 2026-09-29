"""
POPIA knowledge base used to seed the compliance framework.

Sources (researched September 2026):
- Protection of Personal Information Act 4 of 2013 (POPIA), especially ss 8-35, 55-58, 69-72, 107-109.
- POPIA Regulations 2018 as amended with effect from 17 April 2025 (GN 6126 of 2025): regulation 4
  (Information Officer duties; compliance framework must be "continuously improved"), objections and
  correction requests via any channel free of charge, direct-marketing consent "substantially similar to
  Form 4" where an opt-out does not count as consent.
- Regulations relating to the Processing of Health Information (in force 6 March 2026) - apply to employers.
- Information Regulator: security compromises must be reported on the eServices portal (since 1 April 2025);
  Information Officers are registered on the eServices portal; PAIA s83(4) annual reports are submitted
  on the eServices portal between 1 April and 30 June for the period 1 April - 31 March.
- Promotion of Access to Information Act 2 of 2000 (PAIA) s51 manual - small-business exemption ended
  31 December 2021, so every private body needs one.
- Guidance Note on Direct Marketing (December 2024).

This is practical guidance, not legal advice. Have an attorney review your final documents if you can.
"""

# (code, area, essential, title, why, how, legal_ref, action_url, action_label)
CHECKLIST = [
    # ---------------- Governance ----------------
    (
        "GOV-01", "governance", True,
        "Confirm who your Information Officer is",
        "Every business must have an Information Officer (IO) – the person accountable for POPIA compliance. "
        "By law it is the head of the business (owner, CEO or managing director). The head may authorise another "
        "employee to act as IO, but stays ultimately responsible.",
        "1. Decide whether you (as head) will be the IO or authorise someone else.\n"
        "2. Fill in the Information Officer section of the Company profile.\n"
        "3. Generate and sign the 'Information Officer appointment' document and file it.",
        "POPIA s1, s55; PAIA s1", "compliance:profile", "Open company profile",
    ),
    (
        "GOV-02", "governance", True,
        "Register your Information Officer with the Information Regulator",
        "The IO may only take up their duties after being registered with the Information Regulator. Registration is free "
        "and done online. Unregistered IOs are one of the first things the Regulator checks.",
        "1. Go to https://eservices.inforegulator.org.za and create a user profile.\n"
        "2. Choose 'Information Officer registration' and capture the business (CIPC number) and IO details.\n"
        "3. Save the confirmation/reference and record the date in the Company profile.",
        "POPIA s55(2); Regulation 4", "compliance:profile", "Record registration",
    ),
    (
        "GOV-03", "governance", False,
        "Designate a Deputy Information Officer (if needed)",
        "Deputies help make the business 'as accessible as reasonably possible' for requests. A very small business can "
        "operate with just the IO – mark this Not applicable and explain why.",
        "If someone else can handle requests when the IO is away, designate them in writing, register them on the "
        "eServices portal and add them to the Company profile.",
        "POPIA s56; PAIA s17", "compliance:profile", "Open company profile",
    ),
    (
        "GOV-04", "governance", True,
        "Adopt a POPIA compliance framework and policy",
        "The IO must develop, implement, monitor and continuously improve a compliance framework. This app is that "
        "framework; the written 'POPIA Compliance Policy' documents it for staff and the Regulator.",
        "1. Generate the POPIA Compliance Policy from Documents.\n2. Review, sign and date it.\n"
        "3. Share it with staff and keep the signed copy.",
        "Regulation 4(1)(a) (amended 2025)", "compliance:documents", "Go to documents",
    ),
    (
        "GOV-05", "governance", True,
        "Do a personal information impact assessment",
        "The IO must ensure a personal information impact assessment is done – in plain terms: identify what could go "
        "wrong with the personal information you hold and decide what to do about it.",
        "1. Complete the Processing register first.\n2. Review the example risks in the Risk register, adjust scores, "
        "add your own and record controls.\n3. Repeat yearly or whenever you introduce a new system.",
        "Regulation 4(1)(b); POPIA s19(2)", "compliance:risk_list", "Open risk register",
    ),
    (
        "GOV-06", "governance", True,
        "Hold POPIA awareness training for staff",
        "Staff mistakes (phishing, wrong recipient, weak passwords) cause most breaches. The IO must run internal "
        "awareness sessions.",
        "1. Run a short session (30–60 min) using the Learn pages and your policy.\n"
        "2. Log date and attendees in Training.\n3. Repeat yearly and for every new employee.",
        "Regulation 4(1)(e)", "compliance:training_list", "Log training",
    ),
    (
        "GOV-07", "governance", True,
        "Schedule an annual compliance review",
        "POPIA compliance is ongoing. The 2025 amendments require the framework to be continuously improved.",
        "Keep the recurring tasks in Tasks & deadlines. Once a year re-walk this checklist and update evidence.",
        "Regulation 4(1)(a)", "compliance:task_list", "Open tasks",
    ),
    # ---------------- Lawful processing ----------------
    (
        "LAW-01", "lawful", True,
        "Map the personal information you process",
        "You can't protect what you don't know you have. The processing register lists each activity (payroll, "
        "recruitment, customer orders...), what information it uses, why, where it goes and how long you keep it.",
        "Review the draft entries in the Processing register, correct them, add missing activities and mark each Confirmed.",
        "POPIA s8, s17", "compliance:activity_list", "Open processing register",
    ),
    (
        "LAW-02", "lawful", True,
        "Have a lawful ground for each activity",
        "Processing is only lawful if one of the s11 grounds applies: consent, a contract with the person, a legal "
        "obligation, the person's legitimate interest, or your legitimate interest.",
        "Choose the lawful ground for each activity in the Processing register. Avoid relying on consent where "
        "another ground fits – consent can be withdrawn.",
        "POPIA s9, s11", "compliance:activity_list", "Open processing register",
    ),
    (
        "LAW-03", "lawful", True,
        "Collect only what you need (minimality)",
        "Information must be adequate, relevant and not excessive for the purpose.",
        "Review your forms (job applications, customer/supplier onboarding, visitor logs). Remove fields you don't "
        "use – e.g. ID numbers or marital status where not needed.",
        "POPIA s10", "", "",
    ),
    (
        "LAW-04", "lawful", False,
        "Collect information directly from the person where possible",
        "The default is to collect from the person themselves. Collecting elsewhere (e.g. reference or credit checks) "
        "needs a justification such as consent.",
        "Note the source of each activity in the Processing register. Get written consent for background checks.",
        "POPIA s12", "compliance:activity_list", "Open processing register",
    ),
    (
        "LAW-05", "lawful", True,
        "Define specific purposes",
        "You must collect for a specific, explicitly defined and lawful purpose related to your business.",
        "Fill in 'Why do you need it?' for every activity. These purposes feed straight into your privacy notices.",
        "POPIA s13", "compliance:activity_list", "Open processing register",
    ),
    (
        "LAW-06", "lawful", True,
        "Adopt a retention schedule and destroy old records",
        "Records may not be kept longer than necessary, unless a law requires it. After that they must be destroyed or "
        "de-identified so they cannot be reconstructed.",
        "1. Review the Retention schedule (it lists South African legal minimums).\n"
        "2. Set a retention period for each activity.\n3. Do the quarterly clean-up task.",
        "POPIA s14", "compliance:retention_list", "Open retention schedule",
    ),
    (
        "LAW-07", "lawful", False,
        "Check compatibility before reusing information for a new purpose",
        "Using information for a new purpose must be compatible with the original purpose (e.g. using staff photos in "
        "marketing is not).",
        "Before any new use, ask: would the person reasonably expect this? If not, get consent.",
        "POPIA s15", "", "",
    ),
    (
        "LAW-08", "lawful", False,
        "Keep proof of consent where you rely on it",
        "If consent is your lawful ground you must be able to prove it, and people may withdraw it at any time.",
        "Keep signed/recorded consents (e.g. biometric clock-in, health information). Record withdrawals.",
        "POPIA s11(2)", "", "",
    ),
    # ---------------- Openness & quality ----------------
    (
        "OPEN-01", "openness", True,
        "Give customers and suppliers a privacy notice",
        "When you collect information you must tell people who you are, what you collect, why, whether it's "
        "voluntary, who receives it, cross-border transfers and their rights.",
        "Generate the Privacy notice, publish it on your website and link to it in email signatures, quotes, invoices "
        "and onboarding forms.",
        "POPIA s18", "compliance:documents", "Go to documents",
    ),
    (
        "OPEN-02", "openness", True,
        "Give employees a privacy notice",
        "Employees are data subjects too. They must be told how their information (including health and banking "
        "details) is used.",
        "Generate the Employee privacy notice; have each employee acknowledge it (new hires at onboarding).",
        "POPIA s18", "compliance:documents", "Go to documents",
    ),
    (
        "OPEN-03", "openness", True,
        "Keep information accurate and up to date",
        "You must take reasonable steps to ensure information is complete, accurate and not misleading.",
        "E.g. ask employees yearly to confirm contact, bank and next-of-kin details; update supplier details on change.",
        "POPIA s16", "", "",
    ),
    (
        "OPEN-04", "openness", True,
        "Document all processing operations",
        "You must maintain documentation of all processing operations under your responsibility.",
        "The Processing register (with PDF/print export) is this documentation. Keep it current.",
        "POPIA s17", "compliance:activity_list", "Open processing register",
    ),
    # ---------------- Security ----------------
    (
        "SEC-01", "security", True,
        "Protect email and cloud accounts with MFA",
        "Most small-business breaches start with a stolen password. Multi-factor authentication stops the majority.",
        "Turn on MFA for email (Microsoft 365/Google), banking, payroll, accounting and this app. Use a password manager.",
        "POPIA s19", "", "",
    ),
    (
        "SEC-02", "security", True,
        "Encrypt laptops and phones",
        "A lost encrypted laptop is usually not a notifiable breach. An unencrypted one almost always is.",
        "Turn on BitLocker (Windows) or FileVault (Mac); set phone PIN/biometric lock; enable remote wipe.",
        "POPIA s19", "", "",
    ),
    (
        "SEC-03", "security", True,
        "Keep backups that ransomware can't reach",
        "You must be able to restore information and protect its integrity.",
        "Keep at least one backup offline or immutable; test a restore every quarter (see Tasks).",
        "POPIA s19", "compliance:task_list", "Open tasks",
    ),
    (
        "SEC-04", "security", True,
        "Patch systems and run anti-malware",
        "Unpatched software is a 'reasonably foreseeable' risk you must address.",
        "Enable automatic updates on all devices, routers and servers. Use built-in Defender or equivalent.",
        "POPIA s19(1)-(3)", "", "",
    ),
    (
        "SEC-05", "security", True,
        "Control who can access what",
        "Only people who need information for their job should have access (e.g. payroll and health information).",
        "Review user access quarterly; remove leavers on their last day; don't share accounts.",
        "POPIA s19", "compliance:task_list", "Open tasks",
    ),
    (
        "SEC-06", "security", False,
        "Secure paper records and dispose of them safely",
        "Security applies to paper too – HR files, CVs, signed forms.",
        "Lock cabinets, clean-desk habit, cross-cut shred or use a certified shredding service; wipe devices before disposal.",
        "POPIA s14(4), s19", "", "",
    ),
    (
        "SEC-07", "security", True,
        "Sign agreements with all operators (service providers)",
        "Anyone processing personal information for you (payroll bureau, IT support, cloud providers) must be bound by a "
        "written contract requiring confidentiality, security measures and breach notification to you.",
        "List providers in the Operators register. Accept their Data Processing Agreement or use the Operator agreement "
        "template from Documents.",
        "POPIA s20, s21", "compliance:operator_list", "Open operators",
    ),
    (
        "SEC-08", "security", True,
        "Bind staff to confidentiality",
        "Staff who handle personal information must treat it confidentially.",
        "Add a confidentiality/POPIA clause to employment contracts or have staff sign the policy acknowledgement.",
        "POPIA s20(b)", "", "",
    ),
    (
        "SEC-09", "security", True,
        "Have a breach response plan",
        "If there are reasonable grounds to believe personal information was accessed or acquired by an unauthorised "
        "person, you must notify the Regulator and the affected people as soon as reasonably possible. There is no "
        "'low risk' exemption like in Europe.",
        "Generate the Breach response plan. Log every incident (even suspected) in Incidents, which walks you through "
        "each step.",
        "POPIA s22", "compliance:incident_list", "Open incidents",
    ),
    (
        "SEC-10", "security", True,
        "Know how to report a breach on the eServices portal",
        "Since 1 April 2025 security compromises must be reported to the Regulator via the eServices portal (form SCN1), "
        "not by email.",
        "Create your eServices profile now (same as GOV-02) so you're not doing it for the first time during a crisis.",
        "POPIA s22; Regulator notice 2025", "", "",
    ),
    # ---------------- Rights ----------------
    (
        "RIGHTS-01", "rights", True,
        "Be ready to answer access requests within 30 days",
        "People may ask whether you hold their information and for a copy of it. Under PAIA a private body must decide "
        "within 30 days (extendable once by 30 days with notice).",
        "Log every request in Requests; the app calculates the deadline and warns you before it expires.",
        "POPIA s23; PAIA s50, s56, s57", "compliance:request_list", "Open requests",
    ),
    (
        "RIGHTS-02", "rights", True,
        "Handle correction and deletion requests",
        "People may ask you to correct or delete information that is inaccurate, excessive, out of date or unlawfully "
        "obtained (Form 2 or similar).",
        "Log it, check it, correct/delete or give reasons for refusing, and notify the requester.",
        "POPIA s24; Regulation 3", "compliance:request_list", "Open requests",
    ),
    (
        "RIGHTS-03", "rights", True,
        "Handle objections",
        "People may object to processing based on legitimate interest, and to direct marketing, at any time. Since April "
        "2025 objections can arrive by email, SMS, WhatsApp or phone, and must be free of charge.",
        "Log objections; stop the processing unless legislation requires it to continue.",
        "POPIA s11(3)-(4); Regulation 2 (amended)", "compliance:request_list", "Open requests",
    ),
    (
        "RIGHTS-04", "rights", True,
        "Verify identity before disclosing information",
        "Sending someone's information to an impostor is itself a breach.",
        "Ask for adequate proof of identity (e.g. call back on the number you have on file) before releasing information.",
        "POPIA s23(1)", "", "",
    ),
    # ---------------- Special ----------------
    (
        "SPEC-01", "special", True,
        "Identify special personal information",
        "Health, biometrics, race/ethnicity, religion, trade union membership, political views, sex life and criminal "
        "behaviour are prohibited from processing unless an exception in POPIA applies.",
        "Tick 'special personal information' on each relevant activity in the Processing register and document the "
        "authorisation you rely on.",
        "POPIA s26, s27", "compliance:activity_list", "Open processing register",
    ),
    (
        "SPEC-02", "special", True,
        "Handle employee health information correctly",
        "Employers may process health information (sick notes, medical aid, occupational health) where needed to meet "
        "legal duties or employment policies, under a duty of confidentiality. The Health Information Regulations "
        "(in force 6 March 2026) now expressly cover employers.",
        "Restrict sick notes and medical records to HR/management; keep them separate from the general personnel file; "
        "ensure staff handling them are bound to confidentiality; mention it in the Employee privacy notice.",
        "POPIA s27, s32; Health Information Regulations 2026", "", "",
    ),
    (
        "SPEC-03", "special", False,
        "Get consent for biometrics (fingerprint/face clocking or access)",
        "Biometric information is special personal information. The usual basis is the employee's explicit consent – "
        "offer an alternative (card/PIN) for those who refuse.",
        "If you use biometric devices: collect written consent before enrolment; otherwise mark Not applicable.",
        "POPIA s26, s27(1)(a)", "", "",
    ),
    (
        "SPEC-04", "special", False,
        "Limit race information to Employment Equity purposes",
        "Race may be processed where required by law, e.g. for Employment Equity reporting by designated employers.",
        "Only collect race if you are a designated employer (or for B-BBEE) and say so in the employee notice.",
        "POPIA s29", "", "",
    ),
    (
        "SPEC-05", "special", False,
        "Criminal and credit checks on applicants",
        "Criminal behaviour information is special personal information; credit checks involve third-party sources.",
        "Only check where the role justifies it, with the applicant's written consent, and keep results confidential.",
        "POPIA s12, s26, s33", "", "",
    ),
    (
        "SPEC-06", "special", True,
        "Protect children's information",
        "Information about children (under 18) – e.g. employees' dependants on medical aid – may only be processed with "
        "a competent person's consent or another s35 exception.",
        "Collect dependant details only where needed (medical aid/benefits) and via the parent-employee.",
        "POPIA s34, s35", "", "",
    ),
    (
        "SPEC-07", "special", True,
        "Document cross-border transfers",
        "Using overseas cloud services (Microsoft 365, Google Workspace, Dropbox, Hetzner...) means personal information "
        "leaves South Africa. That is allowed only on a s72 ground – usually that the recipient is bound by law or an "
        "agreement giving adequate protection (e.g. EU GDPR).",
        "For each operator record where data is stored and the s72 basis. Mention transfers in your privacy notices.",
        "POPIA s72", "compliance:operator_list", "Open operators",
    ),
    (
        "SPEC-08", "special", False,
        "Confirm you don't need prior authorisation",
        "Certain processing needs the Regulator's approval before it starts: credit reporting, processing criminal/"
        "objectionable conduct on behalf of third parties, linking unique identifiers across organisations for new "
        "purposes, or sending special/children's information to countries without adequate protection.",
        "Most small businesses do none of these – confirm and mark Not applicable with a short explanation.",
        "POPIA s57, s58", "", "",
    ),
    # ---------------- Marketing ----------------
    (
        "MKT-01", "marketing", False,
        "Only send electronic marketing with consent or to existing customers",
        "Email/SMS/WhatsApp/phone marketing needs opt-in consent (form substantially similar to Form 4, free of charge – "
        "an opt-out is not consent), unless the person is an existing customer who bought similar products and was given "
        "a chance to opt out. Every message must include an opt-out.",
        "If you don't do marketing, mark Not applicable. Otherwise keep consent records and include an unsubscribe option.",
        "POPIA s69; Regulation 6 (amended 2025); Guidance Note on Direct Marketing", "", "",
    ),
    (
        "MKT-02", "marketing", False,
        "Keep a do-not-contact list",
        "Opt-outs must be honoured across all channels and lists.",
        "Log opt-outs in Requests (type 'Stop direct marketing') and suppress them in your mailing tool.",
        "POPIA s11(3)(b), s69", "compliance:request_list", "Open requests",
    ),
    (
        "MKT-03", "marketing", False,
        "No decisions based solely on automated processing",
        "People may not be subject to decisions with legal effect based solely on automated profiling, unless safeguards apply.",
        "Most small businesses don't do this – mark Not applicable if so.",
        "POPIA s71", "", "",
    ),
    # ---------------- PAIA ----------------
    (
        "PAIA-01", "paia", True,
        "Compile and publish a PAIA manual",
        "Every private body – including sole proprietors and small companies – must have a PAIA manual describing the "
        "records it holds and how to request them. The small-business exemption ended in 2021.",
        "Generate the PAIA manual, review it, publish it on your website and keep a copy at your premises.",
        "PAIA s51", "compliance:documents", "Go to documents",
    ),
    (
        "PAIA-02", "paia", True,
        "Submit the annual PAIA report (1 April – 30 June)",
        "The Regulator requires every private body to submit an annual report on access requests via the eServices "
        "portal between 1 April and 30 June, covering 1 April to 31 March. Submit it even if you received no requests.",
        "Use the PAIA report page in this app to get the figures, then submit on the eServices portal.",
        "PAIA s83(4)", "compliance:paia_report", "Open PAIA report",
    ),
    (
        "PAIA-03", "paia", False,
        "Keep the PAIA manual up to date",
        "The manual must be updated whenever something material changes (address, IO, new record categories).",
        "Review it yearly with the annual compliance review.",
        "PAIA s51(2)", "compliance:task_list", "Open tasks",
    ),
]


RETENTION_RULES = [
    # (record_type, examples, period, starts_from, legal_source, kind)
    ("Basic employment records", "Name, occupation, time worked, remuneration, date of birth", "3 years",
     "Date of last entry", "Basic Conditions of Employment Act 75 of 1997, s31", "statutory"),
    ("Disciplinary records", "Transgressions, sanctions, reasons", "3 years", "Date of the record",
     "Labour Relations Act 66 of 1995, s205", "statutory"),
    ("UIF records", "Remuneration, UIF contributions, employee details", "5 years", "Date of the record",
     "Unemployment Insurance Act 63 of 2001", "statutory"),
    ("COIDA earnings records", "Wages, time worked, piece-work, overtime", "4 years", "Date of the record",
     "Compensation for Occupational Injuries and Diseases Act 130 of 1993", "statutory"),
    ("Tax records", "Payroll/PAYE, IRP5s, invoices, VAT records, tax returns and supporting documents", "5 years",
     "Date the related tax return was submitted", "Tax Administration Act 28 of 2011, s29 & s32", "statutory"),
    ("Company accounting records", "Accounting records, annual financial statements, minutes, resolutions", "7 years",
     "Date of the record", "Companies Act 71 of 2008, s24", "statutory"),
    ("Company founding records", "MOI, registration certificate, securities register", "Indefinitely",
     "Life of the company", "Companies Act 71 of 2008, s24 & s50", "statutory"),
    ("Health & safety incident records", "Incident registers and reports", "3 years", "Date of the record",
     "OHS Act General Administrative Regulations", "statutory"),
    ("Personnel file after employment ends", "Contract, performance reviews, leave records", "5 years",
     "Last day of employment", "Policy – covers UIF/tax periods and possible disputes (POPIA s14)", "policy"),
    ("Unsuccessful job applications", "CVs, interview notes, assessments", "6 months",
     "Date the position is filled", "Policy – matches the 6-month period for discrimination disputes (EEA s10); longer only with consent", "policy"),
    ("Customer & supplier contact details", "Contact person names, emails, phone numbers", "Duration of relationship + 5 years",
     "End of the relationship", "Policy – aligned to tax record period (POPIA s14)", "policy"),
    ("Consent records", "Biometric, health, marketing or background-check consents", "Duration of processing + 3 years",
     "Withdrawal of consent or end of processing", "Policy – Prescription Act 68 of 1969 (3-year claims)", "policy"),
    ("Data subject & PAIA requests", "Requests, correspondence, decisions", "5 years", "Date request closed",
     "Policy – evidence for PAIA reports and complaints", "policy"),
    ("Security incident records", "Incident log, investigation, notifications", "5 years", "Date incident closed",
     "Policy – accountability evidence (POPIA s8, s22)", "policy"),
]


OPERATORS = [
    # (name, service, personal_info, location, outside_sa, basis, notes)
    ("Hetzner Online GmbH", "Hosts this POPIA compliance app (if you deploy it on Hetzner)",
     "Compliance records: requester names/contacts, incident details, staff names in training logs",
     "Germany or Finland (EU) – check your server's location in the Hetzner console", True, "adequate",
     "Hetzner is bound by the EU GDPR. Accept Hetzner's Data Processing Agreement (Hetzner Console → Account → DPA) "
     "and file it. If you run the app on your own computer instead, delete this entry."),
    ("Email & document storage provider", "Email, calendar and file storage (e.g. Microsoft 365 or Google Workspace)",
     "All information in emails and files: staff, customer and supplier details, CVs, invoices",
     "Usually EU, US or South Africa – check your admin console", True, "adequate",
     "Rename to your actual provider. Their online Data Protection Addendum usually satisfies s21 and s72."),
    ("Payroll / accounting software", "Payroll, invoicing, bookkeeping (e.g. Sage, Xero, SimplePay)",
     "Employee ID numbers, tax numbers, salaries, bank details; customer/supplier billing details",
     "Check with provider", False, "unknown",
     "Rename to your actual provider. Check where data is hosted and whether their terms include a DPA."),
    ("External accountant / bookkeeper", "Prepares tax returns, payroll or financial statements",
     "Employee payroll information, customer/supplier financial records", "South Africa", False, "local",
     "Accountants are usually operators when they process payroll for you – sign an operator agreement or confidentiality clause."),
    ("IT support provider", "Maintains computers, networks and accounts", "Potentially access to all systems",
     "South Africa", False, "local", "Rename or delete if you don't use one."),
]


ACTIVITIES = [
    {
        "name": "Employee administration & payroll",
        "data_subjects": "Employees and contractors (and their dependants)",
        "personal_info": "Name, ID/passport number, contact details, address, next of kin, bank details, tax number, "
                         "salary and deductions, leave records, performance and disciplinary records, qualifications",
        "purpose": "Managing the employment relationship, paying salaries, meeting tax, UIF, COIDA and labour-law "
                   "obligations, administering benefits (medical aid, pension/provident fund)",
        "lawful_basis": "contract",
        "lawful_basis_notes": "Employment contract; also legal obligations under BCEA, Income Tax Act, UIF Act, COIDA",
        "source": "Directly from the employee",
        "special_info": True,
        "special_info_details": "Health (sick notes, medical aid, incapacity) – s27(1)(b)/s32 employer exception; race only if "
                                "Employment Equity designated employer (s29). Biometrics only with consent (s27(1)(a)).",
        "children_info": True,
        "recipients": "SARS, Department of Employment and Labour (UIF/COIDA), medical aid and retirement fund "
                      "administrators, bank, auditors/accountant",
        "cross_border": True,
        "retention": "Basic records 3 years; tax/UIF records 5 years; personnel file 5 years after employment ends",
        "security_measures": "Payroll system with individual logins and MFA; HR files in locked cabinet; health "
                             "records kept separately with restricted access",
        "operators": ["Payroll / accounting software", "Email & document storage provider", "External accountant / bookkeeper"],
    },
    {
        "name": "Recruitment",
        "data_subjects": "Job applicants",
        "personal_info": "CV details, contact details, qualifications, work history, references, interview notes; "
                         "criminal/credit check results where applicable",
        "purpose": "Evaluating candidates for vacancies",
        "lawful_basis": "legit_interest",
        "lawful_basis_notes": "Pre-contractual steps at applicant's request; consent for criminal/credit checks",
        "source": "Directly from applicants; referees and verification agencies with consent",
        "special_info": False,
        "special_info_details": "",
        "children_info": False,
        "recipients": "Interviewing managers; background screening agency (if used)",
        "cross_border": True,
        "retention": "6 months after position filled unless candidate consents to longer",
        "security_measures": "CVs stored in a restricted folder; paper CVs shredded after retention period",
        "operators": ["Email & document storage provider"],
    },
    {
        "name": "Customers & suppliers – orders, invoicing and payments",
        "data_subjects": "Customers and suppliers (companies are also protected), and their contact persons",
        "personal_info": "Company names, registration and VAT numbers, contact person names, job titles, emails, "
                         "phone numbers, delivery and billing addresses, bank details, order and payment history",
        "purpose": "Quoting, supplying and buying goods/services, invoicing, paying and collecting payment, "
                   "keeping accounting and tax records",
        "lawful_basis": "contract",
        "lawful_basis_notes": "Contract with the customer/supplier; Tax Administration Act and Companies Act record-keeping",
        "source": "Directly from customers and suppliers",
        "special_info": False,
        "special_info_details": "",
        "children_info": False,
        "recipients": "Bank, couriers, auditors/accountant, SARS (on audit)",
        "cross_border": True,
        "retention": "Duration of relationship + 5 years; accounting records 7 years",
        "security_measures": "Accounting system with individual logins and MFA; email with MFA",
        "operators": ["Payroll / accounting software", "Email & document storage provider"],
    },
]


RISKS = [
    # (title, description, likelihood, impact, mitigation)
    ("Phishing / hacked email account", "An attacker steals a password and reads or forwards email containing staff, "
     "customer or banking details, or changes bank details on invoices.", 4, 4,
     "MFA on all email accounts; staff phishing awareness; verify bank detail changes by phone."),
    ("Lost or stolen laptop or phone", "A device with company email and files is lost or stolen.", 3, 4,
     "Full-disk encryption (BitLocker/FileVault); screen lock; remote wipe; no local copies of HR files."),
    ("Ransomware", "Malware encrypts or steals files, making records unavailable or leaking them.", 3, 5,
     "Automatic updates; anti-malware; offline/immutable backups tested quarterly; least-privilege accounts."),
    ("Email sent to the wrong person", "Payslips, CVs or customer details emailed to the wrong recipient.", 3, 3,
     "Disable email address auto-complete for sensitive mail; password-protect payslips; double-check before sending."),
    ("Breach at a service provider", "A payroll, cloud or IT provider suffers a breach affecting your data.", 2, 4,
     "Operator agreements requiring breach notification; choose reputable providers; review yearly."),
    ("Keeping records longer than necessary", "Old CVs, ex-employee files and customer data pile up, increasing "
     "the impact of any breach.", 4, 2, "Retention schedule; quarterly clean-up task."),
    ("Unauthorised access to employee health information", "Sick notes or medical information seen by staff who "
     "don't need them.", 2, 4, "Keep health records separate with restricted access; confidentiality undertakings."),
    ("Overseas storage without documented safeguards", "Cloud services store data abroad without a documented s72 basis.",
     3, 3, "Record every operator's data location and s72 basis; accept providers' data protection addenda."),
]


def seed_tasks(today):
    """Return (title, details, due_date, recurrence, link) for the default compliance calendar."""
    from datetime import date, timedelta

    from .models import add_months

    june_30 = date(today.year, 6, 30)
    if june_30 < today:
        june_30 = date(today.year + 1, 6, 30)
    return [
        ("Submit PAIA annual report on the eServices portal",
         "Window opens 1 April and closes 30 June. Covers 1 April – 31 March. Use the PAIA report page for the figures.",
         june_30, "yearly", "compliance:paia_report"),
        ("Annual POPIA compliance review",
         "Re-walk the checklist, confirm the processing register, operators and risks are current, and update policies.",
         add_months(today, 12), "yearly", "compliance:checklist"),
        ("Staff POPIA awareness training",
         "Run a short awareness session and log attendees.", today + timedelta(days=60), "yearly", "compliance:training_list"),
        ("Review PAIA manual and privacy notices",
         "Update if contact details, the Information Officer or your processing changed. Re-publish on the website.",
         add_months(today, 12), "yearly", "compliance:documents"),
        ("Review operators and cross-border transfers",
         "Check each provider still has an agreement and a documented s72 basis.", add_months(today, 12), "yearly",
         "compliance:operator_list"),
        ("Records clean-up: destroy records past retention",
         "Use the retention schedule. Shred paper and delete electronic records (incl. old email attachments).",
         add_months(today, 3), "quarterly", "compliance:retention_list"),
        ("Review user access to systems",
         "Remove leavers, check who can see payroll and HR files, confirm MFA is on everywhere.",
         add_months(today, 3), "quarterly", ""),
        ("Test restoring a backup",
         "Restore a file (and this app's database) from backup to prove backups work.", add_months(today, 3), "quarterly", ""),
    ]
