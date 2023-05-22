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

exp = "ss0p99_1p0001_1p005"
path2dataset = path2build+"../bin/"+exp+"/"
setuptxt = path2dataset+"/run0setup.txt"
dataset = path2dataset+"/run0SDMdata.zarr"

savedir = path2sds+"prescribed2dflow/ssvar/"+exp+"/"

print("build: "+path2build+"\ndataset: "+dataset+"\nsavedir: "+savedir)