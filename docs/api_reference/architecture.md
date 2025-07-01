<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# The architecture of Transformer Thermal Model

```mermaid
stateDiagram-v2
    direction TB


    %% Define states with descriptions
    DataCollection: Data Collection
    Validation: Input Validation
    TransformerConfig: Transformer Configuration
    HotSpotCalib: Hot Spot Calibration
    ThermalModel: Thermal Model Engine
    TempCalculation: Temperature Calculation
    AgingAnalysis: Aging Analysis
    Results: Output Results

    %% Legend for state descriptions
    state Legend{
        direction LR
        LegendInputState: Input State
        LegendProcessState: Process State
        LegendOutputState: Output State
        LegendOptionalState: Optional State
    }
    
    %% Composite state for input data sources
    state DataCollection {
        direction LR
        state InputData{
            direction LR
            DateTimeIndex: Date and Time Index
            LoadProfile: Load Profile Data
            AmbientTemp: Ambient Temperature Data

            InputProfile: InputProfile

            DateTimeIndex --> InputProfile
            LoadProfile --> InputProfile
            AmbientTemp --> InputProfile
        }
        state CoolerConfiguration {
            direction LR
            CoolerTypePT: CoolerType ONAN or ONAF
            CoolerTypeDT: CoolerType not needed

            [*] --> CoolerTypePT: PowerTransformer
            [*] --> CoolerTypeDT: DistributionTransformer
        }
        
        state TransformerSpecs {
            direction LR
            MandatorySpecs: Mandatory Specifications
            OptionalSpecs: Optional Specifications
            TransformerSpecifications: UserTransformerSpecifications
            
            MandatorySpecs:  - load_loss (W)
            MandatorySpecs:  - nom_load_sec_side (A)
            MandatorySpecs:  - no_load_loss (W)
            MandatorySpecs:  - amb_temp_surcharge (K)

            OptionalSpecs:  - top_oil_temp_rise (K)
            OptionalSpecs:  - winding_oil_gradient (K)
            OptionalSpecs:  - hot_spot_fac (-)
            OptionalSpecs:  - time_const_oil, time_const_windings
            OptionalSpecs:  - ... (other optional specs)

            MandatorySpecs --> TransformerSpecifications
            OptionalSpecs --> TransformerSpecifications

        }

        [*] --> InputData      
        [*] --> TransformerSpecs
        [*] --> CoolerConfiguration
    }
    
    %% Composite state for results
    state Results {
        TopOilTemp: Top Oil Temperature
        HotSpotTemp: Hot Spot Temperature
        AgingResults: Aging Assessment
        
        OutputProfile: OutputProfile

        TopOilTemp --> OutputProfile
        HotSpotTemp --> OutputProfile
        AgingResults --> OutputProfile
    }
    
    %% Main flow
    DataCollection
    DataCollection --> Validation: Validate inputs
    Validation --> ThermalModel: create Model() with InputProfile and Transformer
    Validation --> TransformerConfig: Create Transformer() with specs and cooler type
    TransformerConfig --> HotSpotCalib: Calibrate hot spot factor if needed (only for PowerTransformers)
    TransformerConfig --> ThermalModel: skip if factor known
    HotSpotCalib --> ThermalModel: Initialize model
    ThermalModel --> TempCalculation: Calculate temperatures
    TempCalculation --> AgingAnalysis: Analyze aging
    TempCalculation --> Results: Generate outputs
    AgingAnalysis --> Results: Add aging data
    Results --> [*]

    
    %% Notes for clarity
    note right of Validation
        Uses Pydantic schemas to validate
        load profiles, ambient temperature,
        and transformer specifications
    end note
    
    note left of TempCalculation
        Implements IEC 60076-7 standard
        for thermal modeling calculations
    end note
    
    %% Styling
    classDef inputState fill:#F0F4E3,stroke:#99B352
    classDef processState fill:#ECDEDE,stroke:#8F3825
    classDef outputState fill:#E8DFEB,stroke:#6B3078
    classDef optionalState fill:#F2E7DF,stroke:#AD672F
    
    class LegendInputState,Validation,InputProfile,TransformerSpecifications,CoolerTypePT,CoolerTypeDT inputState
    class LegendProcessState,TransformerConfig,ThermalModel,TempCalculation processState
    class LegendOutputState,OutputProfile outputState
    class LegendOptionalState,HotSpotCalib,AgingAnalysis optionalState
```
