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
        LegendOptionalState: Optional State
        LegendOutputState: Output State
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
        InitialTemperatures: Initial temperatures (optional)
        InitialTemperatures:  - Initial top oil temperature

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
        [*] --> InitialTemperatures
    }
    
    %% Composite state for results
    state Results {
        TopOilTemp: Top Oil Temperature
        HotSpotTemp: Hot Spot Temperature
        AgingResults: Aging Assessment
        
        OutputProfile: OutputProfile
        AgingOutput: pd.Series

        TopOilTemp --> OutputProfile
        HotSpotTemp --> OutputProfile
        AgingResults --> AgingOutput
    }
    
    %% Main flow
    DataCollection
    DataCollection --> Validation: Validate inputs
    Validation --> ThermalModel: create Model() with InputProfile, Transformer and optional initial temperatures
    Validation --> TransformerConfig: Create Transformer() with specs and cooler type
    TransformerConfig --> HotSpotCalib: Calibrate hot spot factor if needed (only for PowerTransformers)
    TransformerConfig --> ThermalModel: skip if factor known
    HotSpotCalib --> ThermalModel: Initialize model
    ThermalModel --> TempCalculation: Calculate temperatures
    TempCalculation --> AgingAnalysis: Analyze aging (using the modeled hot spot profile)
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
    classDef inputState fill:#d9e7e0,stroke:#267950,stroke-width:3px
    classDef processState fill:#fbe9d9,stroke:#ea8426
    classDef optionalState fill:#f3dddd,stroke:#bb3b40,font-style:italic,stroke-dasharray: 5 5
    classDef outputState fill:#ecddec,stroke:#954091,stroke-width:3px
    
    class LegendInputState,Validation,InputProfile,TransformerSpecifications,CoolerTypePT,CoolerTypeDT inputState
    class LegendProcessState,TransformerConfig,ThermalModel,TempCalculation processState
    class LegendOutputState,OutputProfile,AgingOutput outputState
    class LegendOptionalState,HotSpotCalib,AgingAnalysis optionalState
```
