### paths and file names often required by ipynb plotting scripts ###

HOMEdir = "/home/m/m300950"
path2sds = HOMEdir+"/superdrops_in_action"
# path2build = HOMEdir+"/CLEO/build"
# path2build = path2sds+"/quickplots/condensationmethod/newrsqrd_shimacrit1_v2/build/"
path2build = path2sds+"/quickplots/condensationmethod/newrsqrd_shimacrit1_v2_matsusubstepped/build/"
path2dataset = path2build+"/bin"

gridfile = path2build+"/share/dimlessGBxboundaries.dat"
setuptxt = path2dataset+"/setup.txt"
dataset = path2dataset+"/SDMdata.zarr"

stem = "test"
# savedir = path2sds+"/quickplots/"+stem+"plots/"
# savedir = path2sds+"/quickplots/condensationmethod/newrsqrd_shimacrit1_v2/plots/"
savedir = path2sds+"/quickplots/condensationmethod/newrsqrd_shimacrit1_v2_matsusubstepped/plots/"

print("build: "+path2build+"\ndataset: "+dataset+"\nsavedir: "+savedir)