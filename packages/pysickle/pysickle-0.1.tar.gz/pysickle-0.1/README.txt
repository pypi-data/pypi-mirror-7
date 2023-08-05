===========
Pysickle
===========

**pysickle.py** will try to remove sequences that cause misalignments from a multiple sequence alignment (MSA). It reads a given MSA in multi-fasta format and removes sequences with the highest penalty scores, then builds the next MSA without those sequences. This process is repeated until a user-specified cuttoff is reached or less than three sequences are left to be aligned.

Usage::
    
    ######################################
    # pysickle.py
    ######################################
    usage:
        pysickle.py -f multifasta alignment
    options:
        -f, --fasta=FILE    multifasta alignment (eg. "align.fas")
        OR
        -F, --fasta_dir=DIR directory with multifasta files (needs -s SUFFIX)
        -s, --suffix=SUFFIX will try to work with files that end with SUFFIX (eg ".fas")

        -a, --msa_tool=STR  supported: "mafft" [default:"mafft"]
        -i, --max_iterations=NUM    force stop after NUM iterations
        -n, --num_threads=NUM   max number of threads to be executed in parallel [default: 1]
        -m, --mode=MODE         set strategy to remove outlier sequences [default: "Sites"]
                                available modes (not case sensitive):
                                    "Sites", "Gaps", "uGaps","Insertions",
                                    "uInsertions","uInstertionsGaps", "custom"
        -l, --log       write logfile
        -h, --help      prints this

    only for mode "custom":
        -g, --gap_penalty=NUM        set gap penalty [default: 1.0]
        -G, --unique_gap_penalty=NUM set unique gap penalty [default: 10.0]
        -j, --insertion_penalty=NUM  set insertion penalty [default:1.0]
        -J, --unique_insertion_penalty=NUM set insertion penalty [default:1.0]
        -M, --mismatch_penalty=NUM   set mismatch penalty [default:1.0]
        -r, --match_reward=NUM       set match reward [default: -10.0]


Currently supported multiple sequence aligners:

- mafft (Katoh, Standley 2013 (Molecular Biology and Evolution 30:772-780) MAFFT multiple sequence alignment software version 7: improvements in performance and usability. http://mafft.cbrc.jp/alignment/software/)


Requirements
============
* matplotlib
* numpy

External Programs
-----------------
* mafft


