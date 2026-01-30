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

    Container_Boundary(c1, "Transformer Thermal Model") {
        System(toolbox, "Toolbox", "Provides extra utility functions that are not necessary to run the model,<br/> but can be handy for a large group of our users.")
        System(model, "Model", "Calculate transformer temperatures under specified load<br/> and ambient temperature profiles.")
        System(transformer, "Transformer", "Data class (containing logic) with specifications and calculated properties<br/> of a transformer. Can build a PowerTransformer, DistributionTransformer<br/> and ThreeWindingTransformer.")
        System(hs_calibration, "Hot-spot calibration", "Calibrates hot spot factor as a replacement<br/> if this value is unknown to the user.")
        System(aging, "Aging", "Determine the aging rate profile for a specific type of insulated paper<br/> for a given hot spot profile.")
        System(docs, "Docs", "Module with markdown files linking to existing code and extra added context around it.")
    }

    System_Ext(mkdocs, "mkdocs", "MkDocs is a fast, simple and downright gorgeous static site generator<br/> that's geared towards building project documentation.")
    System_Ext(pandas, "Pandas", "A fast, powerful, flexible and easy to use open source data analysis<br/> and manipulation tool, built on top of the Python programming language.")
    System_Ext(numpy, "Numpy", "The fundamental package for scientific computing with Python")

    Rel(scientist, transformer, "Provides asset specifications to build a")
    Rel(scientist, toolbox, "Easily transforms pandas input into TTM-valid input with")
    Rel(scientist, aging, "Estimates the aging of a transformer using.")
    Rel(scientist, docs, "Understands the workings of TTM via the")

```
<!-- markdownlint-enable MD013 -->
