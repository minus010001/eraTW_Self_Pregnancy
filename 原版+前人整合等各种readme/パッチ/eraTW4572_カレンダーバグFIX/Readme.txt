カレンダーバグFIX

○ファイル構成
 ERB┬MOVEMENTS─JOB_仕事内容.ERB
    └コマンド関連─カレンダー.ERB

○修正内容
　カレンダー呼び出し時に条件を満たしているキャラクターの
　仕事予定が表示されないことがある問題を修正

○修正箇所
・JOB_仕事内容.ERB
　@CHARA_HOLIDAY
　①@CHARA_HOLIDAY(ARG)の引数を増やして（省略可）
　　@CHARA_HOLIDAY(ARG, ARG:1=0)に変更
　②13-16行目をARG:1の値による分岐で回避するよう修正
　　ARG:1 = 1の場合、仕事量による休日判定と、
　　終了時刻による休日判定を行わない
・カレンダー.ERB
　@予定表
　①209行目のCHARA_HOLIDAYの呼び出しに引数を追加
　　CHARA_HOLIDAY(LOCAL, 1)

by eratoho総合スレ240-585

