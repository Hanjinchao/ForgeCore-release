
# OrgeCore Release Project

OrgeCore is a free-to-use commercial binary tool designed to simplify training popular neural network models.
It supports Windows and Linux, and includes optional Rust-based inference binary compilation.
This project is open for public use, you can find the binary file from realease link


## Features 

- Simple GUI workflow for training YOLO-style models
- Supports YOLOv8-ready dataset structure
- CPU or GPU training options
- Automatically generates a parameter file for customization
- Can compile an inference-ready binary using Rust

## How to Use
Windows / Linux(Ubuntu) 
| > Download the binary from the Releases page. \
 Install and run the application on Windows.  
 Install with [sudo dpkg -i dist/forgecore_*.deb]. 

| > Prepare your dataset in YOLOv8 format with the required folder structure.
| >Follow the UI steps:

    Step 1 — Build
    Choose GPU or CPU mode depending on your system.

    Step 2 — Training
    Select your dataset folder.
    The trained model output will be automatically saved to the output directory.
    A parameter file will also be generated—modify it as needed for your workflow.

    Step 3 — Build Inference Binary (Optional)
    If you need a final standalone inference binary:
    Run the final build step
    The completed inference binary will appear in the specified output folder

## Notes: 
1. The final .safetensors file will be located in:
|your-root-data-dir|/run_with_early_stopping/weights
If you want to retrain the network, remove this folder first.
2. train_parameters.yaml is generated in |your-root-data-dir|. Modify it to adjust learning rate, epochs, or other parameters for your use case.

## Example
An example code is included showing how to load the generated binary and weight file for inference.

## Project Status-Updates
This is a personal project, not affiliated with any employer.
Model updates or new features are delivered without a fixed schedule.
There is no defined roadmap and no commitment toward enterprise-level capabilities—updates will come when possible.

# License

This software is provided as a binary-only tool.

✔ Free for personal or commercial use
✔ Redistribution allowed (binary only, unmodified)

✘ Modification of the binary is not allowed
✘ Reverse engineering, decompiling, or disassembling is prohibited
✘ Selling or claiming ownership of the binary is not permitted

The source code is not public and remains fully owned by the author.
