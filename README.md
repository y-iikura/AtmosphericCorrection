AtmosphericCorrection
======================
幾何補正済みの衛星画像から地表面反射率とエアロゾルの光学的厚さの空間分布の複数の可能性を同時に推定します。

概要と原理
===
* 平坦で一様な状況でも、衛星で検知する放射輝度Lsから地表面反射率ρを求めるには、エアロゾルの光学的厚さτが必要です。逆にρが分れば、τを推定する事が可能です。これは数学的には一つの方程式に対して、二つの未知数がある状況で解は不定となります。
* 非一様な状況では、画素の数だけの方程式とその2倍の未知数があります。さらに、起伏のある状況では、太陽入射角（天空光の遮蔽や照り返し光もある）が変化します。さらに、周辺の画素の反射が背景放射輝度や環境放射照度として影響を与えます。
* 一方、エアロゾルの空間分布は地表面反射率と較べれば、その変化は非常に小さいと考えれます。また、土地被覆分類図や直達日射照度のシミュレーション値などを利用すれば大気がない場合に、衛星から同じに見える画素を分類して利用する事も可能です。放射輝度の違いを大気の影響に限定できるからです。
* 同時推定法では与えられたLsと任意に設定するρとτの空間分布から出発して、反復により上記の制約条件を満たす解を求めます。


処理の流れ
===
以下の３つの部分（フォルダ名）からなります。  
* 前処理 PreProcessing  
　　- オリジナルデータのカラー合成  
　　- パラメータファイル（aparm.txt)の作成  
　　- ６Sによる大気パラメータの作成  
　　- 画素毎のρ-τ関数の作成  
　　- 分類クラスの作成
* 反復処理 MainProcessing  
　　- 作業フォルダの作成と処理条件の設定  
　　- 反復処理の実行
　　- 推定した反射率と光学的暑さのカラー合成
* 後処理 PostProcessing  
　　- 推定した反射率を利用した再分類と反復処理  
　　- 推定した反射率と光学的暑さのカラー合成  
　　- スケールハイトを用いた光学的厚さの標高補正  
　　- 推定結果の評価


使い方
------
上記の処理をシェルスクリプト(tcor.sh)にまとめてあります。ターミナルで以下のようなコマンドを入力します。お試し用のデータ(ETM02063010832.zip) がLFS (Large File Storage) として保存されています。
<pre>
$ sh tcor.sh
</pre>

### シェルスクリプトの例 ###
<pre>
#cd /Volumes/Transcend/AtmosphericCorrection
fscene=ETM02063010832
python PreProcessing/color_original.py $fscene
python PreProcessing/aparm.py $fscene
python PreProcessing/sixs_parm.py $fscene Mar 20 10 6
python PreProcessing/pre_function.py $fscene Mar20
python PreProcessing/pre_class.py $fscene 320 K 20
python PreProcessing/pre_class.py $fscene 320 I 1
cd $fscene
python ../MainProcessing/tcor_init.py MbK20P320_5 fMar20 cls320K_20
python ../MainProcessing/tcor_batch.py  MbK20P320_5 8
python ../MainProcessing/color_image.py  MbK20P320_5 7 0.6
python ../PostProcessing/post_reclss.py  MbK20P320_5 8 11
python ../PostProcessing/color_image2.py  MbK20P320_5 10 0.6
python ../PostProcessing/post_hcorrect.py  MbK20P320_5 10 0.6
python ../PostProcessing/post_evaluate.py  MbK20P320_5 8
exit
</pre>

途中でエラーとなる場合は、必要となる修正を行い、そこまでのコマンドをコメントアウトしてからスクリプトを再度実行する。

作業フォルダの命名規則等
------
####フォルダ名に以下のように処理の内容が含まれています。それらはフォルダ内のaparm.txtにも記載されます。  
　* M: 利用したエアロゾルタイプ（M:maritime、U:urbanなど）  
　* a：処理の識別（今後利用予定）  
　* K: エアロゾルのスケールハイト(2km)などの識別に利用  
　* 20：光学的厚さの初期値0.2  
　* P:　クラス代表値の選別方法（P:モード、M：中央値など）  
　* 320：クラス分類のカテゴリー数  
　* _5：減衰係数0.5  

　
####出力画像は以下の通りです。なおPostProcessingでは推定した反射率を利用して画素を再分類しています。
　* MaK20P320_5_ref321x.png：MainProcessingが終了して画像化した地表面反射率  
　*  MaK20P320_5_tauf321x.png：MainProcessingが終了して画像化した光学的厚さ  
　* MaK20P320_5_ref321y.png：PostProcessingが終了して画像化した地表面反射率  
　* MaK20P320_5_tauf321y.png：PostProcessingが終了して画像化した光学的厚さ  
　* MaK20P320_5_tauf321z.png：スケールハイトを補正した実質の光学的厚さ  
　
　
####指定したフォルダ内には最初に述べた計算の途中経過が含まれています。


必要なデータなど
----------------
お試し用のデータ(ETM02063010832.zip)を解凍して確認して下さい。

* 幾何補正済みの衛星データ(GEOTIF形式）と幾何情報や校正係数等が記載されているファイル(gparm.txt)が必要です。LandsatETM、LandsatOLI、AlosAVNIR2を利用して作成する事ができます。

* 衛星画像と同じ範囲の数値標高モデルと土地被覆分類図が必要です。それぞれ、KibanDemとJaxaLandcoverを利用して作成する事ができます。


利用するソフトウェアおよびライブラリ
--------
Python2.7で動作を確認しています。大気パラメータを計算するために放射伝達コードが必要です。現在は６S（Version2.1）を利用しています。6Sにパスが通っていなければなりません。Avnir2については、応答関数を組み込む必要があります。

1. sys,os,numpy,scipy,osgeo、cv2が必要です。
2. 自作のライブラリを利用します。  
　　1.UTILITY/rtc\_util  反射率の推定等に利用するライブラリ
　　2.Utility/tcor\_util 主に反復処理で利用するライブラリ  　
　　　

参考文献など
--------
* 飯倉善和、木村一星：衛星画像を用いた分光反射率と光学的厚さの同時推定、計測自動制御学会東北支部第289回研究集会、資料番号289-01、2014
* Y.Iikura, M.Takeo, N.Manago, H.Kuze: Surface reflectance estimation from satellite imagery with inhomogeneous atmospheric conditions IGARSS2015, 2015
* Y.Iikura, N.Manago, M.Sekiguchi, H.Kuze: Utiization ofradiative transfer code for satellite image processing, The23rd CEReS International Symposium on EnvironmentalRemote Sensing, 2015
* 飯倉善和、眞子直弘、久世宏明：衛星画像を用いた地表面反射率と光学的厚さの同時推定法の改良、日本リモートセンシング学会第60回学術講演会論文集、pp.31-34、2016


ライセンス
----------
Copyright &copy; 2016 Yoshikazu Iikura  
Distributed under the [MIT License][mit].

[MIT]: http://www.opensource.org/licenses/mit-