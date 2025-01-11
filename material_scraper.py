from xml.dom import minidom
import csv
import os
import glob
import codecs
import re

def get_next_file_number(output_dir):
    # Get all existing materials_properties files
    existing_files = glob.glob(os.path.join(output_dir, "materials_properties*.csv"))
    if not existing_files:
        return 1
    
    # Extract numbers from existing filenames
    numbers = []
    pattern = re.compile(r"materials_properties(\d+)\.csv$")
    for file in existing_files:
        match = pattern.search(file)
        if match:
            numbers.append(int(match.group(1)))
    
    # Return next number in sequence, or 1 if no numbered files exist
    return max(numbers) + 1 if numbers else 1

def get_source_category(filename):
    filename = filename.lower()
    if 'hoya' in filename:
        return 'Hoya'
    elif 'schott' in filename:
        return 'Schott'
    elif 'optical' in filename:
        return 'Optical'
    elif 'custom' in filename:
        return 'Custom'
    else:
        return 'Other'

def get_property_value(properties, display_name):
    for prop in properties:
        if prop.nodeType == prop.ELEMENT_NODE:
            if prop.getAttribute('displayname').lower() == display_name.lower():
                value = prop.getAttribute('value')
                units = prop.getAttribute('units')
                return value, units
    return None, None

def process_material_file(file_path, csvwriter):
    try:
        # Read the file with UTF-16 encoding
        with codecs.open(file_path, 'r', encoding='utf-16') as file:
            xml_content = file.read()
        
        # Parse XML content
        doc = minidom.parseString(xml_content)
        
        # Get the source category
        source_category = get_source_category(os.path.basename(file_path))
        
        # Find all material elements
        materials = doc.getElementsByTagName('material')
        if not materials:
            print(f"Warning: No materials found in {file_path}")
            return False
            
        for material in materials:
            material_name = material.getAttribute('name') or 'Unknown'
            print(f"Found material: {material_name}")
            
            # Initialize property dictionary
            properties = {
                'Elastic Modulus': 'N/A',
                'Poisson\'s Ratio': 'N/A',
                'Shear Modulus': 'N/A',
                'Thermal Expansion Coefficient': 'N/A',
                'Density': 'N/A',
                'Thermal Conductivity': 'N/A',
                'Specific Heat': 'N/A',
                'Tensile Strength': 'N/A',
                'Compressive Strength': 'N/A',
                'Other Properties': []
            }
            
            # Process physical properties
            physical_props = material.getElementsByTagName('physicalproperties')
            if physical_props:
                for prop in physical_props[0].childNodes:
                    if prop.nodeType == prop.ELEMENT_NODE:
                        name = prop.getAttribute('displayname')
                        value = prop.getAttribute('value')
                        units = prop.getAttribute('units') or ''
                        
                        # Map properties to their respective columns
                        name_lower = name.lower()
                        if "elastic" in name_lower or "young" in name_lower:
                            properties['Elastic Modulus'] = f"{value} {units}".strip()
                        elif "poisson" in name_lower:
                            properties['Poisson\'s Ratio'] = f"{value} {units}".strip()
                        elif "shear" in name_lower:
                            properties['Shear Modulus'] = f"{value} {units}".strip()
                        elif "thermal expansion" in name_lower:
                            properties['Thermal Expansion Coefficient'] = f"{value} {units}".strip()
                        elif "density" in name_lower or "dens" in name_lower:
                            # Convert to kg/m³ if needed
                            try:
                                density_value = float(value)
                                if units.lower() in ['g/cm³', 'g/cc']:
                                    density_value *= 1000
                                properties['Density'] = f"{density_value} kg/m³"
                            except ValueError:
                                properties['Density'] = f"{value} {units}".strip()
                        elif "thermal conductivity" in name_lower:
                            properties['Thermal Conductivity'] = f"{value} {units}".strip()
                        elif "specific heat" in name_lower or "heat capacity" in name_lower:
                            properties['Specific Heat'] = f"{value} {units}".strip()
                        elif "tensile" in name_lower:
                            properties['Tensile Strength'] = f"{value} {units}".strip()
                        elif "compressive" in name_lower:
                            properties['Compressive Strength'] = f"{value} {units}".strip()
                        else:
                            properties['Other Properties'].append(f"{name}: {value} {units}".strip())
            
            # Process custom properties
            custom_props = material.getElementsByTagName('prop')
            for prop in custom_props:
                name = prop.getAttribute('name')
                value = prop.getAttribute('value')
                units = prop.getAttribute('units') or ''
                properties['Other Properties'].append(f"{name}: {value} {units}".strip())
            
            # Write the row
            csvwriter.writerow([
                material_name,
                source_category,
                properties['Elastic Modulus'],
                properties['Poisson\'s Ratio'],
                properties['Shear Modulus'],
                properties['Thermal Expansion Coefficient'],
                properties['Density'],
                properties['Thermal Conductivity'],
                properties['Specific Heat'],
                properties['Tensile Strength'],
                properties['Compressive Strength'],
                '; '.join(properties['Other Properties']) if properties['Other Properties'] else 'N/A'
            ])
        
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return False

def main():
    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Get the next file number
    next_number = get_next_file_number(output_dir)
    
    # Create the output filename with the next number
    output_file = os.path.join(output_dir, f"materials_properties{next_number}.csv")
    
    try:
        with open(output_file, "w", newline="", encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            # Header row with new columns
            csvwriter.writerow([
                "Glass Name",
                "Source",
                "Elastic Modulus",
                "Poisson's Ratio",
                "Shear Modulus",
                "Thermal Expansion Coefficient",
                "Density (kg/m³)",
                "Thermal Conductivity",
                "Specific Heat",
                "Tensile Strength",
                "Compressive Strength",
                "Other Properties"
            ])

            # Process all glass files
            glass_files = glob.glob("glass*.txt")
            
            # Add other material files
            material_files = glass_files + ["Custom Materials.txt", "Optical Materials.txt"]
            
            successful_files = 0
            for file_path in material_files:
                if os.path.exists(file_path):
                    print(f"\nProcessing {file_path}...")
                    if process_material_file(file_path, csvwriter):
                        successful_files += 1
                else:
                    print(f"File not found: {file_path}")

            print(f"\nExtraction complete!")
            print(f"Successfully processed {successful_files} out of {len(material_files)} files")
            print(f"Data saved to {output_file}")
    except PermissionError:
        print(f"Error: Unable to write to {output_file}. Please close any programs that might have this file open.")
        return
    except Exception as e:
        print(f"Error: {str(e)}")
        return

if __name__ == "__main__":
    main() 