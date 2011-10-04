:"
:" % = current file
:" s = substitute
:" no = no 'magic' pattern matching
:" trailing '/e' turns off 'pattern not found' messages
:" w = write file
:"
:%sno/d:\/rrgis\/250k\/q/z:\/arcdata\/250k\/boundary\/q/e
:%sno/d:\/rrgis\/250k\/info\/q/z:\/arcdata\/250k\/boundary\/info\/q/e
:%sno/d:\/rrgis\/250k\/boundary/z:\/arcdata\/250k\/boundary/e
:%sno/d:\/rrgis\/250k\/theme/z:\/arcdata\/250k\/theme/e
:%sno/d:\/rrgis\/50k\/theme/z:\/arcdata\/50k\/theme/e
:%sno/d:\/rrgis\/1000k/z:\/arcdata\/1000k/e
:%sno/d:\/rrgis/z:\/arcdata_old/e
:%sno/z:\/arcdata\/lib250/z:\/arcdata_old\/250k/e
:%sno/z:\/arcdata\/arcdata/z:\/arcdata/e
:%sno/z:\/arcdata_old\/arcdata/z:\/arcdata_old/e
:" %sno/z:\/arcdata_old\/1000k/z:\arcdata\/1000k/e
:" %sno/\/1000k\/boundary\/border/\/1000k\/boundary\/mborder/e
:" %sno/\/1000k\/boundary\/codist/\/1000k\/boundary\/mcodist/e
:" %sno/\/1000k\/boundary\/fntt/\/1000k\/boundary\/mfntt/e
:" %sno/\/1000k\/boundary\/gma/\/1000k\/boundary\/mgma/e
:" %sno/\/1000k\/boundary\/oa/\/1000k\/boundary\/moa/e
:" %sno/\/1000k\/boundary\/park/\/1000k\/boundary\/mpark/e
:" %sno/\/1000k\/boundary\/rtc/\/1000k\/boundary\/mrtc/e
:" %sno/\/1000k\/boundary\/info\/border/\/1000k\/boundary\/info\/mborder/e
:" %sno/\/1000k\/boundary\/info\/codist/\/1000k\/boundary\/info\/mcodist/e
:" %sno/\/1000k\/boundary\/info\/fntt/\/1000k\/boundary\/info\/mfntt/e
:" %sno/\/1000k\/boundary\/info\/gma/\/1000k\/boundary\/info\/mgma/e
:" %sno/\/1000k\/boundary\/info\/oa/\/1000k\/boundary\/info\/moa/e
:" %sno/\/1000k\/boundary\/info\/park/\/1000k\/boundary\/info\/mpark/e
:" %sno/\/1000k\/boundary\/info\/rtc/\/1000k\/boundary\/info\/mrtc/e
:%sno/"Forest\ Inventory\ 250"/"Forest\ Inventory\ 50k"/e
:%sno/"rr50\.forest"/"Forest\ Inventory\ 50k\.forest_cover"/e
:%sno/"Forest\ Inventory\ 250.forest_cover"/"Forest\ Inventory\ 50k\.forest_cover"/e
:%sno/"forest\ inventory.forest_cover"/"Forest\ Inventory\ 50k\.forest_cover"/e
:%sno/"forest\ inventory\ 250.forest_cover"/"Forest\ Inventory\ 50k\.forest_cover"/e
:%sno/250k\/theme\/forestry/50k\/theme\/forestry/e
:%sno/"rr250\./"rr250-old\./e
:%sno/"rr50\./"rr50-old\./e
:%sno/"rr1000\.coast/"base\ 1000k\.coast/e
:%sno/"rr1000\.water/"base\ 1000k\.water/e
:%sno/"rr1000\.river/"base\ 1000k\.river/e
:%sno/"rr1000\.ice/"base\ 1000k\.ice/e
:%sno/"rr1000\.contour/"base\ 1000k\.contour/e
:%sno/"rr1000\.hypsometry/"base\ 1000k\.hypsometry/e
:%sno/"rr1000\.access/"base\ 1000k\.access/e
:%sno/"rr1000\.places/"base\ 1000k\.places/e
:%sno/"rr1000\.ocean/"base\ 1000k\.ocean/e
:%sno/z:\/arcdata\/250k\/base/z:\/arcdata_old\/250k\/base/e
:%sno/z:\/arcdata\/50k\/base/z:\/arcdata_old\/50k\/base/e
:%sno/z:\/arcdata\/1000k\/boundary/z:\/arcdata_old\/1000k\/boundary/e
:%sno/z:\/arcdata\/250k\/boundary/z:\/arcdata_old\/250k\/boundary/e
:%sno/z:\/arcdata\/50k\/boundary/z:\/arcdata_old\/50k\/boundary/e
:%sno/z:\/arcdata_old\/1000k\/base/z:\/arcdata\/1000k\/base/e
:%sno/\/lims\//\/base\//e
:%sno/"rr250-old\.-lims/"rr250-old\./e
:%sno/old\.old\./old\./e
:%sno/z:\/b1000k\//z:\/arcdata\/1000k\//e
:w
