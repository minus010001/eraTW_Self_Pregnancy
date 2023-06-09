eraTWeraTW4.551用色々修正

 CSV─VariableSize.csv

 ERB┬イベント関連─EVENTCOMEND2.ERB
	├コマンド関連┬USERCOM.ERB
	│			　└USERCOM_コマンド表示処理.ERB
	├ステータス計算関連─COUNTER─COUNTER_MESSAGE.ERB
	└口上・メッセージ関連┬EVENT_MESSAGE_挿入系COM┬EVENT_MESSAGE_Ａ騎乗位する.ERB
						　│					　 ├EVENT_MESSAGE_その他挿入系.ERB
						　│					　 ├EVENT_MESSAGE_後背位_通常.ERB
						　│					　 └EVENT_MESSAGE_後背位アナル.ERB
						　├EVENT_MESSAGE_COM.ERB
						　└KOJO_MESSAGE.ERB

236スレ>>536おそらく修正(VariableSize.csv
236スレ>>545の1修正(EVENTCOMEND2.ERB,EVENT_MESSAGE_COM.ERB
	おまけで、服はだけ時の乳首吸い＆胸愛撫の地の文をちょこっと追記
236スレ>>545の３修正(KOJO_MESSAGE.ERB
236スレ>>973の件で手入れ(USERCOM_コマンド表示処理.ERB,COUNTER_MESSAGE.ERB,EVENT_MESSAGE_Ａ騎乗位する.ERB,EVENT_MESSAGE_その他挿入系.ERB,EVENT_MESSAGE_後背位_通常.ERB,EVENT_MESSAGE_後背位アナル.ERB
	とりあえず後背位&後背位アナルCOMの条件（BEDROOMではなくINROOM）に、コマンド表示を摺り寄せてみた
		つまり、ちゃんとした部屋の中では後背位になると言う事
	それに関連して、背面立位の地の文に手を加えてみる
		見通しが良い広い屋外で背面立位する時はTARGETの腕を掴んでるという描写にしてみる
	さらに加えて、MASTERが下の穴でくわえ込む系の地の文が、TARGET主体になってたので主客転倒して、MASTER主体に書き直してみる
		単に既存の地の文のMASTERとTARGET入れ替えるだけだと、カウンターされてる感が強いので勝手に色々とやってみた
インデント修正(USERCOM.ERB


あと、一応直したけど入れなかったのが、カウンター表示周り
SOURCE.ERBの25行目と505行目で条件文が異なってた結果、挿入直後にカウンター表示＞アニメ表示後に同じカウンター表示になってたり
てか、おそらく通常カウンターが出てこなくなってたのも同じ理由じゃないかなと言うのと、進捗で修正済みということなので出す必要ないかなと


なお、口上はRETURN 0がまだ地味に生き残ってたので、全部RETURN 1に変更したくらいでほぼ変化無し
てか、依頼口上の難度が高すぎて、低空飛行中
さとりんの陥落状態×依頼口上分岐×依頼数……、これ無理

byさもま
