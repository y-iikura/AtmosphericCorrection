#cd /Volumes/S_Processing/Atmospheric_Correction
fscene=ETM02063010832
#python PreProcessing/color_original.py $fscene
#python PreProcessing/aparm.py $fscene
#python PreProcessing/sixs_parm.py $fscene Mar 20
#python PreProcessing/pre_function.py $fscene Mar20
#python PreProcessing/pre_class.py $fscene 320 K 20
#python PreProcessing/pre_class.py $fscene 320 I 1
cd $fscene
#python ../MainProcessing/tcor_init.py MaK20P320_5 fMar20 cls320K_20
#python ../MainProcessing/tcor_batch.py  MaK20P320_5 5
python ../MainProcessing/color_image.py  MaK20P320_5 4 0.6
exit
#python ../PostProcessing/post_reclss.py  MaK20P320_5 5 8
#python ../PostProcessing/color_image2.py  MaK20P320_5 0.6
#python ../PostProcessing/post_hcorrect.py  MaK20P320_5 0.6
exit

