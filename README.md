# Padilla-Coreano Lab's Animal Pose Tracking Respository

## Summary

Main repository for Padilla-Coreano Lab's projects that use Animal Pose Tracking programs such as SLEAP.

## Resources
- https://sleap.ai/index.html

Directory Overview: 

- feature_extraction_sleap.ipynb (author MC): 
    - calculates distances, velocities, angles etc. by creating a class for h5 files for SLEAP tracked videos (a few 2d only functions for tube test)
    - feature visualization functions that displays pose position and feature value overlaid on randomly sampled frames for calculated features  
    - creates gifs from videos for clusters from unsupervized clustering techniques
    - plots ethograms and other behavior bouts (based on cluster) graphs
- results > sleap_analysis: 
    - tubetest_analysis.ipynb: old notebook that plays with sleap h5 files and visualization of tracks as well as attempting to manually define a push, author MIC 
    - UMAP_tubetest.ipynb: attempts to do UMAP unsupervized clustering on tube test data (unsuccessfully) and attempts to make videos of clustered data 
    - aidan_fxn.ipynb: author AH, function to create a 2D array of start and stop frames for which a given feature passes a given threshold. The output is an array of two element arrays, where the first value is the start frame and the second value is the stop frame
- src > .gitkeep 
- bin > sleap command to install sleap 
- training_profiles: sleap models
- sleap_env: idk why this is here 

    