# System Architecture Diagram - AttendSmart

The following architecture diagram illustrates the overall system design, components, modules, and their interactions for the AttendSmart platform.

```mermaid
graph TD
    %% Define styles
    classDef edge fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef cloud fill:#eef2ff,stroke:#4f46e5,stroke-width:2px;
    classDef db fill:#f0fdf4,stroke:#16a34a,stroke-width:2px;
    classDef ui fill:#fff7ed,stroke:#ea580c,stroke-width:2px;

    subgraph "Edge / Client Layer"
        BD[Biometric Devices]:::edge
        RFID[RFID Scanners]:::edge
        WA[Web Application / UI]:::ui
        MA[Mobile Application]:::ui
    end

    subgraph "AttendSmart Cloud Architecture (Backend)"
        AG[API Gateway / Load Balancer]:::cloud
        AUTH[Authentication Service]:::cloud
        
        KS[Kafka Event Stream / Ingestion]:::cloud
        
        VE[Attendance Validation Engine]:::cloud
        RE[Reporting & Analytics Engine]:::cloud
        NS[Notification Service]:::cloud
        
        VE -- "Validates Rules (Status, Duplicates, Time)" --> RE
    end

    subgraph "Data Storage Layer"
        RDB[(Relational DB: PostgreSQL\nUsers, Schedules, Core Data)]:::db
        TSDB[(NoSQL: Cassandra\nHigh-Volume Log Streams)]:::db
        CACHE[(Redis Cache\nSession & Duplicate Checks)]:::db
    end

    %% Flow connections
    BD -->|Scan Data| AG
    RFID -->|Badge Data| AG
    WA -->|Admin Requests| AG
    MA -->|Teacher Requests| AG

    AG --> AUTH
    AUTH -->|Authenticated| KS
    
    KS -->|Raw Events| VE
    VE -->|Valid Event| TSDB
    VE <-->|Check Duplicates| CACHE
    
    RE <--> RDB
    RE <--> TSDB
    
    VE -->|Triggers Alert| NS
    NS -->|SMS/Email| Parents/Students

```

## Interaction Summary
1. **Edge Devices** (Biometric/RFID) and **Faculty Web Portals** continuously push scan events to the **API Gateway**.
2. The Gateway authenticates the request and queues the event in the **Event Stream** to handle millions of concurrent updates smoothly.
3. The **Validation Engine** pulls events, verifies temporal bounds (class schedule), and checks **Redis** to prevent immediate duplicate scans.
4. Validated data is committed to the **NoSQL Database** (for massive scale).
5. The **Reporting Engine** aggregates data for the Dashboard UI, querying both NoSQL and PostgreSQL.
6. The **Notification Service** dispatches real-time alerts if a student is flagged as absent, late, or falling below compliance thresholds.
