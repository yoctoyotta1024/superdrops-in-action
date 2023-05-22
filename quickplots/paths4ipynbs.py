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
path2build = "/work/mh1126/m300950/prescribed2dflow/ssvar/build/"
gridfile = path2build+"/share/dimlessGBxbounds.dat"

path2dataset = path2build+"../bin/ss0p65_1p0/"
setuptxt = path2dataset+"/run0setup.txt"
dataset = path2dataset+"/run0SDMdata.zarr"

stem = "test"
savedir = path2sds+"prescribed2dflow/ssvar/ss0p65_1p0/"+stem+"plots/"

print("build: "+path2build+"\ndataset: "+dataset+"\nsavedir: "+savedir)