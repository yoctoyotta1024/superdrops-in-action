### ---------------------- REMOTE VERSION ----------------------- ###
### paths and file names often required by ipynb plotting scripts ###

HOMEdir = "/home/m/m300950"
path2sds = HOMEdir+"/superdrops_in_action/"
path2build = "/work/mh1126/m300950/prescribed2dflow/build/"
#path2build = "/home/m/m300950/CLEO/build/"

expdir, rundir = "/conc1e9_res50/", "/n2/run14"
# savedir = path2sds+"prescribed2dflow/convstudy/"+expdir+rundir+"/"
savedir = path2sds+"prescribed2dflow/convstudy/"+expdir+"/compareplots/"
print("builddir: "+path2build+"\nsavedir: "+savedir)

class DatasetPaths:
  def __init__(self):
        
    # path2dataset = path2build+"/bin/"
    # self.gridfile = path2build+"/share/dimlessGBxboundaries.dat"
    # self.setuptxt = path2dataset+"/setup.txt"
    # self.dataset = path2dataset+"/SDMdata.zarr"
    path2dataset = path2build+"../"+expdir+rundir
    self.gridfile = path2build+"/share/"+expdir+"/dimlessGBxbounds.dat"
    self.setuptxt = path2dataset+"setup.txt"
    self.dataset = path2dataset+"SDMdata.zarr"
     
    print("dataset: "+self.dataset,
          "\ngridfile: "+self.gridfile,
          "\nsetup: "+self.setuptxt)

class EnsembPaths:
  def __init__(self):
    
    exp = "/n8/"
    self.path2ensemb = path2build+"../"+expdir+exp+"/ensemb/" 
    self.gridfile = path2build+"/share/"+expdir+"/dimlessGBxbounds.dat"
    self.setuptxt = self.path2ensemb+"../run0setup.txt"
    
    print("ensembdir: "+self.path2ensemb,
          "\ngridfile: "+self.gridfile,
          "\nsetup: "+self.setuptxt)

class ExperimentsPaths:
  def __init__(self):
    
    # self.exps = ["n2", "n4", "n8", "n16", "n32", "n64", "n128", "n512"]
    self.exps = ["n2", "n4", "n8", "n16", "n32", "n512"]
    self.nruns = 15

    self.saveexpsdir, self.ensembdirs = {}, {}
    for exp in self.exps:
      self.saveexpsdir[exp] = path2sds+"prescribed2dflow/convstudy/"+expdir+exp+"/"
      self.ensembdirs[exp] = path2build+"../"+expdir+exp+"/ensemb/" 
    
    self.gridfile = path2build+"/share/"+expdir+"/dimlessGBxbounds.dat"
    self.setuptxt = self.ensembdirs[self.exps[0]]+"../run0setup.txt" # use setuptxt from 1st run of 1st experiment

    print("experiments: ",self.exps,
          "\nensembdirs: ", ",\n".join([dir for dir in self.ensembdirs.values()]),
          "\ngridfile: "+self.gridfile,
          "\nsetup: "+self.setuptxt)

# ### ---------------------- LOCAL VERSION ------------------------ ###
# ### paths and file names often required by ipynb plotting scripts ###

# HOMEdir = "/Users/yoctoyotta1024/Documents/b1_springsummer2023/"
# path2sds = HOMEdir+"/superdrops_in_action/"
# path2build = HOMEdir+"/CLEO/build/"

# exp = "n2"
# savedir = path2sds+"/quickplots/plots/"
# print("builddir: "+path2build+"\nsavedir: "+savedir)

# class DatasetPaths:
#   def __init__(self):
        
#     path2dataset = path2build+"/bin/"
#     self.gridfile = path2build+"/share/dimlessGBxboundaries.dat"
#     self.setuptxt = path2dataset+"/run0setup.txt"
#     self.dataset = path2dataset+"/run0SDMdata.zarr"
    
#     print("dataset: "+self.dataset,
#           "\ngridfile: "+self.gridfile,
#           "\nsetup: "+self.setuptxt)

# class EnsembPaths:
#   def __init__(self):
      
#     self.ensembdir = path2build+"/bin/"+exp+"/" 
#     self.gridfile = path2build+"/share/dimlessGBxbounds.dat"
#     self.setuptxt = self.ensembdir+"/run0setup.txt"
    
#     print("ensembdir: "+self.ensembdir,
#           "\ngridfile: "+self.gridfile,
#           "\nsetup: "+self.setuptxt)

# class ExperimentsPaths:
#   def __init__(self):
    
#     self.exps = ["n8"]
    
#     self.saveexpsdir, self.ensembdirs = {}, {}
#     for exp in self.exps:
#       self.saveexpsdir[exp] = path2sds+"prescribed2dflow/convstudy/"+expdir+exp+"/"
#       self.ensembdirs[exp] = path2build+"/bin/"+expdir+exp+"/ensemb/" 
    
#     self.gridfile = path2build+"/share/dimlessGBxbounds.dat"
#     self.setuptxt = path2build+"/bin/"+self.exps[0]+"/run0setup.txt" # use setuptxt from 1st run of 1st experiment

#     print("experiments: ",self.exps,
#           "\nensembdirs: ", ",\n".join([dir for dir in self.ensembdirs.values()]),
#           "\ngridfile: "+self.gridfile,
#           "\nsetup: "+self.setuptxt)