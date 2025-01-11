# Material Properties Scraper

A Python script to extract material properties from SolidWorks material XML files and export them to CSV format.

## Features

- Extracts material properties from SolidWorks XML material files
- Supports multiple file formats (Hoya, Schott, Custom, and Optical materials)
- Exports data to CSV with the following properties:
  - Glass Name
  - Source (Hoya, Schott, Optical, Custom)
  - Elastic Modulus
  - Poisson's Ratio
  - Shear Modulus
  - Thermal Expansion Coefficient
  - Density (kg/m³)
  - Thermal Conductivity
  - Specific Heat
  - Tensile Strength
  - Compressive Strength
  - Other Properties

## Usage

1. Place your SolidWorks material XML files in the same directory as the script
2. Run the script:
   ```bash
   python material_scraper.py
   ```
3. The script will create an `output` directory and save the results in a CSV file named `materials_propertiesX.csv` where X is an incrementing number

## Input Files

The script processes the following files:
- `glass - *.txt` (any file starting with "glass -")
- `Custom Materials.txt`
- `Optical Materials.txt`

## Output Format

The script generates a CSV file with the following columns:
1. Glass Name
2. Source
3. Elastic Modulus
4. Poisson's Ratio
5. Shear Modulus
6. Thermal Expansion Coefficient
7. Density (kg/m³)
8. Thermal Conductivity
9. Specific Heat
10. Tensile Strength
11. Compressive Strength
12. Other Properties

## Requirements

- Python 3.x
- No additional packages required (uses standard library only)