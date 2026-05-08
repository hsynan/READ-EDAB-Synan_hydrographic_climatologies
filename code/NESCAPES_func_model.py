# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 13:21:42 2025

@author: haley.synan

"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import os
import cartopy
import warnings
from scipy.cluster.hierarchy import cut_tree
import seaborn as sns
warnings.filterwarnings('ignore', category=DeprecationWarning)

import pickle
# Load the dictionary from the file
with open(r"W:\nadata\PROJECTS\NESCAPES\CODE\hyper_params.pickle", "rb") as hyper_param:
    hyper_param = pickle.load(hyper_param)

def buffer_clip(data: (gpd.GeoDataFrame, pd.DataFrame), shp: gpd.GeoDataFrame, buff_dist, inside = 'no',projection="EPSG:4326", latname: str='latitude',lonname: str='longitude'):
    """
    PURPOSE: 
        Create a buffer around a shapefile and clip data. Returns clipped data INSIDE or OUTSIDE the buffered shapefile.
        NOTE - this is not currently available to apply to xarray datasets.
    REQUIRED INPUT: 
        Data (dataframe, geodataframe): Data to be clipped
        Shp (geodataframe): Shapefile for clipping  
    OPTIONAL INPUT: 
        Inside (str): 'yes' or 'no'. "yes" returns the data within the buffered shapefile. "no" returns the data NOT in the buffered shapefile. ]
                    (Sample application: get rid of near coastal data by buffering a coastline shapefile). Default is 'no'
        Projection (str): projection (formatted as EPSG code) for the returned data. Default is WGS84 (world geodetic system 1984)
        Latname (str): variable name for latitude. Default is latitude
        Lonname (str): variable name for longitude. Default is longitude
    HISTORY:
        11/6/24: function initialized for xarray datasets
        6/3/25: updated functionality for geodataframe
    """
    if isinstance(data,pd.DataFrame):
        gdf = gpd.GeoDataFrame(
        data, geometry=gpd.points_from_xy(data[lonname], data[latname]), crs=projection) #turn dataframe into geodataframe 
        in_shp = gpd.clip(gdf,shp.buffer(buff_dist))
    elif isinstance(data, gpd.GeoDataFrame):
        in_shp = gpd.clip(gdf,shp.buffer(buff_dist), crs=projection)
    if inside == 'no':
        buffered = data[~data.isin(in_shp)].dropna()
        return buffered
    if inside == 'yes':
        return in_shp


def log_chla(data):
    """
     PURPOSE: 
        Log 10 chlorophyll values
    REQUIRED INPUT: 
        Data (dataframe): Data with chlorophyll variables in it
    OPTIONAL INPUT: 
        None
    HISTORY:
        6/6/25: Function initialized
    """
    var = [var for var in data.columns.tolist() if 'chl' in var]
    for v in var:
        data[v] = np.log10(data[v])
    return data


def get_vars(data, monthly=True):
    """
     PURPOSE: 
        Get variables to determine formatting of data for the SOM.
    REQUIRED INPUT: 
        Data (dataframe): Data (should be formatted with monthly variables as separate columns)
    OPTIONAL INPUT: 
        Monthly (binary): How do you want the data formatted? Monthly - month variables are in columns, not monthly - month variables are in the rows
    HISTORY:
        6/6/25: Function initialized from code
    """
    if monthly == True:
        clustering_vars = data.columns.tolist()
        clustering_vars.remove('latitude') #remove lat and lon as input variables
        clustering_vars.remove('longitude')
        try:
            clustering_vars.remove('Unnamed: 0')
        except:
            pass
        try:
            clustering_vars.remove('Unnamed: 0.1')
        except:
            pass
    else: 
        ct = pd.concat([data[var] for var in data.columns.tolist() if 'CT' in var])
        sa = pd.concat([data[var] for var in data.columns.tolist() if 'SA' in var])
        rho = pd.concat([data[var] for var in data.columns.tolist() if 'rho' in var])
        chl = pd.concat([data[var] for var in data.columns.tolist() if 'chlor_a' in var])
        lat= data.latitude.tolist() * 12
        lon = data.longitude.tolist() * 12
        month = []
        for x in range(1,13):
            month.extend([x]*len(data.latitude))
        data = pd.DataFrame({'latitude':lat,'longitude':lon,'CT':ct, 'SA':sa,'rho':rho,'chla':chl,'month':month})
        clustering_vars = ['CT','SA','rho','chla']
    return data, clustering_vars
    


def normalize(data,clustering_vars, monthly=True):
    """
     PURPOSE: 
        Normalize input data for SOM 
    REQUIRED INPUT: 
        Data (dataframe): Formatted dataframe
    OPTIONAL INPUT: 
        Monthly (binary): Data format. Monthly - month variables are in columns, not monthly - month variables are in the rows
    HISTORY:
        6/6/25: Function initialized from code 
    """
    from sklearn.preprocessing import MinMaxScaler
    # MinMax scaled
    scaler = MinMaxScaler(feature_range=(-1,1))
    scaler.fit(data[clustering_vars])
    dat = scaler.transform(data[clustering_vars])
    dat= pd.DataFrame(dat,index=data.index)
    N = len(data)
    dataa = dat.to_numpy()
    return dataa, scaler


from sompy.sompy import SOMFactory
from matplotlib.colors import ListedColormap
from scipy.cluster.hierarchy import linkage, dendrogram
def train_som(dataa,clustering_vars,msz=hyper_param['msz'],rough_len=hyper_param['rough_len'], fine_len =hyper_param['fine_len']):
    """
     PURPOSE: 
        Train SOM 
    REQUIRED INPUT: 
        Data (np array): Normalized data as array
        Clustering_vars: list of string of variables to train on 
    OPTIONAL INPUT: 
        Msz (
    HISTORY:
        6/6/25: Function initialized from code 
    """
    sm = SOMFactory().build(dataa, mapsize = msz, normalization = None, component_names=clustering_vars,initialization='pca',)
    sm.train(n_job=1, verbose=False, train_rough_len=rough_len, train_finetune_len=fine_len)
    return sm

from sklearn.cluster import AgglomerativeClustering
def wss_calculation(K, data):
    """
     PURPOSE: 
        Calculate the within(cluster) sum of squares to determine the optimal number of clusters. Code is from https://jbhender.github.io/Stats506/F18/GP/Group15.html
    REQUIRED INPUT: 
        K (int): number of clusters to test (ex: if K = 15, test 2-15 clusters)
        data (numpy array): matrix of data to perform calculation on
    OPTIONAL INPUT: 
        None
    HISTORY:
        8/28/24: Function initialized from code 
    """
    WSS = []
    for i in range(K):
        cluster = AgglomerativeClustering(n_clusters= i+1, metric='euclidean', linkage='average')  
        cluster.fit_predict(data)
        # cluster index
        label = cluster.labels_
        wss = []
        for j in range(i+1):
            # extract each cluster according to its index
            idx = [t for t, e in enumerate(label) if e == j]
            cluster = data[idx,]
            # calculate the WSS:
            cluster_mean = cluster.mean(axis=0)
            distance = np.sum(np.abs(cluster - cluster_mean)**2,axis=-1)
            wss.append(sum(distance))
        WSS.append(sum(wss))
    return WSS

def plt_wss(clustering, K=20):
    """
     PURPOSE: 
        Visualize within clusters sum of squares to 
    REQUIRED INPUT: 
        clustering (): Data after applying hierarchical agglomerative clustering
    OPTIONAL INPUT: 
        K (int): max number of clusters to test
    HISTORY:
        6/9/25: Function initialized from code 
    """
    WSS=wss_calculation(K, clustering)
    cluster_range = range(1, K+1)
    plt.figure(figsize=(10,5))
    plt.title('Within cluster sum of squares elbow plot')
    plt.xlabel('Number of cluster (k)')
    plt.ylabel('Total intra-cluster variation')
    plt.plot(cluster_range, WSS, marker = "x")
    return plt

def plt_dendro(clustering,yline=None):
    """
     PURPOSE: 
        Plot dendrogram from results of hierarchical agglomerative clustering
    REQUIRED INPUT: 
        clustering (): Data after applying hierarchical agglomerative clustering
    OPTIONAL INPUT: 
        yline (int): height (in inches) to put a horizontal line to represent where the hierarchy was cut and number of clusters retained
    HISTORY:
        6/9/25: Function initialized from code 
    """
    fig = plt.figure(figsize=(10, 7)) #set figure size
    dendrogram(clustering, truncate_mode = 'level', p = 4,above_threshold_color='blue', color_threshold=5, show_leaf_counts=True,leaf_font_size=7 )
    plt.title('Dendrogram')
    #plt.text(5, 27, '*Truncated to show last 4 levels', fontsize = 8)
    # specifying horizontal line type 
    try:
        plt.axhline(y = yline, color = 'r', linestyle = '-') 
    except:
        pass
    plt.xlabel('Leaf Counts')
    plt.ylabel('Cluster distance')
    plt.show()
    return plt

def get_clus_labels(data, clustering_vars, bmu, cluster_labels):
    """
     PURPOSE: 
        Apply cluster labels from the HAC to the original data / bmus
    REQUIRED INPUT: 
        Data (numpy array): matrix of data
        Clustering_vars ():
        Bmu (): bmus corresponding to each data point 
    OPTIONAL INPUT: 
        None
    HISTORY:
        6/9/25: Function initialized from code 
    """
    if 'latitude' in clustering_vars:
        pass
    else: 
        clustering_vars.append('latitude')
        clustering_vars.append('longitude')
    
    dd = data[clustering_vars].dropna()
    dd.insert(0,'bmu',bmu[0])
    dd = dd.reset_index()
    labels = []
    for x in range(len(dd)):
        labels.append(cluster_labels[int(dd.bmu[x])])
    dd.insert(2,'HAC',labels)
    return dd 

def summary_stats(model_results):
    """
     PURPOSE: 
        Apply cluster labels from the HAC to the original data / bmus
    REQUIRED INPUT: 
        Res (dataframe): dataframe with HAC results 
    OPTIONAL INPUT: 
        None
    HISTORY:
        6/9/25: Function initialized from code 
    """
    temp = []
    sal = []
    rho = []
    res = model_results['res']
    for x in range(model_results['n_clusters']):
        temp.append(res[res.HAC==x][res.columns[np.where(res.columns.to_series().str.contains('CT'))]])
        sal.append(res[res.HAC==x][res.columns[np.where(res.columns.to_series().str.contains('SA'))]])
        rho.append(res[res.HAC==x][res.columns[np.where(res.columns.to_series().str.contains('rho'))]])
    
    summary= pd.DataFrame({'CT_annual_mean':[x.mean().mean() for x in temp], 'CT_annual_min':[x.min().min() for x in temp], 'CT_annual_max':[x.max().max() for x in temp],
                  'SA_annual_mean':[x.mean().mean() for x in sal], 'SA_annual_min':[x.min().min() for x in sal], 'SA_annual_max':[x.max().max() for x in sal],
                  'rho_annual_mean':[x.mean().mean() for x in rho], 'rho_annual_min':[x.min().min() for x in rho], 'rho_annual_max':[x.max().max() for x in rho]})
    summary.style.set_caption('<div style="text-align:center; font-size: 20px;">Summary statistics for final clusters</div>')
    summary['clus_num'] = np.arange(1,len(summary)+1)
    summary.set_index('clus_num')
    return summary 

from matplotlib.colors import ListedColormap
from shapely.ops import unary_union
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter
import matplotlib.ticker as mticker
    
def plot_map(res, n_clusters, monthly=True):
    """
     PURPOSE: 
        Plot resulting clusters on map. If monthly=False, will plot by month. If monthly=True, will only plot 1 one image (as it doesn't change monthly).
        Default is monthly=True
    REQUIRED INPUT: 
        Res (dataframe): dataframe with HAC results 
        N_clusters (int): number of final clusters 
    OPTIONAL INPUT: 
        Monthly (binary): Data format. Monthly - month variables are in columns, not monthly - month variables are in the rows
    HISTORY:
        6/9/25: Function initialized from code 
    """
    bathym = cfeature.NaturalEarthFeature(name='bathymetry_K_200', scale='10m', category='physical')
    bathym = unary_union(list(bathym.geometries()))
    cm = plt.get_cmap('jet', n_clusters) #choose colorbar
    if monthly == True: 
        fig = plt.figure(figsize=(12, 8)) #set figure size
        map_projection = cartopy.crs.PlateCarree() #set map projection
        ax = plt.axes(projection=map_projection) 
        im = plt.scatter(res.longitude,res.latitude, c=res.HAC,cmap =cm,s=44,marker='s' ) #plot
        cb = plt.colorbar(im,label='Cluster Number' ,shrink=0.92) #add colorbar
        cb.ax.set_yticks(np.arange(0,n_clusters).tolist()) #set ticks to every int
        cb.ax.set_yticklabels(np.arange(1,n_clusters+1).tolist()) #set tick labels to start from 1 (rather than 0)
        ax.add_feature(cartopy.feature.COASTLINE, linewidth=1) #add coastlines
        #ax.add_feature(cartopy.feature.LAND, zorder=100, facecolor='lightgrey') #add land mask 
        ax.add_geometries(bathym, facecolor='none', edgecolor='black', crs=cartopy.crs.PlateCarree()) #add bathymetry line
        ax.set_extent([-75.6, -63.8, 35, 47])
        plt.title('Clusters from trained model')
        return plt
    else: 
        fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(12, 7),
                         subplot_kw={'projection': cartopy.crs.PlateCarree()})
        for month_num in range(1, 13):
            # Select data for the current month
            sub = res[res.month == month_num]
            ax = axes.flatten()[month_num - 1]
            ax.set_title(f'Month {month_num}')  # Set the title for each subplot
            im = ax.scatter(sub.longitude, sub.latitude, c=sub.HAC,cmap =cm,s=10,marker='s' ) 
            #gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')
            #gl.xlabel_style = {'rotation': 45}
            #gl.ylabel_style = {'rotation': 45}
            ax.add_feature(cartopy.feature.COASTLINE, linewidth=1) #add coastlines
            ax.add_feature(cartopy.feature.LAND, zorder=100, facecolor='lightgrey') #add land mask 
            ax.set_extent([-75.6, -63.8, 35, 44.85])
            ax.add_geometries(bathym, facecolor='none', edgecolor='black', crs=cartopy.crs.PlateCarree()) #add bathymetry line
        fig.subplots_adjust(right=0.8)
        cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
        cb =fig.colorbar(im, cax=cbar_ax)
        cb.ax.set_yticks(np.arange(0,n_clusters).tolist()) #set ticks to every int
        cb.ax.set_yticklabels(np.arange(1,n_clusters+1).tolist()) #set tick labels to start from 1 (rather than 0)
        return fig

import sklearn as sk
def validity_tests(nodes, cluster_labels):
    """
     PURPOSE: 
        Run clustering validity tests on data/results
    REQUIRED INPUT: 
        Nodes (np array): centers of each nodes from SOM 
        Cluster_labels (np array): array of cluster labels
    OPTIONAL INPUT: 
        None
    HISTORY:
        6/9/25: Function initialized from code 
    """
    avgsilh = sk.metrics.silhouette_score(nodes, cluster_labels)
    #Calinski Harabasz (higher = better)
    from sklearn import metrics
    from sklearn.metrics import pairwise_distances
    chi = metrics.calinski_harabasz_score(nodes, cluster_labels)
    #Davies Bouldin (closer to 0 = better)
    from sklearn.metrics import davies_bouldin_score
    db = davies_bouldin_score(nodes, cluster_labels)
    return avgsilh, chi, db

import pickle
def save_model(nodes,res,clustering_vars,sm,data, scaler):
    """
     PURPOSE: 
        Apply cluster labels from the HAC to the original data / bmus
    REQUIRED INPUT: 
        Res (dataframe): dataframe with HAC results 
        Nodes (np array): centers of each nodes from SOM 
        Clustering_vars (list): list of variable names that were used in training
        Data (array): original training data
    OPTIONAL INPUT: 
        None
    HISTORY:
        6/9/25: Function initialized from code 
    """
    results={'nodes':nodes,
                   'res':res,
            'clustering_vars':clustering_vars,
            'normalizer':scaler,
            'sm':sm,
            'not_norm_train_dat':data[clustering_vars].drop(['latitude','longitude'],axis=1),
            'data':data}
    # Save the dictionary to a file
    with open("model_results.pickle", "wb") as model_results:
        pickle.dump(results, model_results)