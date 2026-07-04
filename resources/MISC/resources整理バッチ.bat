echo on
pause

rem 以下のファイルを削除
del 顔_55.csv
del 顔_98.csv
del 顔_107.csv
del 顔_108.csv
del 立ち絵_9.csv
del 立ち絵_51.csv
del 顔_9.csv
del 顔_51.csv
del 55.bak
del 55_顔.bak
del 39_顔.bak
del 41_顔_1.bak

rem 新規フォルダ作成
md 個別キャラコマンド 汎用コマンド

rem カレントフォルダから移動
move 39_コマンド.csv .\個別キャラコマンド\
move 39_奉仕.webp .\個別キャラコマンド\
move 41_コマンド.csv .\個別キャラコマンド\
move 41_奉仕.webp .\個別キャラコマンド\
move 42_コマンド.csv .\個別キャラコマンド\
move 42_奉仕.webp .\個別キャラコマンド\
move 42_奉仕b.webp .\個別キャラコマンド\
move 55_コマンド.csv .\個別キャラコマンド\
move 55_奉仕.webp .\個別キャラコマンド\
move 65_コマンド.csv .\個別キャラコマンド\
move 65_精液垂れ.webp .\個別キャラコマンド\
move 86_コマンド.csv .\個別キャラコマンド\
move 86_奉仕.webp .\個別キャラコマンド\
move kaoru_set_顔.webp .\モブ子パーツ関連\
move MOB_男.webp .\モブ子パーツ関連\
move MOBイナバセット.webp .\モブ子パーツ関連\
move kaoru_set.webp .\モブ子パーツ関連\
move kaoru_set_a.webp .\モブ子パーツ関連\
move モブ販売員素材.webp .\モブ子パーツ関連\
move 茨たぬき素材.webp .\モブ子パーツ関連\
move モブ店員パーツ.webp .\モブ子パーツ関連\
move 太眉リソース.webp .\モブ子パーツ関連\
move 巫女服リソース.webp .\モブ子パーツ関連\
move kaoru_set.csv .\モブ子パーツ関連\
move kaoru_set_顔.csv .\モブ子パーツ関連\
move MOB.csv .\モブ子パーツ関連\

rem "hatate_skirt"フォルダの内容を"resources"→"日常コマンド"へ移動
cd hatate_skirt
move * ..
cd %~dp0
move はたてスカートめくり改.csv .\日常コマンド\
move はたてのぱんつ.webp .\日常コマンド\
move はたての身体.webp .\日常コマンド\

rem "日常コマンド"フォルダを"hatate_picture"に変更
rename 日常コマンド hatate_picture

rem "hatate_skirt"フォルダを削除
rd hatate_skirt

pause

