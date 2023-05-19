### paths and file names often required by ipynb plotting scripts ###

HOMEdir = "/home/m/m300950"
path2sds = HOMEdir+"/superdrops_in_action"
path2build = HOMEdir+"/CLEO/build"
path2dataset = path2build+"/bin"

gridfile = path2build+"/share/dimlessGBxboundaries.dat"
setuptxt = path2dataset+"/testsetup.txt"
dataset = path2dataset+"/testSDMdata.zarr"

stem = ""
savedir = path2sds+"/quickplots/"+stem+"plots/"

print("build: "+path2build+"\ndataset: "+dataset+"\nsavedir: "+savedir)