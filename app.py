from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/generate_smiles', methods=['POST'])
def generate_smiles():
    data = request.get_json()
    sequences = data.get('sequences')
    uniprot_ids = data.get('uniprot_ids')
    num_generated = data.get('num_generated', 10)  # Default value
    output_file = "temp_output.txt"  # Temporary output file

    if not sequences and not uniprot_ids:
        return jsonify({'error': 'Either sequences or uniprot_ids must be provided'}), 400

    try:
        # Prepare the command
        command = ["python3", "drugGen_generator_cli.py",
                   "--num_generated", str(num_generated),
                   "--output_file", output_file]

        if sequences:
            command.extend(["--sequences"] + sequences)  # Pass sequences as separate args
        if uniprot_ids:
            command.extend(["--uniprot_ids"] + uniprot_ids)  # Pass uniprot_ids as separate args

        # Execute the command
        subprocess.run(command, check=True, cwd=os.getcwd())

        # Read SMILES from the output file
        with open(output_file, 'r') as f:
            generated_smiles = [line.strip() for line in f]

        # Remove the temporary output file
        os.remove(output_file)

        return jsonify({'generated_smiles': generated_smiles})

    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500
    except FileNotFoundError:
        return jsonify({'error': 'DrugGen_generator_cli.py not found'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
