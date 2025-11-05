# Architecture Diagrams
## Airborne Radar Target Behavior Analysis System

**Document Version:** 1.0  
**Date:** November 5, 2025  
**Supplementary to:** TECHNICAL_PROPOSAL.md

---

## Table of Contents

1. [System Architecture Diagrams](#1-system-architecture-diagrams)
2. [Sequence Diagrams](#2-sequence-diagrams)
3. [State Machine Diagrams](#3-state-machine-diagrams)
4. [Component Interaction Diagrams](#4-component-interaction-diagrams)
5. [Data Model Diagrams](#5-data-model-diagrams)

---

## 1. System Architecture Diagrams

### 1.1 Layer Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI1[PyQt5 GUI<br/>main_window.py]
        UI2[CLI Interface<br/>main.py]
    end
    
    subgraph "Application Service Layer"
        SVC1[Configuration Service<br/>config loader]
        SVC2[Logging Service<br/>logging system]
        SVC3[File Management<br/>I/O handlers]
    end
    
    subgraph "Business Logic Layer"
        BL1[Data Loader<br/>data_loader.py]
        BL2[Feature Extractor<br/>feature_extractor.py]
        BL3[Tagging Engine<br/>tagging_engine.py]
        BL4[Synthetic Generator<br/>synthetic_generator.py]
        BL5[External Interface<br/>external_interface.py]
    end
    
    subgraph "Data Access Layer"
        DAL1[Binary File Handler]
        DAL2[HDF5 File Handler]
        DAL3[JSON Handler]
        DAL4[Memory Cache]
    end
    
    subgraph "External Systems"
        EXT1[C++ Libraries<br/>.so, .dll]
        EXT2[MATLAB Engine]
        EXT3[File System]
    end
    
    UI1 --> SVC1
    UI1 --> SVC2
    UI2 --> SVC1
    UI2 --> SVC2
    
    SVC1 --> BL1
    SVC1 --> BL2
    SVC1 --> BL3
    SVC1 --> BL4
    SVC1 --> BL5
    
    BL1 --> DAL1
    BL1 --> DAL2
    BL2 --> DAL4
    BL3 --> DAL4
    BL4 --> DAL2
    BL5 --> EXT1
    BL5 --> EXT2
    
    DAL1 --> EXT3
    DAL2 --> EXT3
    DAL3 --> EXT3
```

### 1.2 Component Dependency Graph

```mermaid
graph TD
    MAIN[main.py] --> DL[RadarDataLoader]
    MAIN --> FE[FeatureExtractor]
    MAIN --> TE[TaggingEngine]
    MAIN --> SG[SyntheticDataGenerator]
    
    GUI[gui/main_window.py] --> DL
    GUI --> FE
    GUI --> TE
    GUI --> SG
    
    FE --> DL
    TE --> FE
    EI[ExternalInterface] --> FE
    
    DL -.uses.-> NP[NumPy]
    DL -.uses.-> H5[h5py]
    
    FE -.uses.-> NP
    FE -.uses.-> SP[SciPy]
    FE -.uses.-> SK[scikit-learn]
    
    TE -.uses.-> NP
    
    SG -.uses.-> NP
    SG -.uses.-> SP
    SG -.uses.-> H5
    
    EI -.uses.-> CT[ctypes]
    EI -.uses.-> ML[MATLAB Engine]
    
    GUI -.uses.-> PQ[PyQt5]
    GUI -.uses.-> MPL[Matplotlib]
```

### 1.3 Deployment View

```mermaid
graph TB
    subgraph "User's Computer"
        subgraph "Python Environment"
            APP[Radar Analyzer<br/>Application]
            LIB[Python Libraries<br/>NumPy, SciPy, etc.]
        end
        
        subgraph "File System"
            CFG[Configuration<br/>YAML files]
            DATA[Data Files<br/>Binary/HDF5]
            LOG[Log Files]
            RESULTS[Output Files<br/>JSON/HDF5]
        end
        
        subgraph "Optional External"
            CPP[C++ Libraries<br/>.so, .dll]
            MATLAB[MATLAB Engine]
        end
    end
    
    subgraph "User Interface"
        DESKTOP[Desktop Display]
        TERMINAL[Command Terminal]
    end
    
    APP --> CFG
    APP --> DATA
    APP --> LOG
    APP --> RESULTS
    APP -.optional.-> CPP
    APP -.optional.-> MATLAB
    APP --> LIB
    
    APP --> DESKTOP
    APP --> TERMINAL
```

---

## 2. Sequence Diagrams

### 2.1 Complete Analysis Workflow

```mermaid
sequenceDiagram
    actor User
    participant GUI as GUI Application
    participant DL as Data Loader
    participant FE as Feature Extractor
    participant EI as External Interface
    participant TE as Tagging Engine
    participant FS as File System
    
    User->>GUI: Load File
    GUI->>DL: load_file(filepath)
    DL->>FS: Open file
    FS-->>DL: File handle
    DL->>DL: Parse header
    DL->>DL: Extract data
    DL-->>GUI: data dictionary
    GUI->>GUI: Display data info
    
    User->>GUI: Click "Analyze"
    GUI->>FE: extract_all_features(data)
    
    FE->>EI: Check external algorithms
    alt External Available
        EI->>EI: Use C++/MATLAB
        EI-->>FE: Processed data
    else Use Python
        FE->>FE: Python processing
    end
    
    FE->>FE: Extract velocity features
    FE->>FE: Extract trajectory features
    FE->>FE: Extract acceleration features
    FE->>FE: Extract Doppler features
    FE->>FE: Extract RCS features
    FE-->>GUI: features dictionary
    
    GUI->>TE: tag_target(features)
    TE->>TE: Apply speed rules
    TE->>TE: Apply maneuver rules
    TE->>TE: Apply profile rules
    TE-->>GUI: tags list
    
    GUI->>TE: generate_report(features, tags)
    TE-->>GUI: formatted report
    
    GUI->>GUI: Display results
    GUI->>User: Show report & visualization
    
    User->>GUI: Export Results
    GUI->>TE: export_tags(features, tags, filepath)
    TE->>FS: Write JSON file
    FS-->>TE: Success
    TE-->>GUI: Export complete
    GUI->>User: Confirmation
```

### 2.2 Synthetic Data Generation Sequence

```mermaid
sequenceDiagram
    actor User
    participant GUI as GUI
    participant SG as Synthetic Generator
    participant FS as File System
    
    User->>GUI: Click "Generate Synthetic Data"
    GUI->>User: Request parameters
    User->>GUI: Set num_targets=10, duration=60s
    
    GUI->>SG: generate_dataset(config)
    
    loop For each target (1 to 10)
        SG->>SG: Select random behavior
        SG->>SG: generate_trajectory(behavior)
        Note over SG: Creates position array
        
        SG->>SG: Calculate velocity
        Note over SG: Differentiate position
        
        SG->>SG: Calculate acceleration
        Note over SG: Differentiate velocity
        
        SG->>SG: generate_radar_returns(position)
        Note over SG: Simulate IQ data
        
        SG->>SG: generate_doppler_spectrum(velocity)
        Note over SG: FFT of returns
        
        SG->>SG: add_noise(data)
        Note over SG: Realistic noise injection
        
        SG->>SG: Create ground truth labels
    end
    
    SG-->>GUI: dataset (list of 10 targets)
    
    User->>GUI: Save Dataset
    GUI->>SG: save_synthetic_dataset(dataset, output_dir)
    
    loop For each target in dataset
        SG->>FS: Create HDF5 file
        SG->>FS: Write position data
        SG->>FS: Write velocity data
        SG->>FS: Write raw_data (IQ)
        SG->>FS: Write doppler spectrum
        SG->>FS: Write metadata & labels
        FS-->>SG: File saved
    end
    
    SG-->>GUI: Save complete
    GUI->>User: Show success message
```

### 2.3 Batch Processing Sequence

```mermaid
sequenceDiagram
    actor User
    participant CLI as Command Line
    participant MAIN as Main Controller
    participant DL as Data Loader
    participant FE as Feature Extractor
    participant TE as Tagging Engine
    participant FS as File System
    
    User->>CLI: radar-analyzer batch -i input/ -o output/
    CLI->>MAIN: batch_analysis(input_dir, output_dir)
    
    MAIN->>FS: Scan directory
    FS-->>MAIN: file_list [file1, file2, ..., fileN]
    
    MAIN->>User: Found N files to process
    
    loop For each file in file_list
        MAIN->>DL: load_file(file)
        DL->>FS: Read file
        FS-->>DL: Raw data
        DL-->>MAIN: data dict
        
        MAIN->>FE: extract_all_features(data)
        FE-->>MAIN: features dict
        
        MAIN->>TE: tag_target(features)
        TE-->>MAIN: tags list
        
        MAIN->>TE: generate_report(features, tags)
        TE-->>MAIN: report text
        
        MAIN->>FS: Save individual report
        FS-->>MAIN: Report saved
        
        MAIN->>User: Progress: X/N files completed
    end
    
    MAIN->>TE: export_tags(all_features, all_tags, combined.json)
    TE->>FS: Write combined results
    FS-->>TE: Success
    
    MAIN->>User: Batch processing complete!
```

### 2.4 External Algorithm Integration

```mermaid
sequenceDiagram
    participant APP as Application
    participant EI as External Interface
    participant CPP as C++ Library
    participant MAT as MATLAB Engine
    participant PY as Python Fallback
    
    APP->>EI: Initialize external_interface
    EI->>EI: load_config()
    
    alt C++ Library Configured
        EI->>CPP: Load library (cpp_lib_path)
        alt Load Success
            CPP-->>EI: Library handle
            EI->>EI: Register function pointers
        else Load Failure
            CPP-->>EI: Error
            EI->>EI: Set fallback flag
        end
    end
    
    alt MATLAB Configured
        EI->>MAT: Start MATLAB engine
        alt Engine Start Success
            MAT-->>EI: Engine handle
        else Engine Start Failure
            MAT-->>EI: Error
            EI->>EI: Set fallback flag
        end
    end
    
    APP->>EI: call_algorithm("doppler_analysis", data)
    
    alt C++ Available
        EI->>CPP: Call doppler_analysis_cpp(data)
        CPP->>CPP: Process with C++
        CPP-->>EI: Results
    else MATLAB Available
        EI->>MAT: feval("doppler_analysis", data)
        MAT->>MAT: Process with MATLAB
        MAT-->>EI: Results
    else Use Fallback
        EI->>PY: doppler_analysis_python(data)
        PY->>PY: Process with NumPy/SciPy
        PY-->>EI: Results
    end
    
    EI-->>APP: Processed results
```

---

## 3. State Machine Diagrams

### 3.1 GUI Application State Machine

```mermaid
stateDiagram-v2
    [*] --> Initializing
    
    Initializing --> Ready: Setup Complete
    
    Ready --> LoadingData: User Loads File
    LoadingData --> DataLoaded: Load Success
    LoadingData --> Error: Load Failure
    DataLoaded --> Ready: View Data
    
    DataLoaded --> Analyzing: User Clicks Analyze
    Analyzing --> AnalysisComplete: Analysis Success
    Analyzing --> Error: Analysis Failure
    AnalysisComplete --> DataLoaded: View Results
    
    DataLoaded --> GeneratingSynthetic: User Generates Synthetic
    GeneratingSynthetic --> SyntheticComplete: Generation Success
    GeneratingSynthetic --> Error: Generation Failure
    SyntheticComplete --> Ready: Save Complete
    
    AnalysisComplete --> Exporting: User Exports
    Exporting --> Ready: Export Complete
    Exporting --> Error: Export Failure
    
    Error --> Ready: User Acknowledges Error
    
    Ready --> [*]: User Exits
    DataLoaded --> [*]: User Exits
    AnalysisComplete --> [*]: User Exits
```

### 3.2 Data Processing State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    Idle --> Loading: Start Load
    Loading --> Parsing: File Opened
    Parsing --> Extracting: Header Parsed
    Extracting --> Loaded: Data Extracted
    Extracting --> Failed: Parse Error
    
    Loaded --> FeatureExtraction: Start Analysis
    FeatureExtraction --> VelocityFeatures: Extract Velocity
    VelocityFeatures --> TrajectoryFeatures: Extract Trajectory
    TrajectoryFeatures --> AccelFeatures: Extract Acceleration
    AccelFeatures --> DopplerFeatures: Extract Doppler
    DopplerFeatures --> RCSFeatures: Extract RCS
    RCSFeatures --> FeaturesComplete: All Features Extracted
    
    FeaturesComplete --> Tagging: Start Tagging
    Tagging --> SpeedTags: Tag Speed
    SpeedTags --> ManeuverTags: Tag Maneuvers
    ManeuverTags --> ProfileTags: Tag Profiles
    ProfileTags --> TagsComplete: All Tags Applied
    
    TagsComplete --> Reporting: Generate Report
    Reporting --> Complete: Report Ready
    
    Complete --> Idle: Reset
    Failed --> Idle: Reset
```

---

## 4. Component Interaction Diagrams

### 4.1 Feature Extraction Data Flow

```mermaid
graph TD
    subgraph Input
        A[Radar Data Dictionary]
        A1[position: ndarray]
        A2[velocity: ndarray]
        A3[raw_data: ndarray]
        A4[doppler: ndarray]
        A5[timestamps: ndarray]
        A6[metadata: dict]
    end
    
    A --> A1
    A --> A2
    A --> A3
    A --> A4
    A --> A5
    A --> A6
    
    subgraph Feature Extraction
        FE[Feature Extractor]
        
        B1[Velocity Feature Module]
        B2[Trajectory Feature Module]
        B3[Acceleration Feature Module]
        B4[Doppler Feature Module]
        B5[RCS Feature Module]
        B6[Statistical Feature Module]
    end
    
    A2 --> B1
    A1 --> B2
    A2 --> B3
    A4 --> B4
    A3 --> B5
    A --> B6
    
    B1 --> FE
    B2 --> FE
    B3 --> FE
    B4 --> FE
    B5 --> FE
    B6 --> FE
    
    subgraph Output
        C[Features Dictionary]
        C1[Velocity Features: 10]
        C2[Trajectory Features: 12]
        C3[Acceleration Features: 8]
        C4[Doppler Features: 6]
        C5[RCS Features: 5]
        C6[Statistical Features: 5]
    end
    
    FE --> C
    C --> C1
    C --> C2
    C --> C3
    C --> C4
    C --> C5
    C --> C6
```

### 4.2 Tagging Engine Decision Flow

```mermaid
graph TD
    A[Features Input] --> B[Tagging Engine]
    
    B --> C{Speed Analysis}
    C -->|speed_mean > 300| D1[high_speed]
    C -->|150-300| D2[medium_speed]
    C -->|50-150| D3[low_speed]
    C -->|< 5| D4[hovering]
    
    B --> E{G-Force Analysis}
    E -->|g_force_max > 5| F1[g_turn]
    
    B --> G{Trajectory Analysis}
    G -->|turn_angle > 45| H1[sharp_trajectory]
    G -->|turn_angle < 15| H2[smooth_trajectory]
    G -->|straightness > 0.9| H3[straight_line]
    
    B --> I{Altitude Analysis}
    I -->|rate > 10| J1[ascending]
    I -->|rate < -10| J2[descending]
    
    B --> K{Pattern Analysis}
    K -->|circular + consistent| L1[spiral]
    K -->|low_speed + circular| L2[loitering]
    
    B --> M{Speed Trend}
    M -->|increasing| N1[accelerating]
    M -->|decreasing| N2[decelerating]
    
    B --> O{Complex Behavior}
    O -->|high_speed + high_g + sharp| P1[evasive_maneuver]
    
    D1 --> Q[Combine All Tags]
    D2 --> Q
    D3 --> Q
    D4 --> Q
    F1 --> Q
    H1 --> Q
    H2 --> Q
    H3 --> Q
    J1 --> Q
    J2 --> Q
    L1 --> Q
    L2 --> Q
    N1 --> Q
    N2 --> Q
    P1 --> Q
    
    Q --> R[Final Tag List]
```

### 4.3 Synthetic Data Generation Pipeline

```mermaid
graph LR
    subgraph Configuration
        A[Behavior Type Selection]
        B[Duration Parameters]
        C[Noise Level]
        D[Sampling Rate]
    end
    
    subgraph Trajectory Generation
        E[Initial Conditions]
        F[Behavior Pattern Function]
        G[Position Time Series]
        H[Velocity Computation]
        I[Acceleration Computation]
    end
    
    subgraph Radar Simulation
        J[Range Calculation]
        K[Doppler Shift]
        L[RCS Model]
        M[IQ Data Generation]
        N[Noise Addition]
    end
    
    subgraph Output
        O[Position Array]
        P[Velocity Array]
        Q[Raw IQ Data]
        R[Doppler Spectrum]
        S[Metadata & Labels]
        T[HDF5 File]
    end
    
    A --> F
    B --> F
    D --> F
    E --> F
    F --> G
    G --> H
    H --> I
    
    G --> J
    H --> K
    G --> L
    J --> M
    K --> M
    L --> M
    M --> N
    C --> N
    
    G --> O
    H --> P
    N --> Q
    K --> R
    A --> S
    
    O --> T
    P --> T
    Q --> T
    R --> T
    S --> T
```

---

## 5. Data Model Diagrams

### 5.1 Radar Data Structure

```mermaid
erDiagram
    RADAR_DATA ||--|| METADATA : contains
    RADAR_DATA ||--o{ POSITION : has
    RADAR_DATA ||--o{ VELOCITY : has
    RADAR_DATA ||--o{ RAW_IQ : has
    RADAR_DATA ||--o{ DOPPLER : has
    RADAR_DATA ||--o{ TIMESTAMPS : has
    
    METADATA {
        uint32 magic_number
        uint32 version
        uint32 sampling_rate
        uint32 num_channels
        uint32 samples_per_pulse
        float32 prf
        float32 center_frequency
        string source
    }
    
    POSITION {
        float64 x
        float64 y
        float64 z
        int index
    }
    
    VELOCITY {
        float64 vx
        float64 vy
        float64 vz
        int index
    }
    
    RAW_IQ {
        float32 i_component
        float32 q_component
        int sample_index
    }
    
    DOPPLER {
        float32 frequency
        float32 magnitude
        int bin_index
    }
    
    TIMESTAMPS {
        float64 time
        int index
    }
```

### 5.2 Feature Data Structure

```mermaid
erDiagram
    FEATURES ||--|| VELOCITY_FEATURES : includes
    FEATURES ||--|| TRAJECTORY_FEATURES : includes
    FEATURES ||--|| ACCELERATION_FEATURES : includes
    FEATURES ||--|| DOPPLER_FEATURES : includes
    FEATURES ||--|| RCS_FEATURES : includes
    FEATURES ||--|| STATISTICAL_FEATURES : includes
    
    VELOCITY_FEATURES {
        float64 speed_mean
        float64 speed_std
        float64 speed_max
        float64 speed_min
        float64 speed_variance
        float64 speed_range
        float64 vx_mean
        float64 vy_mean
        float64 vz_mean
        array speed_percentiles
    }
    
    TRAJECTORY_FEATURES {
        float64 path_length
        float64 path_straightness
        float64 mean_turn_angle
        float64 max_turn_angle
        float64 curvature_mean
        float64 curvature_max
        float64 trajectory_smoothness
        int direction_changes
        float64 heading_variance
    }
    
    ACCELERATION_FEATURES {
        float64 g_force_mean
        float64 g_force_max
        float64 g_force_min
        float64 g_force_std
        int high_g_events
        float64 jerk_mean
        float64 jerk_max
    }
    
    DOPPLER_FEATURES {
        float64 doppler_mean
        float64 doppler_std
        float64 doppler_bandwidth
        float64 peak_frequency
        float64 peak_power
        float64 doppler_spread
    }
    
    RCS_FEATURES {
        float64 rcs_mean
        float64 rcs_std
        float64 rcs_fluctuation
        float64 power_max
        float64 power_min
    }
    
    STATISTICAL_FEATURES {
        float64 duration
        int num_samples
        float64 altitude_change
        float64 distance_traveled
        float64 sampling_rate
    }
```

### 5.3 Tag Classification Structure

```mermaid
erDiagram
    BEHAVIOR_TAGS ||--o{ SPEED_TAGS : contains
    BEHAVIOR_TAGS ||--o{ MANEUVER_TAGS : contains
    BEHAVIOR_TAGS ||--o{ PROFILE_TAGS : contains
    
    SPEED_TAGS {
        string high_speed
        string medium_speed
        string low_speed
        string hovering
    }
    
    MANEUVER_TAGS {
        string g_turn
        string sharp_trajectory
        string smooth_trajectory
        string evasive_maneuver
        string straight_line
    }
    
    PROFILE_TAGS {
        string ascending
        string descending
        string spiral
        string loitering
        string accelerating
        string decelerating
    }
    
    CLASSIFICATION_RULES ||--|| SPEED_TAGS : defines
    CLASSIFICATION_RULES ||--|| MANEUVER_TAGS : defines
    CLASSIFICATION_RULES ||--|| PROFILE_TAGS : defines
    
    CLASSIFICATION_RULES {
        float64 high_speed_threshold
        float64 medium_speed_threshold
        float64 low_speed_threshold
        float64 hovering_threshold
        float64 high_g_threshold
        float64 sharp_turn_threshold
        float64 smooth_turn_threshold
        float64 ascending_rate_threshold
        float64 descending_rate_threshold
    }
```

### 5.4 Configuration Structure

```mermaid
erDiagram
    CONFIGURATION ||--|| DATA_PROCESSING : contains
    CONFIGURATION ||--|| FEATURES_CONFIG : contains
    CONFIGURATION ||--|| SYNTHETIC_CONFIG : contains
    CONFIGURATION ||--|| EXTERNAL_CONFIG : contains
    CONFIGURATION ||--|| GUI_CONFIG : contains
    CONFIGURATION ||--|| OUTPUT_CONFIG : contains
    
    DATA_PROCESSING {
        int chunk_size
        int sampling_rate
        int buffer_size
    }
    
    FEATURES_CONFIG {
        dict velocity_threshold
        dict acceleration_threshold
        dict trajectory
        dict radar_signature
    }
    
    SYNTHETIC_CONFIG {
        int num_samples
        float duration
        float noise_level
        int num_targets
        list target_types
    }
    
    EXTERNAL_CONFIG {
        string cpp_lib_path
        bool use_cffi
        list algorithms
    }
    
    GUI_CONFIG {
        string theme
        list window_size
        int plot_update_interval
        int max_display_points
    }
    
    OUTPUT_CONFIG {
        string save_format
        bool compression
        dict dataset_split
    }
```

---

## 6. Process Flow Diagrams

### 6.1 Complete System Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                        System Workflow                           │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │  User Input  │
    └──────┬───────┘
           │
           ├─────────────────┬──────────────┬─────────────────┐
           │                 │              │                 │
    ┌──────▼──────┐   ┌──────▼──────┐  ┌──▼─────────┐  ┌───▼────────┐
    │  GUI Launch │   │  CLI Analyze│  │ CLI Batch  │  │ CLI Generate│
    └──────┬──────┘   └──────┬──────┘  └──┬─────────┘  └───┬────────┘
           │                 │              │                │
           └─────────────────┴──────────────┴────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Configuration  │
                    │     Loading     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Data Loading  │
                    │  (Binary/HDF5)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    External     │
                    │   Algorithm?    │───No──┐
                    └────────┬────────┘       │
                            Yes               │
                             │                │
                    ┌────────▼────────┐       │
                    │  C++/MATLAB     │       │
                    │   Processing    │       │
                    └────────┬────────┘       │
                             └────────────────┘
                                     │
                            ┌────────▼────────┐
                            │     Feature     │
                            │   Extraction    │
                            │  (40+ features) │
                            └────────┬────────┘
                                     │
                            ┌────────▼────────┐
                            │     Tagging     │
                            │     Engine      │
                            │   (15 tags)     │
                            └────────┬────────┘
                                     │
                            ┌────────▼────────┐
                            │     Report      │
                            │   Generation    │
                            └────────┬────────┘
                                     │
                         ┌───────────┴───────────┐
                         │                       │
                ┌────────▼────────┐     ┌───────▼────────┐
                │  Display in GUI │     │  Export to File│
                └─────────────────┘     │  (JSON/HDF5)   │
                                        └────────────────┘
```

### 6.2 Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      Error Handling Flow                         │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │  Operation   │
    │   Attempt    │
    └──────┬───────┘
           │
    ┌──────▼───────┐
    │  Try Execute │
    └──────┬───────┘
           │
           ├───Success───►┌────────────┐
           │              │   Return   │
           │              │  Results   │
           │              └────────────┘
           │
           └───Failure───►┌────────────┐
                          │   Catch    │
                          │  Exception │
                          └──────┬─────┘
                                 │
                        ┌────────▼────────┐
                        │   Log Error     │
                        │ (with context)  │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────────┐
                        │ Can Fallback/Retry? │
                        └─────────┬───────────┘
                                  │
                    ┌─────────────┼─────────────┐
                   Yes                          No
                    │                            │
           ┌────────▼────────┐          ┌───────▼────────┐
           │  Use Fallback   │          │  Show User     │
           │  Implementation │          │     Error      │
           └────────┬────────┘          │    Message     │
                    │                   └───────┬────────┘
                    │                           │
           ┌────────▼────────┐          ┌───────▼────────┐
           │  Log Fallback   │          │   Allow User   │
           │      Usage      │          │   to Retry/    │
           └────────┬────────┘          │    Cancel      │
                    │                   └────────────────┘
           ┌────────▼────────┐
           │  Continue with  │
           │    Fallback     │
           └─────────────────┘
```

---

**Document End**

**Prepared by:** AI System Architect  
**Date:** November 5, 2025  
**Version:** 1.0  
**Companion to:** TECHNICAL_PROPOSAL.md
