# Changelog
All notable changes to this project will be documented in this file. See [conventional commits](https://www.conventionalcommits.org/) for commit guidelines.

- - -
## [v0.8.1](https://github.com/yoctoyotta1024/superdrops-in-action/compare/1297e05337525a50ce0fc70c40a800899d0bcdc1..v0.8.1) - 2025-09-04
#### Bug Fixes
- missing binpath in run script args to python script - ([a984fc3](https://github.com/yoctoyotta1024/superdrops-in-action/commit/a984fc3f4ebe265168e6b25663bcef5098422432)) - clara.bayley
- major bugfix of bad check for empty arrays in 1dkid dynamics update of wvel - ([1297e05](https://github.com/yoctoyotta1024/superdrops-in-action/commit/1297e05337525a50ce0fc70c40a800899d0bcdc1)) - clara.bayley

- - -

## [v0.8.0](https://github.com/yoctoyotta1024/superdrops-in-action/compare/cad2dfb36a069faf69d8100e7ab75a605ac33927..v0.8.0) - 2025-07-29
#### Bug Fixes
- stddev of mean of population not just sample - ([1a86616](https://github.com/yoctoyotta1024/superdrops-in-action/commit/1a86616f9ace3b7aaff93a75858fdf92a2b71ed5)) - clara.bayley
- false j loop for integers not run ids - ([b21187d](https://github.com/yoctoyotta1024/superdrops-in-action/commit/b21187d01091a749dc9815e4ce5870bb4721de9d)) - clara.bayley
#### Continuous Integration
- delete unneeded calls - ([cad2dfb](https://github.com/yoctoyotta1024/superdrops-in-action/commit/cad2dfb36a069faf69d8100e7ab75a605ac33927)) - clara.bayley
#### Features
- script specifically for plot in CLEO paper 2 - ([67f2800](https://github.com/yoctoyotta1024/superdrops-in-action/commit/67f28000757abcab8c28fe82517a9c6c737dbe13)) - clara.bayley
- new file for plotting ensemble dataset - ([182f821](https://github.com/yoctoyotta1024/superdrops-in-action/commit/182f8210c2b3ec651f42100b423402487f58d42c)) - clara.bayley
#### Miscellaneous Chores
- delete unwanted statement - ([3e93009](https://github.com/yoctoyotta1024/superdrops-in-action/commit/3e93009e6b4d5afba5f199773089e147f461c56b)) - clara.bayley
#### Refactoring
- better way to write paths - ([baa566c](https://github.com/yoctoyotta1024/superdrops-in-action/commit/baa566ca238d22229b74bf38b3765b2de01275f4)) - clara.bayley
- update gitignore - ([9cf6cfd](https://github.com/yoctoyotta1024/superdrops-in-action/commit/9cf6cfd6f657c9177834f1bdd3c945d3f4d9333d)) - clara.bayley
- never plot more than one realisation of SD initial conditions - ([78b3195](https://github.com/yoctoyotta1024/superdrops-in-action/commit/78b31957d2c01e81af7186d26d22613f10892664)) - clara.bayley
- lower surface pressure to 965hPa - ([2f61966](https://github.com/yoctoyotta1024/superdrops-in-action/commit/2f619668da36a43349d8c090b3754cb0e6665af4)) - clara.bayley
- nicer way to write plotting - ([ddc551a](https://github.com/yoctoyotta1024/superdrops-in-action/commit/ddc551ab2bd6663c20765ac732820f8c664f83bd)) - clara.bayley
- add density profile to timeslice plots - ([ca5121c](https://github.com/yoctoyotta1024/superdrops-in-action/commit/ca5121cb2d4b4c30cb51311d50d0058b1ea20af8)) - clara.bayley
- add hill plots for ensemble - ([d182297](https://github.com/yoctoyotta1024/superdrops-in-action/commit/d1822972f9eeafc28272ac2e1f1f92d8eac01af5)) - clara.bayley
- edit defaults - ([11f4690](https://github.com/yoctoyotta1024/superdrops-in-action/commit/11f46907b2a7c7a6a43e7e1359e6e8cd9220ba16)) - clara.bayley

- - -

## [v0.7.1](https://github.com/yoctoyotta1024/superdrops-in-action/compare/4df85ad23ba7dce8dc47aee61e1a47ca2fa935f0..v0.7.1) - 2025-07-28
#### Bug Fixes
- missing (1+qv) factor in calculation of derivative of rho_d when accounting for water vapour - ([4701804](https://github.com/yoctoyotta1024/superdrops-in-action/commit/47018041d491a8c3592448c5ea4a627115da752a)) - clara.bayley
- qv and _th bug on interpolation when apprx_drhod_dz is false - ([4df85ad](https://github.com/yoctoyotta1024/superdrops-in-action/commit/4df85ad23ba7dce8dc47aee61e1a47ca2fa935f0)) - clara.bayley
#### Refactoring
- add density to initial profiles quickplot - ([b63ebfc](https://github.com/yoctoyotta1024/superdrops-in-action/commit/b63ebfc19f0c42b0f0027e4591d32cd83c9c8c20)) - clara.bayley
- edit superdrops in setup and don't use approximation to initial density profile - ([7f6c486](https://github.com/yoctoyotta1024/superdrops-in-action/commit/7f6c486b85b7a863800464351a45776b7bb6306e)) - clara.bayley

- - -

## [v0.7.0](https://github.com/yoctoyotta1024/superdrops-in-action/compare/4873a28c758a05778a1e72902d744111f789aa8f..v0.7.0) - 2025-07-24
#### Documentation
- correct example calls to inputfile and run functions - ([2427e10](https://github.com/yoctoyotta1024/superdrops-in-action/commit/2427e10545dd38f82340ad368e0371b1b50add4a)) - clara.bayley
#### Features
- use bash script to create configs for each run - ([a30c6e8](https://github.com/yoctoyotta1024/superdrops-in-action/commit/a30c6e80180c4cc1ed162eaa386accf7767145fb)) - clara.bayley
- new script to copy config and edit parameters - ([b42412d](https://github.com/yoctoyotta1024/superdrops-in-action/commit/b42412d2470babbd300d4f0a2021b40de1543591)) - clara.bayley
#### Miscellaneous Chores
- edit commands in docs - ([9f2e175](https://github.com/yoctoyotta1024/superdrops-in-action/commit/9f2e175d262c599074a31419e45d116d14fc0e52)) - clara.bayley
- remove last modified from file headers - ([c2ed388](https://github.com/yoctoyotta1024/superdrops-in-action/commit/c2ed388752d8e2c1122ef473063bceb792b7f1aa)) - clara.bayley
- copy changes from CLEO 0.52.0 pycleo library into cleo_deps - ([32e3817](https://github.com/yoctoyotta1024/superdrops-in-action/commit/32e3817eafe8f25ded13a1189c253f1f304117eb)) - clara.bayley
- copy changes from CLEO 0.52.0 runcleo library into cleo_deps - ([be99802](https://github.com/yoctoyotta1024/superdrops-in-action/commit/be99802e5e088fba898172d6290e2670a57e737e)) - clara.bayley
- copy changes from CLEO 0.52.0 superdrops library into cleo_deps - ([12695ac](https://github.com/yoctoyotta1024/superdrops-in-action/commit/12695acccb0a930bf4d120c8c054506c01846554)) - clara.bayley
- copy changes from CLEO 0.52.0 observers library into cleo_deps - ([258473e](https://github.com/yoctoyotta1024/superdrops-in-action/commit/258473e1a58dedbc5e18534d516fd39fb71fb1fb)) - clara.bayley
- copy changes from CLEO 0.52.0 into cleo_deps - ([1b92521](https://github.com/yoctoyotta1024/superdrops-in-action/commit/1b92521cead9b3fab20f5cdc612b49ac809be14a)) - clara.bayley
#### Refactoring
- input scripts for gbxs and supers use argparse - ([8a03cfc](https://github.com/yoctoyotta1024/superdrops-in-action/commit/8a03cfcc7c4db6ec360321af2cb19aed1480cb3a)) - clara.bayley
- modify defaults - ([903006b](https://github.com/yoctoyotta1024/superdrops-in-action/commit/903006ba73ca16309862bff9030b85a882c57070)) - clara.bayley
- run script for ensemble of runs - ([60d1c89](https://github.com/yoctoyotta1024/superdrops-in-action/commit/60d1c89e6f73efb3ebdf0cc0ecc402540809bd11)) - clara.bayley
- add precip to quickplots - ([10265ac](https://github.com/yoctoyotta1024/superdrops-in-action/commit/10265ac2eafc8cabc6ba55aabb0130fddded871d)) - clara.bayley
- generalise run scripts - ([6d01774](https://github.com/yoctoyotta1024/superdrops-in-action/commit/6d017747120d151aecfc649c7458ca0e71949ca2)) - clara.bayley
- homogenise bash script args - ([4c25bd9](https://github.com/yoctoyotta1024/superdrops-in-action/commit/4c25bd9dfe4b580e32757ef88bac1a82566adbd7)) - clara.bayley
- give configs as list to input files creation - ([cabfad8](https://github.com/yoctoyotta1024/superdrops-in-action/commit/cabfad837515496e99e6ac8fa75a942cf3c3af37)) - clara.bayley
- note on config relative paths - ([40d681b](https://github.com/yoctoyotta1024/superdrops-in-action/commit/40d681b1cab799c787b2c203019e6a316617fce8)) - clara.bayley
- change default/example build directory location - ([ef59e6c](https://github.com/yoctoyotta1024/superdrops-in-action/commit/ef59e6c7b90ccc9901517668c5e282a9a2507721)) - clara.bayley
- use cleo 0.52.0 python bindings - ([be4f501](https://github.com/yoctoyotta1024/superdrops-in-action/commit/be4f50173608899789bb6ccec24c1afc6a22e388)) - clara.bayley
- plot for condevap_only - ([b2ebc31](https://github.com/yoctoyotta1024/superdrops-in-action/commit/b2ebc31752a99627c9961e706757f6bcc0325612)) - clara.bayley
- plot for fullscheme - ([cbf930d](https://github.com/yoctoyotta1024/superdrops-in-action/commit/cbf930daca051648e263c0898c0f2451c435e0b3)) - clara.bayley
- more quickplots - ([4873a28](https://github.com/yoctoyotta1024/superdrops-in-action/commit/4873a28c758a05778a1e72902d744111f789aa8f)) - clara.bayley

- - -

## [v0.6.0](https://github.com/yoctoyotta1024/superdrops-in-action/compare/5a9e3bc2cbe8aa2719d2f899e7b3e7ecbb90c419..v0.6.0) - 2025-07-21
#### Bug Fixes
- don't set wvel when its an empty array - ([62f2e0e](https://github.com/yoctoyotta1024/superdrops-in-action/commit/62f2e0e7774d44429bb97f005d8d34b66b5dcfcb)) - clara.bayley
- correc normalisation - ([f6d4608](https://github.com/yoctoyotta1024/superdrops-in-action/commit/f6d46084c879c5d73d5130a8f219dbe371be6ebd)) - clara.bayley
#### Continuous Integration
- fix condition on wvel - ([354717c](https://github.com/yoctoyotta1024/superdrops-in-action/commit/354717c6d536e7b4ebffe8dfee8219fd1e6be627)) - clara.bayley
- edit cleo init cond file locations - ([8aacb51](https://github.com/yoctoyotta1024/superdrops-in-action/commit/8aacb514ad104c6956068591e4cbffb66a402e54)) - clara.bayley
- lower python version requirement - ([bfea9d6](https://github.com/yoctoyotta1024/superdrops-in-action/commit/bfea9d61bf90a0da3c7d2d866f6b20f8d52d36c4)) - clara.bayley
#### Documentation
- note on plotting script - ([1304d93](https://github.com/yoctoyotta1024/superdrops-in-action/commit/1304d93cb06b94e7c7a3a2903425ec9be2b3a893)) - clara.bayley
- how to generate input files - ([68b9c7e](https://github.com/yoctoyotta1024/superdrops-in-action/commit/68b9c7e830f2960b099729953ad4c22d4e772161)) - clara.bayley
#### Features
- new file for quickplotting cleo 1dkid dataset - ([21e3fb2](https://github.com/yoctoyotta1024/superdrops-in-action/commit/21e3fb2b85edfdbfa4753ec949d4d35ba60dc98b)) - clara.bayley
- files to create CLEO kid init conds with alpha sampling - ([cceaec4](https://github.com/yoctoyotta1024/superdrops-in-action/commit/cceaec4a2a8e40a8ef1ffaba433a7dfb55b1daf0)) - clara.bayley
#### Miscellaneous Chores
- move files - ([b29161b](https://github.com/yoctoyotta1024/superdrops-in-action/commit/b29161b3d27dfbdc16e563050a96a2c5b3f066ea)) - clara.bayley
#### Refactoring
- correct labels for args to scriptS - ([e142f83](https://github.com/yoctoyotta1024/superdrops-in-action/commit/e142f833f7562c8794cc3603cd8338b5a734839d)) - clara.bayley
- use cleo numconc tolerance argument - ([ae5174a](https://github.com/yoctoyotta1024/superdrops-in-action/commit/ae5174ac0c95f9339bda4b994968d2868e1cb85f)) - clara.bayley
- add note on meaning of GC - ([24a79fe](https://github.com/yoctoyotta1024/superdrops-in-action/commit/24a79fea256ae3829cd9068ffc431e9aabb6eae5)) - clara.bayley
- reduce subtimestep for NR method - ([a111a02](https://github.com/yoctoyotta1024/superdrops-in-action/commit/a111a020f116e8deb3149ab8cced5d4c0113fa35)) - clara.bayley
- increase nsupers in config - ([98f2ee7](https://github.com/yoctoyotta1024/superdrops-in-action/commit/98f2ee73dfb9504b0edb8d0c8e72518aebaf3143)) - clara.bayley
- change init cond paths in config - ([3a5dffa](https://github.com/yoctoyotta1024/superdrops-in-action/commit/3a5dffad79954d93c5ffa2fe5ec184f6c46585c5)) - clara.bayley
- smaller x and y grid spacing - ([3df89d6](https://github.com/yoctoyotta1024/superdrops-in-action/commit/3df89d6f90c144ae467cedc46c3b3fd7b828c3a3)) - clara.bayley
- require pysdm branch with alpha sampling - ([5a9e3bc](https://github.com/yoctoyotta1024/superdrops-in-action/commit/5a9e3bc2cbe8aa2719d2f899e7b3e7ecbb90c419)) - clara.bayley

- - -

## [v0.5.0](https://github.com/yoctoyotta1024/superdrops-in-action/compare/24b831b360dade48ecea6df27b72fa77bacca536..v0.5.0) - 2025-07-21
#### Bug Fixes
- correct time given to momentum profile - ([1fe29a2](https://github.com/yoctoyotta1024/superdrops-in-action/commit/1fe29a29bc3c28b0831211b415764484ebb861ed)) - clara.bayley
- use vertical velocity for SDs consistant with pympdata density profile - ([0c1b467](https://github.com/yoctoyotta1024/superdrops-in-action/commit/0c1b46744d49c2ffada008c196046ae1ad35d68c)) - clara.bayley
#### Features
- helper bash script to run 1dkid from - ([ac1f78f](https://github.com/yoctoyotta1024/superdrops-in-action/commit/ac1f78f9688bb7ea181dbc1283047acebea76a0c)) - clara.bayley
#### Refactoring
- raise p0 to standard value - ([f347c81](https://github.com/yoctoyotta1024/superdrops-in-action/commit/f347c812c6511e5f7284ef598b572b93a354a5ae)) - clara.bayley
- explicitly set approx flag to true - ([97c4422](https://github.com/yoctoyotta1024/superdrops-in-action/commit/97c44229fed2c89533bbb5585586ab9176b731ab)) - clara.bayley
- lower p0 of kid to 990 - ([3b02e12](https://github.com/yoctoyotta1024/superdrops-in-action/commit/3b02e1230c1908aa70dc979e8a964d16fd9dab64)) - clara.bayley
- rename slurm job - ([54118ce](https://github.com/yoctoyotta1024/superdrops-in-action/commit/54118ce25f305e80c7495339f39b73ef5d0ee950)) - clara.bayley
- add slurm settings to compilation script - ([7f3eaf2](https://github.com/yoctoyotta1024/superdrops-in-action/commit/7f3eaf26fc7c360ce2bff5049a4b80a5d78e3e1c)) - clara.bayley
- adjust timesteps of kid config - ([24b831b](https://github.com/yoctoyotta1024/superdrops-in-action/commit/24b831b360dade48ecea6df27b72fa77bacca536)) - clara.bayley

- - -

## [v0.4.0](https://github.com/yoctoyotta1024/superdrops-in-action/compare/146be40a605cad491e8e97a3f811944d65355650..v0.4.0) - 2025-07-15
#### Documentation
- more detail on CLEO modifications note - ([8334180](https://github.com/yoctoyotta1024/superdrops-in-action/commit/8334180282a5738b99b91c7a6d2bedf115950703)) - clara.bayley
#### Features
- new SDMMethods specifically for KiD test case - ([146be40](https://github.com/yoctoyotta1024/superdrops-in-action/commit/146be40a605cad491e8e97a3f811944d65355650)) - clara.bayley
#### Miscellaneous Chores
- copy libs from CLEO v0.51.0 - ([96611a3](https://github.com/yoctoyotta1024/superdrops-in-action/commit/96611a32d85e97e7cb39ff79b2f5c90542673b8b)) - clara.bayley
- copy libs from CLEO v0.50.0 - ([fb5ac90](https://github.com/yoctoyotta1024/superdrops-in-action/commit/fb5ac90af0803724f6d8b00fe396883ff0eb69b5)) - clara.bayley
- formatting - ([449c3df](https://github.com/yoctoyotta1024/superdrops-in-action/commit/449c3df7612c2461b3793e5072a6534e015667e3)) - clara.bayley
#### Refactoring
- use new observers in 1dkid examples - ([e6d1f42](https://github.com/yoctoyotta1024/superdrops-in-action/commit/e6d1f426abc5a2e1d4414e46fb5debb65982faff)) - clara.bayley
- make scripts compatible with updated cleo version libraries - ([8d5e536](https://github.com/yoctoyotta1024/superdrops-in-action/commit/8d5e536b3ba7ed3add29bcb9cfe0addcbfce5f9f)) - clara.bayley
- replace dokidobs observer with gbxindex observer - ([69d2b90](https://github.com/yoctoyotta1024/superdrops-in-action/commit/69d2b90bad9b7fbc0e69921bc13569600966c47b)) - clara.bayley
- use alias - ([b6e6737](https://github.com/yoctoyotta1024/superdrops-in-action/commit/b6e6737a65d6b3da0089c38aa1ab93948ae91c53)) - clara.bayley
- kid observer is combination of observers - ([f364395](https://github.com/yoctoyotta1024/superdrops-in-action/commit/f3643956f4424290abff21df4fad6e6cc2dcf2c2)) - clara.bayley
- time observations working with kid observer - ([e97a00a](https://github.com/yoctoyotta1024/superdrops-in-action/commit/e97a00a14fcf0fb2d07faf92ec8dbad54f44386d)) - clara.bayley
- add zarr dependency - ([ef90bf7](https://github.com/yoctoyotta1024/superdrops-in-action/commit/ef90bf79ccdb41093ee2671a41c7e3a54622b83a)) - clara.bayley

- - -

## [v0.3.0](https://github.com/yoctoyotta1024/superdrops-in-action/compare/ef7e3fa1db74be595bbd2e1a2a4f175a0ea633a4..v0.3.0) - 2025-07-14
#### Bug Fixes
- correct links to files in CI - ([ef7e3fa](https://github.com/yoctoyotta1024/superdrops-in-action/commit/ef7e3fa1db74be595bbd2e1a2a4f175a0ea633a4)) - clara.bayley
#### Features
- new function to reset superdroplet radii in BCs - ([a7560c2](https://github.com/yoctoyotta1024/superdrops-in-action/commit/a7560c261b457ec11815250969f4f3a90f42d840)) - clara.bayley

- - -

## [v0.2.0](https://github.com/yoctoyotta1024/superdrops-in-action/compare/9b7b715636ea3b61efe2b8a81fa074af0f870601..v0.2.0) - 2025-07-14
#### Bug Fixes
- extra \ removed - ([df1a08c](https://github.com/yoctoyotta1024/superdrops-in-action/commit/df1a08c0863c4c6bce8435bd099897f9fda02b23)) - clara.bayley
- correct paths in config files - ([b243f64](https://github.com/yoctoyotta1024/superdrops-in-action/commit/b243f64495ddf71077eb17a11096e30c7b42ff1f)) - clara.bayley
- fix cmake source and binary dirs and remove unused yac flags from build - ([b6f55b0](https://github.com/yoctoyotta1024/superdrops-in-action/commit/b6f55b065cf52a5bdfdb544cf2d456840d65f22e)) - clara.bayley
- correct project name - ([28c50c7](https://github.com/yoctoyotta1024/superdrops-in-action/commit/28c50c7d649a323a1e30b3d4605cc01c25fc8314)) - clara.bayley
#### Continuous Integration
- more detail in ls - ([74288b1](https://github.com/yoctoyotta1024/superdrops-in-action/commit/74288b119f830a5dd1a0e74d171f56252e0ae280)) - clara.bayley
- change paths for cleo_1d pytests - ([a7cf4c0](https://github.com/yoctoyotta1024/superdrops-in-action/commit/a7cf4c017d48e8b71ce27a3ed2f4cd4ce1ea7468)) - clara.bayley
- add pytests - ([69cfc79](https://github.com/yoctoyotta1024/superdrops-in-action/commit/69cfc79973d291eb5195d9feed6fa123a011bc13)) - clara.bayley
#### Documentation
- notes on cleo_1dkid test case - ([e714267](https://github.com/yoctoyotta1024/superdrops-in-action/commit/e714267b543dcefada7461df37f495440f1c0c9e)) - clara.bayley
- correct script name - ([913ff96](https://github.com/yoctoyotta1024/superdrops-in-action/commit/913ff96f370a6685227f13fdaacc3fa223dd5731)) - clara.bayley
- simplify command - ([efba24f](https://github.com/yoctoyotta1024/superdrops-in-action/commit/efba24f8e4b6317c592d40fa5a7bb323d583e865)) - clara.bayley
- add cleo_1dkid to docs - ([0fd0d90](https://github.com/yoctoyotta1024/superdrops-in-action/commit/0fd0d90144822a77bfc86f874d50586bec8b6262)) - clara.bayley
- add basic documentation - ([9b7b715](https://github.com/yoctoyotta1024/superdrops-in-action/commit/9b7b715636ea3b61efe2b8a81fa074af0f870601)) - clara.bayley
#### Features
- new script to run CLEO fullscheme simulation - ([3d196c5](https://github.com/yoctoyotta1024/superdrops-in-action/commit/3d196c5415dac6aa02e52b458cf9cb38e45a7045)) - clara.bayley
- new script to run CLEO condevap simulation - ([59b1f50](https://github.com/yoctoyotta1024/superdrops-in-action/commit/59b1f50b8f55ddfcf236b9cf0dbce2af5f4409dd)) - clara.bayley
- files copied from CLEO repo for making pycleo bindings suitable to 1-D KiD test case - ([8b27c38](https://github.com/yoctoyotta1024/superdrops-in-action/commit/8b27c385cbb2b02f4a81275bde749fb8eb44a05f)) - clara.bayley
- files copies from microphysics_testcases repo for CLEO and pyMPDATA test cases - ([1c54b61](https://github.com/yoctoyotta1024/superdrops-in-action/commit/1c54b618f2f88682d685cb42bf522f47a41b8e77)) - clara.bayley
#### Miscellaneous Chores
- yaml formatting - ([cd140ac](https://github.com/yoctoyotta1024/superdrops-in-action/commit/cd140acaa47115535736b1b25e09dccb1b189503)) - clara.bayley
- rename variable - ([744efa7](https://github.com/yoctoyotta1024/superdrops-in-action/commit/744efa737d0175b2154e80e3b3e220d2df067a6d)) - clara.bayley
- correct notes - ([dfcc845](https://github.com/yoctoyotta1024/superdrops-in-action/commit/dfcc845f8aa9cb7d015b3e14161814fbcdaff734)) - clara.bayley
- move script - ([82ecc6a](https://github.com/yoctoyotta1024/superdrops-in-action/commit/82ecc6a624584f1fbdab9f9ad7ac7114414544f9)) - clara.bayley
- formatting - ([3caaf14](https://github.com/yoctoyotta1024/superdrops-in-action/commit/3caaf1424f0260bceefaed085f74ef598f5ef75d)) - clara.bayley
#### Refactoring
- use periodic BCs - ([0482345](https://github.com/yoctoyotta1024/superdrops-in-action/commit/04823457138339a7e6d8c600236373024acafeca)) - clara.bayley
- modify binpaths - ([6a5d6de](https://github.com/yoctoyotta1024/superdrops-in-action/commit/6a5d6def906d368a97860a4f65a406dc198fe118)) - clara.bayley
- move binpath in pytests - ([858ee0e](https://github.com/yoctoyotta1024/superdrops-in-action/commit/858ee0e7ab5f5ea2690fc6fab1bb290418114ded)) - clara.bayley
- remove unused yac details - ([22640f4](https://github.com/yoctoyotta1024/superdrops-in-action/commit/22640f41789cd8580b67d07cc7a0b15dd30e75b3)) - clara.bayley
- change default paths for cleo tests - ([29dd2de](https://github.com/yoctoyotta1024/superdrops-in-action/commit/29dd2de4df9b2c227a5b907cfcfc90a670dbeb63)) - clara.bayley
- ignore c++17 formating - ([2695057](https://github.com/yoctoyotta1024/superdrops-in-action/commit/26950575848392f94d5a30403b5987281afcbf1c)) - clara.bayley

- - -

## [v0.1.0](https://github.com/yoctoyotta1024/superdrops-in-action/compare/v0.0.0..v0.1.0) - 2025-07-14
#### Features
- empty repository necessities - ([f2c6e01](https://github.com/yoctoyotta1024/superdrops-in-action/commit/f2c6e010f5d09cabf987be2820c30bc109974944)) - clara.bayley

- - -

## [v0.0.0](https://github.com/yoctoyotta1024/superdrops-in-action/compare/a589750bb93ae42459a53b85756eb3fd848cb1fd..v0.0.0) - 2025-07-14
#### Features
- wipe repository - ([e15d1a8](https://github.com/yoctoyotta1024/superdrops-in-action/commit/e15d1a887cc944d330028cebab07571bdadcd1da)) - clara.bayley

- - -

Changelog generated by [cocogitto](https://github.com/cocogitto/cocogitto).
