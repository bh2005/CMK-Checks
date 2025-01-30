# CMK-Checks

Welcome to the CMK-Checks repository! This project contains various checks and scripts for monitoring and managing devices using Check_MK and ExtremeCloud IQ.

## Table of Contents

- Introduction
- Features
- Installation
- Usage
- Contributing
- License

## Introduction

This repository provides a collection of scripts and checks designed to enhance the monitoring capabilities of Check_MK, particularly for devices managed through ExtremeCloud IQ.

## Features

- Custom checks for Check_MK
- Scripts for managing device locations in ExtremeCloud IQ
- Easy integration with existing monitoring setups

## Installation

To install the scripts and checks, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/bh2005/CMK-Checks.git
    ```
2. Navigate to the directory:
    ```bash
    cd CMK-Checks
    ```
3. Follow the instructions in the individual script directories for setup and configuration.

## Usage

Each script and check comes with its own usage instructions. Please refer to the README files within the respective directories for detailed information.

For example, to use the `xiq_put_loc_2_device.py` script:
1. Ensure you have the required environment variables set (`ADMIN_MAIL`, `XIQ_PASS`, `XIQ_API_SECRET`).
2. Prepare your CSV file with the necessary fields (`id`, `location_id`, `x`, `y`, `latitude`, `longitude`).
3. Run the script:
    ```bash
    python xiq_put_loc_2_device.py
    ```

## Contributing

We welcome contributions from the community! Please read our Contributing Guidelines to get started.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
