# Imports
import re


def geopt_and_out_to_poscar(label='sprc-calc', step=-1):

    # Find lattice vectors and atom species in output file
    cell_regex = re.compile(r'CELL:\s*([0-9\.\-]+)\s+([0-9\.\-]+)'
                            r'\s+([0-9\.\-]+)\s*')
    vec_regex = re.compile(r'\s*([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s*')
    atom_regex = re.compile(r'\s*Atom type [0-9]+\s*\(valence electrons\)\s*:'
                            r'  ([a-zA-Z]{1,2}) [0-9]+\s*')
    num_regex = re.compile(r'Number of atoms of type [0-9]+\s*:  ([0-9]+)\s*')
    species_dict = {}
    out_file = open(label + '.out', 'r')
    out_line = out_file.readline()
    while out_line:

        # Find lattice vectors
        cell_match = cell_regex.match(out_line)
        if cell_match:
            cell_x = float(cell_match.group(1))
            cell_y = float(cell_match.group(2))
            cell_z = float(cell_match.group(3))
            out_line = out_file.readline()
            out_line = out_file.readline()
            vec_1 = [str(float(vec_regex.match(out_line).group(1))*cell_x),
                     str(float(vec_regex.match(out_line).group(2))*cell_y),
                     str(float(vec_regex.match(out_line).group(3))*cell_z)]
            out_line = out_file.readline()
            vec_2 = [str(float(vec_regex.match(out_line).group(1))*cell_x),
                     str(float(vec_regex.match(out_line).group(2))*cell_y),
                     str(float(vec_regex.match(out_line).group(3))*cell_z)]
            out_line = out_file.readline()
            vec_3 = [str(float(vec_regex.match(out_line).group(1))*cell_x),
                     str(float(vec_regex.match(out_line).group(2))*cell_y),
                     str(float(vec_regex.match(out_line).group(3))*cell_z)]

        # Find atom species
        atom_match = atom_regex.match(out_line)
        if atom_match:
            species = atom_match.group(1)
            out_line = out_file.readline()
            out_line = out_file.readline()
            out_line = out_file.readline()
            num = int(num_regex.match(out_line).group(1))
            species_dict[species] = num

        out_line = out_file.readline()
    out_file.close()

    # Find number of steps in geopt file
    num_steps = 0
    geopt_file = open(label + '.geopt', 'r')
    geopt_line = geopt_file.readline()
    while geopt_line:
        if geopt_line == ':R(Bohr):\n':
            num_steps += 1
        geopt_line = geopt_file.readline()
    geopt_file.close()

    # Interpret negative step values
    while step < 0:
        step += num_steps

    # Extract relevant coordinate block from geopt file
    coord_block = ''
    cur_step = -1
    coord_regex = re.compile(r'\s*[0-9\.\-]+\s+[0-9\.\-]+\s+[0-9\.\-]+\s*')
    geopt_file = open(label + '.geopt', 'r')
    geopt_line = geopt_file.readline()
    while geopt_line:
        if geopt_line == ':R(Bohr):\n':
            cur_step += 1
            if cur_step == step:
                geopt_line = geopt_file.readline()
                while coord_regex.match(geopt_line):
                    coord_block += (geopt_line[:-1] + ' F F F\n')
                    geopt_line = geopt_file.readline()
        geopt_line = geopt_file.readline()
    geopt_file.close()

    # Build POSCAR text and write to POSCAR file
    poscar_text = ''
    for species in species_dict:
        poscar_text += (species + ' ')
    poscar_text += '\n0.52917721056\n'
    poscar_text += ' '.join(vec_1) + '\n'
    poscar_text += ' '.join(vec_2) + '\n'
    poscar_text += ' '.join(vec_3) + '\n'
    for species in species_dict:
        poscar_text += (str(species_dict[species]) + ' ')
    poscar_text += '\nSelective dynamics\nCartesian\n'
    poscar_text += coord_block
    poscar_file = open('POSCAR', 'w')
    poscar_file.write(poscar_text)
    poscar_file.close()


geopt_and_out_to_poscar()
