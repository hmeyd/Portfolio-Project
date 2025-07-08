### **Project Charter – Stage 2**

**Project:** Enterprise Platform
**Program:** Holberton School
**Partner:** Crédit Agricole

**Project Team:** Ahmed H’ymed, Myriam Guillabert, Madjiguene Elodie Mbaye, Mame Penda Sadio
**Date:** May 2025

---

### 0. Define Project Objectives

The objective of this project is to facilitate access to reliable and centralized information about French companies using open data. It meets the needs of users (entrepreneurs, companies, analysts) to quickly obtain identification, activity, and structural data about a company.

**SMART Objectives**

1. Create a platform capable of searching for a company by its name or SIREN/SIRET number.

2. Display at least 5 key data points about the company (Company name, SIREN, Start date of activity, Nature of the company, Legal form, APE/NAF code – Main activity, Share capital).

3. Implement and automatically retrieve data via the Sirene API.

---

### 1. Identify Stakeholders and Team Roles

**Stakeholders**

| Type     | Name/Description                                |
| -------- | ----------------------------------------------- |
| Internal | Holberton project team (4 members)              |
| Internal | Holberton instructors / educational advisors    |
| External | Olivier Matz – Crédit Agricole tutor            |
| External | CA employees & professional clients (end users) |

**Team Roles**

| Role                 | Assigned Person   | Main Responsibilities                           |
| -------------------- | ----------------- | ----------------------------------------------- |
| Project Manager      | Ahmed H’ymed      | Organization, planning, progress tracking       |
| Backend Developer    | Myriam Guillabert | API connection, data retrieval and structuring  |
| Frontend Developer   | Elodie Mbaye      | Creating a simple interface to display the data |
| Documentation Writer | Mame Penda Sadio  | Technical and user documentation                |

---

### 2. Define Scope

**In-Scope**

* Company search by name or SIREN/SIRET.
* Connection to one or more public APIs (Sirene API).
* Retrieval and display of key information: name, address, main activity, creation date, legal status.
* Simple presentation via command line or minimalist web page.

**Out-of-Scope**

* Complex features like financial analysis or graphical visualization.
* Integration of private or paid databases.
* User authentication or personal dashboard.

---

### 3. Identify Risks

| Identified Risk                                          | Potential Impact                      | Mitigation Strategy                                                              |
| -------------------------------------------------------- | ------------------------------------- | -------------------------------------------------------------------------------- |
| Sirene API unavailable or unstable                       | Inability to retrieve real-time data  | Prepare a local open data backup dataset to use offline in case of API failure   |
| Difficulty filtering complex data (sector, region, size) | Poor UX, non-functional filters       | Limit filters to 2–3 simple criteria initially; improve iteratively              |
| Incomplete or inconsistent data                          | Incorrect display, loss of user trust | Add checks for key fields + clearly display ‘Data not available’                 |
| Short deadlines, workload overload                       | Delays, incomplete MVP                | Prioritize essential features (strict MVP), divide tasks by specialty            |
| GDPR compliance issues                                   | Risks for Crédit Agricole             | Do not store any sensitive personal data; stick to 100% public data (RNE/Sirene) |
| Technical difficulty implementing frontend               | Limited or non-intuitive presentation | Focus first on a simple display (HTML table or CLI), improve if time allows      |

---

### 4. Develop a High-Level Plan

| Project Phase                       | Estimated Period | Main Objectives                                   |
| ----------------------------------- | ---------------- | ------------------------------------------------- |
| Phase 1 – Analysis & Design         | Week 1           | Understand needs, study APIs, define endpoints    |
| Phase 2 – MVP Development           | Weeks 2–3        | API connection, JSON processing, data display     |
| Phase 3 – User Interface (optional) | Week 4           | Simple frontend or terminal integration           |
| Phase 4 – Testing & Documentation   | Week 5           | Unit tests, error handling, documentation writing |
| Phase 5 – Final Presentation        | Week 6           | Demo preparation, final report, oral presentation |

---
