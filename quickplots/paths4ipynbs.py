### paths and file names often required by ipynb plotting scripts ###

HOMEdir = "/home/m/m300950"
path2sds = HOMEdir+"/superdrops_in_action"
# path2build = HOMEdir+"/CLEO/build"
path2build = path2sds+"/quickplots/condensationmethod/shimacrit1/"
path2dataset = path2build+"matsu_10iters/bin"

gridfile = path2build+"/share/dimlessGBxboundaries.dat"
setuptxt = path2dataset+"/setup.txt"
dataset = path2dataset+"/SDMdata.zarr"

stem = "test"
# savedir = path2sds+"/quickplots/"+stem+"plots/"
savedir = path2sds+"/quickplots/condensationmethod/shimacrit1/matsu_10iters/plots/"

print("build: "+path2build+"\ndataset: "+dataset+"\nsavedir: "+savedir)