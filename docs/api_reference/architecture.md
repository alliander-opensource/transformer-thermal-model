<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# The architecture of Transformer Thermal Model

<!-- markdownlint-disable MD013 -->
## Container diagram

```mermaid
C4Container
    title C2: Containers of the Transformer Thermal Model

    Person_Ext(scientist, "Scientist", "Someone that reports on or analyses thermals of transformers.")
    System_Ext(cyclops, "Cyclic Optimiser", "Finds a thermal limit of a transformer by repeatedly calculating<br/> the thermals and scaling a load profile.")

    

    Boundary(b0, "Transformer Thermal Model") {
        System(toolbox, "Toolbox", "Provides extra utility functions that are not necessary to run the model,<br/> but can be handy for a large group of our users.")

        System(docs, "Docs", "Module with markdown files linking to existing code and extra added context around it.")

        Boundary(b1, "Extra features") {
            System(aging, "Aging", "Determine the aging rate profile for a specific type of insulated paper<br/> for a given hot spot profile.")
        }

        System(thermal_modeling, "Thermal Modeling")

        Boundary(b2, "Thermal Modeling"){
            System(hs_calibration, "Hot-spot calibration", "Calibrates hot spot factor as a replacement<br/> if this value is unknown to the user.")
            System(model, "Model", "Calculate transformer temperatures under specified load<br/> and ambient temperature profiles.")
            System(transformer, "Transformer", "Data class (containing logic) with specifications and calculated properties<br/> of a transformer. Can build a PowerTransformer, DistributionTransformer<br/> and ThreeWindingTransformer.")
            System_Ext(numpy, "Numpy", "The fundamental package for scientific computing with Python")
        }
    }

    Rel(scientist, toolbox, "Easily transforms pandas input into TTM-valid input with")
    Rel(scientist, aging, "Estimates the aging of a transformer using.")
    Rel(scientist, docs, "Understands the workings of TTM via the")

    Rel(cyclops, thermal_modeling, "Calculates thermal transformer limits using")

    Rel(toolbox, thermal_modeling, "Translates input from the user for")

    Rel(thermal_modeling, aging, "Provides possible insulator types for")
    Rel(thermal_modeling, numpy, "Represents, organizes and structures data with")
    
    UpdateLayoutConfig($c4BoundaryInRow="4", $c4ShapeInRow="1")
```

## Component diagrams

### Toolbox components

```mermaid
C4Component
    title C3: Toolbox Components

    Person_Ext(scientist, "Scientist", "Someone that reports on or analyses thermals of transformers.")
    Boundary(b0, "Transformer Thermal Model"){

        System_Boundary(b1, "Toolbox"){
            System(toolbox, "Toolbox", "Provides extra utility functions that are not necessary to run the model,<br/> but can be handy for a large group of our users.")
            System_Ext(pandas, "Pandas", "A fast, powerful, flexible and easy to use open source data analysis<br/> and manipulation tool, built on top of the Python programming language.")
            Rel(toolbox, pandas, "Formats pandas DataFrames to numpy with")
        }
        System(ttm, "Transformer Thermal Model")
    }

    Rel(scientist, toolbox, "Translates their pandas DataFrames to TTM inputs using")
    Rel(toolbox, ttm, "Reads methods for generating user input from")

    UpdateLayoutConfig($c4BoundaryInRow="2", $c4ShapeInRow="1")
```

### Thermal Modeling

```mermaid
C4Component
    title C3: Thermal Modeling

    Person_Ext(scientist, "Scientist", "Someone that reports on or analyses thermals of transformers.")
    System_Ext(cyclops, "Cyclic Optimiser", "Finds a thermal limit of a transformer by repeatedly calculating<br/> the thermals and scaling a load profile.")

    Boundary(b0, "Transformer Thermal Model"){
        System_Boundary(s0, "Thermal Modeling"){
            System(hs_calibration, "Hot-spot calibration", "Calibrates hot spot factor as a replacement<br/> if this value is unknown to the user.")
            System(model, "Model", "Calculate transformer temperatures under specified load<br/> and ambient temperature profiles.")
            System(transformer, "Transformer", "Data class (containing logic) with specifications and calculated properties<br/> of a transformer. Can build a PowerTransformer, DistributionTransformer<br/> and ThreeWindingTransformer.")
        }

        System_Boundary(s1, "Imported packages"){
            System_Ext(numpy, "Numpy", "The fundamental package for scientific computing with Python")
        }
    }
    Rel(scientist, transformer, "Provides asset specifications to build a")
    Rel(scientist, hs_calibration, "Calibrates hot-spot factor (when unknown) with")
    Rel(cyclops, model, "Finds thermal limits of Transformer using")
    Rel(scientist, model, "Finds thermal values of a Transformer using")
    Rel(model, transformer, "Simulates thermal values of the provided")

    Rel(model, numpy, "Represents data with")
    Rel(transformer, numpy, "Represents data with")
    Rel(hs_calibration, numpy, "Represents data with")

    UpdateLayoutConfig($c4BoundaryInRow="3", $c4ShapeInRow="1")
```

<!-- markdownlint-enable MD013 -->
