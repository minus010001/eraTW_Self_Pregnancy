

日記口上のテンプレートが複雑で敷居高そう感じたので、なんとか簡単にできないか試作してみました。
一応自作の小鈴口上をとりあえず簡易版に移植して動作確認はしてます。

●日記口上（簡易版）の書き方
１．@DIARY_BEFORE_CHECK_KX
CHARA = XX　←ここにキャラ番号を入れる

２．@DIARY_TEXT_KX
PRINTFORMDL - %CALLNAME:XX%の日記　PAGE.{PAGECOUNT} -----------
　　　　　　　　　　　　↑ここにキャラ番号を入れる

３．@DIARY_KX_YY_HAPPEN
　　↓ここに発生条件を設定する（例：CFLAG:XX:好感度 >= 100）
SIF 0
　　RETURN 1

形式とリピートに関してはテンプレを参照

４．@DIARY_KX_YY
PRINTFORML 今日は
PRINTFORML 　　　とても
PRINTFORML 　　　　　　いい天気
PRINTFORML 　　　　　　　　　　だった
↑日記を書くだけ

それ以外の部分は詳細版（仮称）と同じです。

●+α
小鈴口上の日記を簡易版に移植

口上色が付かないのを修正
[部屋に入る]にTIME+=1を設定
（スレ284>>8）

