### paths and file names often required by ipynb plotting scripts ###

# HOMEdir = "/home/m/m300950"
# path2sds = HOMEdir+"/superdrops_in_action"
# path2build = HOMEdir+"/CLEO/build/"
# path2dataset = path2build+"/bin/"
# gridfile = path2build+"/share/dimlessGBxboundaries.dat"
# setuptxt = path2dataset+"/setup.txt"
# dataset = path2dataset+"/SDMdata.zarr"
# stem = ""
# savedir = path2sds+"/quickplots/"+stem+"plots/"


HOMEdir = "/home/m/m300950"
path2sds = HOMEdir+"/superdrops_in_action/"
path2build = "/work/mh1126/m300950/prescribed2dflow/conv1/build/"

exp = "n64"
savedir = path2sds+"prescribed2dflow/conv1/"+exp+"/ensemb/"
print("builddir: "+path2build+"\nsavedir: "+savedir)

class DatasetPaths:
  def __init__(self):
        
    path2dataset = path2build+"../bin/"+exp+"/"
    
    self.gridfile = path2build+"/share/dimlessGBxbounds.dat"
    self.setuptxt = path2dataset+"/run9setup.txt"
    self.dataset = path2dataset+"/run9SDMdata.zarr"
    
    print("dataset: "+self.dataset,
          "\ngridfile: "+self.gridfile,
          "\nsetup: "+self.setuptxt)

class EnsembPaths:
  def __init__(self):
      
    self.ensembdir = path2build+"../bin/"+exp+"/ensemb/" 
    self.gridfile = path2build+"/share/dimlessGBxbounds.dat"
    self.setuptxt = self.ensembdir+"../run0setup.txt"
    
    print("ensembdir: "+self.ensembdir,
          "\ngridfile: "+self.gridfile,
          "\nsetup: "+self.setuptxt)