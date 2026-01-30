<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# The architecture of Transformer Thermal Model

<!-- markdownlint-disable MD013 -->
```mermaid
C4Container
    title C2: Containers of the Transformer Thermal Model

    Person_Ext(scientist, "Scientist", "Someone that reports on or analyses thermals of transformers.")
    System_Ext(cyclops, "Cyclic Optimiser", "Finds a thermal limit of a transformer by repeatedly calculating<br/> the thermals and scaling a load profile.")

    

    Boundary(b0, "Transformer Thermal Model") {
        System(toolbox, "Toolbox", "Provides extra utility functions that are not necessary to run the model,<br/> but can be handy for a large group of our users.")

        Boundary(b4, "Documentation") {
            System(docs, "Docs", "Module with markdown files linking to existing code and extra added context around it.")
        }

        Boundary(b2, "Transformer Thermal Model 2"){
            System(hs_calibration, "Hot-spot calibration", "Calibrates hot spot factor as a replacement<br/> if this value is unknown to the user.")
            System(aging, "Aging", "Determine the aging rate profile for a specific type of insulated paper<br/> for a given hot spot profile.")
            System(model, "Model", "Calculate transformer temperatures under specified load<br/> and ambient temperature profiles.")
            System(transformer, "Transformer", "Data class (containing logic) with specifications and calculated properties<br/> of a transformer. Can build a PowerTransformer, DistributionTransformer<br/> and ThreeWindingTransformer.")
            System_Ext(numpy, "Numpy", "The fundamental package for scientific computing with Python")
        }
    }

    Rel(scientist, transformer, "Provides asset specifications to build a")
    Rel(scientist, toolbox, "Easily transforms pandas input into TTM-valid input with")
    Rel(scientist, aging, "Estimates the aging of a transformer using.")
    Rel(scientist, docs, "Understands the workings of TTM via the")

    Rel(cyclops, model, "Calculates thermal transformer limits using")

    Rel(toolbox, model, "Translates input from the user for")

    Rel(transformer, aging, "Provides possible insulator types for")
    Rel(transformer, numpy, "Represents, organizes and structures data with")
    
    UpdateLayoutConfig($c4BoundaryInRow="4", $c4ShapeInRow="1")
```

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
<!-- markdownlint-enable MD013 -->
