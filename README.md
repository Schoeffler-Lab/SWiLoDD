# Instructions for Running SWiLoDD
### Version Requirements
This version of the code works with the following python and python package versions:
python 3.11.8
pandas 2.0.3
numpy 1.24.3
scipy 1.11.1
bokeh 3.2.1

Other versions might work, but haven't been fully tested. 

### Setup and run instuctions

1) Download or clone this repository.
   
2) Move or copy the directory containing the FASTA files you wish to analyze into the `SWiCAM_v1.1-main` directory, in a sub-directory named 'aligns'.

3) Open a command line interface and change your working directory to the sliding-window-analysis directory, for example

        cd example/path/to/directory/SWiLoDD-main

4) Run the program, from within your SWiLoDD directory, as follows:

    python3 run.py path_to_data target window_size n_largest --stride

For example, to look for asparagine enrichments in a 20-residue sliding window with a 5-residue stride:

    python3 run.py aligns/ N 20 50 --stride 5

Or, to look for aspartate and glutamate enrichments in 9-residue sliding widow with a default stride (1):

    python3 run.py aligns/ DE 9 50

5) The program will output raw and collated data to folders called

      results/plots

      results/processed_data
   
   Within this folder, there will be csv files containing raw window frequencies for every sequence in the alignment.
   There will also be a folder containing interactive plots of the average frequencies and the delta average frequencies.
   If you would like to make a publication-quality plot of the delta average frequencies, please see our SWiLoDD Delta Plot Visualizer script on GitHub.
   (https://github.com/Schoeffler-Lab/SWiCAM_Delta_Plot.git )
