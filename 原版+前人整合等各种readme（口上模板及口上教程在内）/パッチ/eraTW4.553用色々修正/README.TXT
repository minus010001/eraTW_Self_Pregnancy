eraTW4.553用色々修正

 ERB┬MOVEMENTS─BASE自然変動.ERB
 	├イベント関連─BEFORETRAIN.ERB
	├コマンド関連┬USERCOM_コマンド表示処理.ERB
	│			　└COMF┬COMF88 バキュームフェラ.ERB
	│					├COMF92 Ａ正常位される.ERB
	│					├COMF93 Ａ後背位される.ERB
	│					├COMF130 正常位される.ERB
	│					├COMF131 後背位される.ERB
	│					└日常系─COMF331 お茶を淹れる（薬入り）.ERB
	├ステータス計算関連┬COUNTER─COUNTER_MESSAGE.ERB
	│					└SOURCE─SOURCE_POSE.ERB
	└口上・メッセージ関連┬EVENT_MESSAGE_COM_セクハラ.ERB
						　├EVENT_MESSAGE_COM300.ERB
						　├EVENT_MESSAGE_挿入系COM┬EVENT_MESSAGE_その他挿入系.ERB
						　│					　 └EVENT_MESSAGE_正常位.ERB
						　└個人口上─幽香─M_KOJO_K68_日常系コマンド.ERB

MASTER受け性交コマンドも、通常or立位の表示変更をするように＆ふたなり時クリ愛撫を竿愛撫と表示するように(USERCOM_コマンド表示処理.ERB,COMF92 Ａ正常位される.ERB,COMF93 Ａ後背位される.ERBCOMF130 正常位される.ERB,COMF131 後背位される.ERB,COUNTER_MESSAGE.ERB
バキュームフェラ実行時のコマンド名がフェラチオになってたので修正(COMF88 バキュームフェラ.ERB
	クリ愛撫もおなじ状態なんだけど、どうやれば良いか解らないので、見苦しいけどそのままだったり
ふたなりTARGETに挿入されてる状態でフェラチオ等を選ぶと、MASTERにＶ経験等がはいりつつ、各コマンドが実行されるのを修正(SOURCE_POSE.ERB
	@挿入解除(ARG)のおかげです、本当にありがとうございます
237スレ>>394の修正(BASE自然変動.ERB,BEFORETRAIN.ERB,COMF331 お茶を淹れる（薬入り）.ERB,M_KOJO_K68_日常系コマンド.ERB
	地の文書いた時に睡眠薬がなかった事
	惚れ薬が他の二つと違ってONOFFの扱いだったので齟齬が出た事
	睡眠薬追加時に、COM開始時のTARGETでONOFFすべきTFLAG:193が、TARGET以外が成功してもONになってた事
	これらの複合作用っぽいので、色々手直ししてみた
	まず、惚れ薬をONOFFスイッチ扱いから時間経過減少型に（おそらく齟齬は出ない筈
	睡眠薬フラグも段階スイッチ式で、こっち弄るとあっちこっちに派生しかねなかったので、一回で睡眠薬効果が2になるように＋もういっこTCVARフラグを作成し一日に二回成功しない様に





幽香口上の人に連絡、惚れ薬分岐を変更したので、分岐条件だけ手を入れさせて頂きました
ご確認をお願いします




さとりん口上は凡ミス修正のみ

今、もこたんの育児口上（地の文改訂＋α）書いてるけど、育児口上関連でまた動きがあるっぽいので、しばらく保留すべきか



複数の自作口上で自作関数を使い回す事に問題があるとか言われるのかーbyさもま（さとり妹紅マミゾウ口上書き）
