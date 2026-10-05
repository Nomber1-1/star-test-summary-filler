import csv
import os

# Skate Canada STAR test fee, in dollars. Raised from 12.00 to 15.00 effective
# 2026-08-01. Single constant on purpose: it is used both for each test line and
# for the sheet total, and a partial edit would make the lines disagree with the
# total. Set it to 12.00 for a batch of tests taken before 2026-08-01.
TEST_FEE = 15.00

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Please install PyMuPDF by running: pip install pymupdf")
    exit(1)

def process_test_summaries(csv_file_path, template_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    eligible_tests = []
    
    # 1. Read the CSV and collect all eligible tests
    with open(csv_file_path, mode='r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            statut_paiement = row.get('Statut de Paiement', '').strip()
            sommaire_test = row.get('# Sommaire de Test', '').strip()
            
            # Condition: Status contains "Paid" AND Summary Number is empty
            if 'Paid' in statut_paiement and not sommaire_test:
                eligible_tests.append(row)
                
    if not eligible_tests:
        print("No eligible tests found.")
        return
        
    # 2. Sort tests by Skater name ("Patineur")
    eligible_tests.sort(key=lambda x: x.get('Patineur', ''))
    
    generated_count = 0
    batch_size = 10
    
    print(f"Found {len(eligible_tests)} tests. Processing in batches of 10...")
    
    # 3. Process in batches of 10
    for i in range(0, len(eligible_tests), batch_size):
        batch = eligible_tests[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        data_dict = {}
        
        # Populate the dictionary for fields 1 through 10 based on the batched items
        for idx, row in enumerate(batch, start=1):
            patineur = row.get('Patineur', '')
            nom_famille = row.get('Patineur Nom  de Famille', '').strip()
            
            # Construct the full name. 
            # If a last name is provided, take the first name part from 'Patineur' (everything before the trailing initials)
            if nom_famille:
                parts = patineur.split()
                # Remove single letter initials (or hyphenated initials like T-H) from the end
                first_name_parts = []
                for p in parts:
                    if all(len(part) == 1 for part in p.split('-')):
                        continue
                    first_name_parts.append(p)
                nom_patineur = ' '.join(first_name_parts) + ' ' + nom_famille
            else:
                nom_patineur = patineur
                
            code_test = row.get('Test Réussi', '')
            note_passage = row.get('Note de Passage', '')
            
            is_reussite = 'Réussite' in note_passage and 'Honneurs' not in note_passage
            is_reprise = 'Reprise' in note_passage
            is_honneurs = 'Honneurs' in note_passage
            
            data_dict.update({
                f"SkaterSkateCanadaNumber{idx}": row.get('# Skate Canada', ''),
                f"EvaluatorSkateCanadaNumber{idx}": row.get('# Skate Canada Eval', ''),
                f"TestCode{idx}": code_test,
                f"TestDate{idx}": row.get('Date (Apparaît comme JJ/MM/AAAA)', ''),
                f"SkaterName{idx}": nom_patineur,
                f"EvaluatorName{idx}": row.get('Evaluateur/trice', ''),
                f"TestPassedCheck{idx}": True if is_reussite else False,
                f"TestFailedCheck{idx}": True if is_reprise else False,
                f"TestPassedWHonoursCheck{idx}": True if is_honneurs else False,
                f"TestAmount{idx}": f"{TEST_FEE:.2f}"
            })
            
        # Calculate total for the sheet
        data_dict["TotalAmountDue"] = f"{len(batch) * TEST_FEE:.2f}"
        
        # Open PDF template for the batch
        doc = fitz.open(template_path)
        page = doc[0]
        
        # Iterate through all fields in the page and update values
        for field in page.widgets():
            field_name = field.field_name
            if field_name in data_dict:
                value = data_dict[field_name]
                if field.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                    field.field_value = value
                else:
                    field.field_value = str(value)
                field.update()
        
        # Save output document
        output_filename = f"{output_name}_{batch_num}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        doc.save(output_path)
        doc.close()
        
        print(f"Generated {output_filename} with {len(batch)} tests.")
        generated_count += 1

    print(f"\nSuccessfully generated {generated_count} summary files in the '{output_dir}' folder.")

if __name__ == "__main__":
    csv_path = 'Saison 2025-26 - MaCaPat - Tests Input.csv'
    template_path = 'Assessment Summary FR - Fillable - 1 Page.pdf'
    output_directory = 'Generated_Summaries'
    output_name = "Spring_2026_Summary"
    
    process_test_summaries(csv_path, template_path, output_directory)
