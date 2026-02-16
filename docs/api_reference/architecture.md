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

        Boundary(b1, "Extra features") {
            Container(docs, "Docs", "HTML module", "Module with markdown files linking to existing code and extra added context around it.")
            Container(toolbox, "Toolbox", "Python module", "Provides extra utility functions that are not necessary to run the model,<br/> but can be handy for a large group of our users.")
            Container(aging, "Aging", "Python module", "Determine the aging rate profile for a specific type of insulated paper<br/> for a given hot spot profile.")
        }

        Boundary(b2, "Core Container"){
            System(thermal_modeling, "Thermal Modeling", "Calculate thermals of a transformer.")
        }

        Boundary(b3, "Imported packages"){
            System_Ext(numpy, "Numpy", "The fundamental package for scientific computing with Python")
        }
    }

    Rel(scientist, toolbox, "Easily transforms pandas input into TTM-valid input with")
    Rel(scientist, aging, "Estimates the aging of a transformer using")
    Rel(scientist, docs, "Understands the workings of TTM via the")
    Rel(scientist, thermal_modeling, "Calculates thermal values of a transformer using")

    Rel(cyclops, thermal_modeling, "Calculates thermal transformer limits using")

    Rel(thermal_modeling, toolbox, "Provides input schemas for")
    Rel(thermal_modeling, aging, "Provides possible insulator types for")

    Rel(aging, numpy, "Represents, organizes and structures data with")
    Rel(thermal_modeling, numpy, "Represents, organizes and structures data with")
    
    UpdateLayoutConfig($c4BoundaryInRow="2", $c4ShapeInRow="2")
```

## Component diagrams

### Thermal Modeling

```mermaid
C4Component
    title C3: Thermal Modeling

    Person_Ext(scientist, "Scientist", "Someone that reports on or analyses thermals of transformers.")
    System_Ext(cyclops, "Cyclic Optimiser", "Finds a thermal limit of a transformer by repeatedly calculating<br/> the thermals and scaling a load profile.")

    Boundary(b0, "Transformer Thermal Model"){
        System_Boundary(s0, "Thermal Modeling"){
            Container(hs_calibration, "Hot-spot calibration", "Python module", "Calibrates hot spot factor as a replacement<br/> if this value is unknown to the user.")
            Container(model, "Model", "Python module", "Calculate transformer temperatures under specified load<br/> and ambient temperature profiles.")
            Container(transformer, "Transformer", "Python module", "Data class (containing logic) with specifications and calculated properties<br/> of a transformer. Can build a PowerTransformer, DistributionTransformer<br/> and ThreeWindingTransformer.")
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
        System(thermal_model, "Thermal Modeling")
    }

    Rel(scientist, toolbox, "Translates their pandas DataFrames to TTM inputs using")
    Rel(toolbox, thermal_model, "Reads methods for generating user input from")

    UpdateLayoutConfig($c4BoundaryInRow="2", $c4ShapeInRow="1")
```

### Docs

```mermaid
C4Component
    title C3: Docs Components

    Person_Ext(scientist, "Scientist", "Someone that reports on or analyses thermals of transformers.")
    Boundary(ttm, "Transformer Thermal Model"){
        Boundary(b0, "Extra features") {
            Container_Boundary(b01, "other features"){
                System(other_features, "Other features", "The other extra features, e.g. the Toolbox and Aging.")
            }
            Container_Boundary(b02, "Docs"){
                System(docs, "Docs", "HTML files building the documentation page")
                System_Ext(mkdocs, "MkDocs", "MkDocs is a fast, simple and downright gorgeous static site generator that's geared towards building project documentation.")
                Person(developer, "Developer", "Someone that contributes to the TTM.")
                Rel(developer, mkdocs, "Builds the documentation by running")
            }
        }

        Boundary(b1, "Core Container"){
            System(thermal_modeling, "Thermal Modeling", "Calculate thermals of a transformer.")
        }

    }

    Rel(scientist, docs, "Understands the inner workings of the TTM via")

    Rel(mkdocs, thermal_modeling, "Retrieves documentation from")
    Rel(mkdocs, other_features, "Retrieves documentation from")
    Rel(docs, mkdocs, "Builds the HTML files with")

    UpdateLayoutConfig($c4BoundaryInRow="1", $c4ShapeInRow="3")


```

<!-- markdownlint-enable MD013 -->