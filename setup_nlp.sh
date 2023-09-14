#!/bin/bash

# Assuming your zip files are inside the nlp/ folder.
# Change the file names accordingly if they are different.

# Unzip file1.zip and rename to nlp1
unzip nlp/nlp1.zip -d temp_folder && mv temp_folder/* nltk_data/ && rm -r temp_folder

# Unzip file2.zip and rename to nlp2
unzip nlp/nlp2.zip -d temp_folder && mv temp_folder/* nltk_data/ && rm -r temp_folder
