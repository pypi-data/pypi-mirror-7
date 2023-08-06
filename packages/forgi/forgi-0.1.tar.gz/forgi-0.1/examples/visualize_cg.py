#!/usr/bin/python

import numpy as np
import sys
import subprocess as sp
import tempfile as tf

import forgi.threedee.model.coarse_grain as cmg
import forgi.utilities.debug as fud
import forgi.threedee.utilities.graph_pdb as ftug
import forgi.threedee.utilities.pdb as cup
import forgi.threedee.utilities.rmsd as ftur
import forgi.threedee.utilities.vector as ftuv
import forgi.threedee.visual.pymol as cvp

from optparse import OptionParser

def align_cgs(cgs):
    '''
    Align each coarse grain RNA to the first one.

    The points representing each coarse grain RNA molecule
    will be the virtual residues.
    
    @param cgs: A list of CoarseGrainRNA structures.
    @return: Nothing, the cgs are modified in place
    '''
    centroid0 = ftuv.get_vector_centroid(ftug.bg_virtual_residues(cgs[0]))
    crds0 = ftuv.center_on_centroid(ftug.bg_virtual_residues(cgs[0]))

    for cg in cgs:
        centroid1 = ftuv.get_vector_centroid(ftug.bg_virtual_residues(cg))
        crds1 = ftuv.center_on_centroid(ftug.bg_virtual_residues(cg))

        rot_mat = ftur.optimal_superposition(crds0, crds1)
        for k in cg.coords.keys():
            cg.coords[k] = (np.dot(rot_mat, cg.coords[k][0] - centroid1),
                            np.dot(rot_mat, cg.coords[k][1] - centroid1))

            if k[0] == 's':
                cg.twists[k] = (np.dot(rot_mat, cg.twists[k][0]),
                                np.dot(rot_mat, cg.twists[k][1]))


def main():
    usage = """
    ./visualize_cg.py cg_file

    Display the coarse-grain representation of a structure in pymol.
    """
    num_args= 0
    parser = OptionParser(usage=usage)

    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')
    parser.add_option('-o', '--output', dest='output', default=None, help="Create a picture of the scene and exit", type='str')
    parser.add_option('-r', '--longrange', dest='longrange', default=False, action='store_true', help="Display long-range interactions")
    parser.add_option('-l', '--loops', dest='loops', default=True, action='store_false', help="Don't display the coarse-grain hairpin loops")
    parser.add_option('-c', '--cones', dest='cones', default=False, action='store_true', help="Display cones that portrude from the stems")
    parser.add_option('-x', '--text', dest='text', default=False, action='store_true', help="Add labels to the figure.")
    parser.add_option('-a', '--align', dest='align', default=False, action='store_true', help='Align all of the structures with the first')
    parser.add_option('-e', '--encompassing-stems', dest='encompassing_stems', default=False, action='store_true', help='Show the big stems that encompass the colinear ones.')
    parser.add_option('-v', '--virtual-atoms', dest='virtual_atoms', default=False, action='store_true', help='Display the virtual atoms')
    parser.add_option('-b', '--basis', dest='basis', default=False, action='store_true', help='Display the coordinate basis of each element')
    parser.add_option('', '--stem-atoms', dest='stem_atoms', default=False, action='store_true', help='Display the stem atoms')
    parser.add_option('', '--rainbow', dest='rainbow', default=False, action='store_true', help='Color each of the nucleotide positions (i.e. average atoms) according to the colors of the rainbow and their position')

    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        sys.exit(1)

    pp = cvp.PymolPrinter()
    pp.add_loops = options.loops
    pp.draw_cones = options.cones
    #sys.exit(1)
    pp.add_longrange = options.longrange
    pp.print_text = options.text
    pp.encompassing_stems = options.encompassing_stems
    pp.virtual_atoms = options.virtual_atoms
    pp.basis = options.basis
    pp.rainbow = options.rainbow

    cgs = []
    for a in args:
        cgs += [cmg.from_file(a)]

    if options.align:
        align_cgs(cgs)

    for i,cg in enumerate(cgs):
        if i > 0:
            pp.color_modifier = .3
            #pp.override_color = 'middle gray'


        pp.coordinates_to_pymol(cg)

    for d in cg.defines:
        if d[0] == 'i' or d[0] == 's' or d[0] == 'm':
            if options.stem_atoms:
                side = 0
                if d[0] == 'm':
                    side = cg.get_strand(d)

                    pp.stem_atoms(cg.coords[d], cg.get_twists(d), 
                                  cg.get_node_dimensions(d)[0], side=side)
                elif d[0] == 's':
                    for side in range(2):
                        pp.stem_atoms(cg.coords[d], cg.get_twists(d), 
                                    cg.get_node_dimensions(d)[0], side=side)


    with tf.NamedTemporaryFile() as f:
        with tf.NamedTemporaryFile(suffix='.pml') as f1:
            f.write(pp.pymol_string())
            f.flush()

            pymol_cmd = 'hide all\n'
            pymol_cmd += 'run %s\n' % (f.name)
            pymol_cmd += 'show cartoon, all\n'
            pymol_cmd += 'bg white\n'
            pymol_cmd += 'clip slab, 10000\n'

            if options.output is not None:
                pymol_cmd += 'ray\n'
                pymol_cmd += 'png %s\n' % (options.output)
                pymol_cmd += 'quit\n'


            f1.write(pymol_cmd)
            f1.flush()

            p = sp.Popen(['pymol', f1.name])
            out, err = p.communicate()

if __name__ == '__main__':
    main()

