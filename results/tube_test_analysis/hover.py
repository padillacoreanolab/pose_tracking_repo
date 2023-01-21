# %%
import h5py
import numpy as np
import umap
import hdbscan
import sklearn.cluster as cluster
from sklearn.metrics import adjusted_rand_score, adjusted_mutual_info_score

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import pickle

from scipy.stats import linregress
from scipy.optimize import curve_fit

from sklearn.datasets import fetch_openml
from sklearn.decomposition import PCA
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


np.set_printoptions(threshold=np.inf)

def save_to_pickle():


    filenames =[
    "./C1_R1v2_ID1v2.mp4.predictions.000_C1_R1v2_ID1v2.analysis_fixed.h5",
    "./C1_R1v4_ID1v3.mp4.predictions.000_C1_R1v4_ID1v3.analysis_fixed.h5",
    "./C2_R1v2_ID1v3.mp4.predictions.000_C2_R1v2_ID1v3.analysis_fixed.h5",
    "./C2_R4v1_ID4v1.mp4.predictions.000_C2_R4v1_ID4v1.analysis_fixed.h5",
    "./C3_R2v1_ID3v4.mp4.predictions.000_C3_R2v1_ID3v4.analysis_fixed.h5",
    "./C3_R1v4_ID4v1.mp4.predictions.000_C3_R1v4_ID4v1.analysis_fixed.h5",
    './C4_R2v1_ID3v2.mp4.predictions.000_C4_R2v1_ID3v2.analysis_fixed.h5',
    "./C4_R1v4_ID2v4.mp4.predictions.000_C4_R1v4_ID2v4.analysis_fixed.h5",
    "./C5_R2v1_ID2v4.mp4.predictions.000_C5_R2v1_ID2v4.analysis_fixed.h5",
    "./C5_R4v1_ID3v4.mp4.predictions.000_C5_R4v1_ID3v4.analysis_fixed.h5",
    "./C6_R1v2_ID1v3.mp4.predictions.slp.000_C6_R1v2_ID1v3.analysis_fixed.h5",
    "./C6_R4v1_ID4v1.mp4.predictions.000_C6_R4v1_ID4v1.analysis_fixed.h5"
    ]

    def get_info(filename):
            with h5py.File(filename, "r") as f:
                dset_names = list(f.keys())
                locations = f["tracks"][:].T
                node_names = [n.decode() for n in f["node_names"][:]]
            return dset_names, locations, node_names

    # %%
    #goal is to combine all locations from all vidoes into one matrix
    #but first lets deal with the missing locations
    from scipy.interpolate import interp1d

    def fill_missing(Y, kind="linear"):
        """Fills missing values independently along each dimension after the first."""

        # Store initial shape.
        initial_shape = Y.shape

        # Flatten after first dim.
        Y = Y.reshape((initial_shape[0], -1))

        # Interpolate along each slice.
        for i in range(Y.shape[-1]):
            y = Y[:, i]

            # Build interpolant.
            x = np.flatnonzero(~np.isnan(y))
            f = interp1d(x, y[x], kind=kind, fill_value=np.nan, bounds_error=False)

            # Fill missing
            xq = np.flatnonzero(np.isnan(y))
            y[xq] = f(xq)
            
            # Fill leading or trailing NaNs with the nearest non-NaN values
            mask = np.isnan(y)
            y[mask] = np.interp(np.flatnonzero(mask), np.flatnonzero(~mask), y[~mask])

            # Save slice
            Y[:, i] = y

        # Restore to initial shape.
        Y = Y.reshape(initial_shape)

        return Y

    # %%
    #iterate through files and concatenate all locations into a location master array 
    #location master array shape (total frames, number of nodes, number of mice, number of coordinate dimensions)
    #location master array shape = (4897,6,2,2)
    def combine_locations(filenames):
        """
        takes in a list a filenames for h5 files that
        you want to concatenate along the frame dimension
        """
        loc_check = []
        is_first = True
        for filename in filenames:
            dset_names, locations, node_names = get_info(filename)
            loc_check.append(locations.shape[0])
            locations = fill_missing(locations)
            if is_first:
                # First array becomes the thing we append to below
                # we don't know the shape ahead of time so this works okay.
                locations_master = locations
                is_first = False
            else:
                locations_master = np.concatenate((locations_master, locations),0)
        return locations_master


    # %%
    loc_master = combine_locations(filenames)

    # %%
    loc_master.shape
    #frames, nodes, coordinates, mice

    # %%
    loc_test = np.reshape(loc_master, (4897, 24), order = 'C')
    loc_test.shape
    #loc_test looks frames in 1D and then iterates through each node, through each mouse, through each coordinate


    reducer = umap.UMAP()
    embedding = reducer.fit_transform(loc_test)
    embedding.shape

    with open('embedding.pickle', 'wb') as f: 
        pickle.dump((embedding, loc_test), f)

def unpickle_embedding():
    with open('embedding.pickle', 'rb') as f:
        data = pickle.load(f)
    return data




# This is to speed up development. We first pickle (save)
# save_to_pickle()
embedding, loc_test = unpickle_embedding()

def display_frame_from_video(frame, video_filename = ""):



### GRAPHING STUFF ####
plt.scatter(
    embedding[:, 0],
    embedding[:, 1])
    #c=[sns.color_palette()[x] for x in penguins.species.map({"Adelie":0, "Chinstrap":1, "Gentoo":2})])
plt.gca().set_aspect('equal', 'datalim')
plt.title('UMAP projection of tube test data', fontsize=24);

# %%
clusterable_embedding = umap.UMAP(
    n_neighbors=30,
    min_dist=0.0,
    n_components=2,
    random_state=42,
).fit_transform(loc_test)

hdbscan_labels = hdbscan.HDBSCAN(min_samples=10, min_cluster_size=500).fit_predict(clusterable_embedding)

print("Printing plot lib")
clustered = (hdbscan_labels >= 0)
fig, ax = plt.subplots()
sc = plt.scatter(clusterable_embedding[clustered, 0],
            clusterable_embedding[clustered, 1],
            c=hdbscan_labels[clustered],
            s=10,
            cmap='Spectral')


annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def update_annot(ind):
    print('ind:')
    print(ind)
    pos = sc.get_offsets()[ind["ind"][0]]
    annot.xy = pos
    text = "{}, {}".format(" ".join(list(map(str,ind["ind"]))), 
                           " ".join([str(n) for n in ind["ind"]]))
    annot.set_text(text)


def hover(event):
    print(event)
    vis = annot.get_visible()
    if event.inaxes == ax:
        cont, ind = sc.contains(event)
        if cont:
            update_annot(ind)
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

fig.canvas.mpl_connect("motion_notify_event", hover)

plt.show()

