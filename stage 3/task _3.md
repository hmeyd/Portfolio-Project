### Recherche d'une entreprise par son SIREN

@startuml
actor User
participant "Frontend" as FE
participant "Backend API" as BE
participant "API SIRENE" as SIRENE

User -> FE : entrer SIREN
FE -> BE : GET /api/company?siren=XXXX
BE -> SIRENE : GET données SIREN
SIRENE --> BE : JSON entreprise
BE --> FE : JSON réponse entreprise
FE --> User : afficher infos entreprise
@enduml

### Téléchargement de documents BODACC

@startuml
actor User
participant "Frontend" as FE
participant "Backend API" as BE
participant "API BODACC" as BODACC

User -> FE : clique "Voir documents"
FE -> BE : GET /api/company/documents?siren=XXXX
BE -> BODACC : GET documents JSON/PDF
BODACC --> BE : liste documents
BE --> FE : JSON liste de documents
FE --> User : afficher / télécharger documents
@enduml

### Comparaison de deux entreprises

@startuml
actor User
participant "Frontend" as FE
participant "Backend API" as BE
participant "API SIRENE" as SIRENE1
participant "API SIRENE" as SIRENE2

User -> FE : entrer siren1 et siren2
FE -> BE : GET /api/compare?siren1=XXX&siren2=YYY
BE -> SIRENE1 : GET siren1
SIRENE1 --> BE : JSON entreprise1
BE -> SIRENE2 : GET siren2
SIRENE2 --> BE : JSON entreprise2
BE --> FE : données comparatives
FE --> User : afficher tableau comparatif
@enduml

