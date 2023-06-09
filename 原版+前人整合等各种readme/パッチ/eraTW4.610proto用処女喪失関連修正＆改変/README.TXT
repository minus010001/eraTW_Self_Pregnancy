eraTW4.610proto用処女喪失関連修正＆改変

 ERB┬コマンド関連─COMF┬COMF71 二穴挿し.ERB
	│					├COMF92 Ａ正常位される.ERB
	│					├COMF93 Ａ後背位される.ERB
	│					└COMF94 Ａ騎乗位する.ERB
	├ステータス計算関連┬TRACHECK_LOST_VIRGIN.ERB
	│					├COUNTER─COUNTER_SOURCE.ERB
	│					└SOURCE─SOURCE.ERB
	└ステータス表示関連─PRINT_STATE2.ERB


その１、アナル処女喪失関連修正(COMF71 二穴挿し.ERB,COMF92 Ａ正常位される.ERB,COMF93 Ａ後背位される.ERB,COMF94 Ａ騎乗位する.ERB,TRACHECK_LOST_VIRGIN.ERB,COUNTER_SOURCE.ERB,SOURCE.ERB
	前回、二穴挿入時の非TARGETアナル消失を修正はしたけど、その発生の大元の原因がわかったので修正し直してみた
	というか、童貞アナル処女ファーストキス関数、なんでSOURCEのキャラループから外れてたんだろ、そりゃTARGET限定にせざるを得ないわけだわ
	ということで、SOURCEのキャラループ内に移動してみるテスト
		おそらく、以前はMASTER関連の童貞喪失等をSOURCE外でやってたことの影響なんだろうけど
	その過程で、二穴挿入時にアナル処女喪失が発生しなくなってたのが判明したのでそっちも修正

その２、処女喪失履歴関連（TRACHECK_LOST_VIRGIN.ERB,SOURCE.ERB
	処女喪失対象がMASTERとTARGETのみ限定っぽかったので、そうじゃない場合を想定して手を入れて見る（今のところ二穴挿入以外では発生しないと思う
	処女奪取対象がMASTER以外の場合の、履歴地の文に手を入れて見る
	

その３、処女喪失履歴表示関連（PRINT_STATE2.ERB
	アナル処女喪失履歴がある場合、余分な改行が入るのを修正
	最初から非処女のキャラに、二通りの処女喪失履歴を追加
		一つ目は既に失ってます表示
		二つ目は、開始時に処女にした場合に、改変されて処女になりました表示、処女を奪うと通常の履歴が表示されます



ちなみに、今回の改変でMASTER＆非TARGETのアナル処女喪失履歴が記録されるようになります
それ以前にMASTER＆非TARGET（4.610proto||eraTW4.600proto＋eraTW4.600proto用色々修正＋α使用時）でアナル経験が増加していても、今回のパッチ導入後の初アナル挿入がアナル処女喪失履歴に登録されます


byさもま
