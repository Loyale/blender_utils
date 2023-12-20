import bpy
import blender_plots as bplt
import anndata as ad
import scanpy as sc
from matplotlib import cm

def read_adata(h5ad_file):
    """Reads anndata file and returns the adata object"""
    adata = ad.read_h5ad(h5ad_file)
    return adata

def color_map(adata,feature=None,cmap='viridis'):
    map = cm.get_cmap(cmap)
    if feature in adata.var.columns:
        colors = map(adata.var[feature])
    elif feature in adata.obs.columns:
        colors = map(adata.obs[feature])
    return colors
    
def umap_3d(adata):
    sc.tl.umap(adata, n_components=3,)
    return adata

def plot_umap_3d(adata,feature=None):
    if feature is None:
        feature = adata.var_names[0]
    bplt.Scatter(adata.obsm['X_umap'],color=adata.obs[feature],)
    return