1,射精箇所,; (ビット 1=膣内 2=アナル 3=手淫 4=口淫 5=パイズリ 6=素股 7=足コキ 8=体表 9=アナル奉仕
2,破瓜抑制フラグ,;（処女で快Vを得た場合、経験を変動させない)
3,SELECTCOM保存
4,破瓜フラグ
5,押し倒し

10,Ｖ挿入継続
11,Ａ挿入継続
12,逆レイプ継続
13,好感度入らない
14,挿入不可

20,时奸刻印取得
21,反発刻印取得
22,苦痛刻印取得
23,快楽刻印取得
24,屈服刻印取得
25,刻印従順変化

40,Info表示中


50,特殊COM,;(1=シックスナイン 2=岩清水 3=Gスポット刺激 4=乱れ牡丹 5=手淫フェラ 6= 7= 8= シックスナインパイズリ 13=交互挿入 17=乳首同時吸い)

60,MASTERの口使用中
61,MASTERの手使用中
62,MASTERのＣ使用中
63,MASTERのＶ使用中
64,MASTERのＡ使用中
65,MASTERのＢ使用中

70,押し倒せない
86,授乳コマンド
87,風チラあり
88,キス合意取得
89,信頼度変化なし

90,理性削り
91,ムード上昇抑制
92,ムードボーナス
93,口上特殊補正
95,好感度ボーナス
96,好感度マイナス
97,好感度管理
98,信頼度管理
99,信頼度管理その２
100,調教中COMABLE管理
101,調教自動実行管理
102,COMABLE管理
;(1=日常ON 2=ウフフON 3=相手から押し倒され)
103,前ターンのTARGET交代
104,現在のTARGET
;(0なら指定しない) TARGET変更用（変更したい相手が入ってる）
105,ビデオカメラ
;(0=固定カメラ 1=MASTER撮影 2=助手撮影)
106,MASTERのＰ挿入中
107,抱きつきモード
108,抱きつき解放ポイント
109,押し倒され開始時間
110,MASTERの馴れ合い

117,妄想中
120,キスマーク
122,包帯
123,耳補正

124,パール期限
125,パール挿入個数
126,パール入れた人
127,パール排出チェック
128,仕返し
131,お茶


140,畑仕事成功度
141,使用楽器
142,GipsLV

150,前回のASSIPLAYの履歴
151,前回の特殊COM
152,前回のダブル○○系コマンドにおけるTARGET以外の参加者（LOCAL）
153,前回のコマンド結果

160,サイズ表示
161,服装表示
162,能力表示
163,経験表示
164,性技表示
165,素質表示
166,刻印表示
167,道具表示
168,浮気歴表示
169,個人情報表示
170,PALAM非表示
171,Status非表示
;172,表示アイテム種類
173,USERCOM非表示
174,LOOK非表示

192,口上によるCOM成否判定
;(-2=コマンド終了、-1＝強制失敗、0=COM依存、1=強制成功0R強制大成功
193,SELECTCOMの分岐
194,SOURCEなどに影響しないSELECTCOMの分岐
195,遠距離移動
196,掃除量
197,水汲み
198,昼寝
199,一日一回
;(bit 1=弁当2=買い出し3=診察 4=特別商品 5=お宅訪問による翌日来訪 6=天候操作 7=弾幕勝負 8=射精判定 9=行きずり引っ掛けた 10=土産屋
; 11=お出かけイベント 12=告白 13=傘修理 14=調理の鉄人)
200,アルバイトで稼いだ金額
201,酔い止め
202,まかない
203,幸運補正
204,キャラリスト
205,運搬
206,遠距離移動その２
207,労働量
;208,傘耐久度
209,大衆浴場フラグ
210,大衆浴場時限入湯回数
211,旧地獄温泉フラグ
212,旧地獄温泉時限入湯回数
213,パンツ収奪
214,出張お掃除
215,デート前好感度
216,あなた起床
;TIME:3+DAY * 1440
217,七夕
218,重さ
219,移動不能メッセージ
220,カジノ入場時カリスマ
221,OPPAI
222,宴会場
223,仙香玉兎
224,GG設置位置
225,ポイズンボディ
226,描写中の子供
;育児中の子供は親のキャラ番号が入る,自立後は子供番号×1000+キャラ番号
227,泡風呂
228,マット貸し出し
229,デート道中
230,スカートめくりすぎ
231,膝枕した
232,マップ切り替え
233,直前モブ子マップ
234,弾幕補正１
235,弾幕補正２
236,宴会状態
;0=開始前、98=開催中(未確認)、99=開催中、100=終了(未確認)、101=終了
237,大荒れ予報の日

240,探索試行回数
241,会話回数
242,固有遭遇イベント
;地域別にbit管理

300,時間経過
301,
302,SKIPASSIKOJO
303,TRAIN_MESSAGE_CALLED

;500~603は引き継用に使用
;500~603は引き継用に使用
;キャラ数が増えた関係で500～630までは使用中（ver4.600proto現在）
;今後も実装キャラ数の増加に伴って使用領域が広がるはず
;ここは広域変数である必要性は薄いので@強くてニューゲーム内でDIMる仕様変更も可能
;custom code
900,GiftsHide
901,SeedUsed
902,ChildFuckUp
903,EjacChange
904,ScheduleHide
905,PreviousPerformances
906,HandlingDuplicateCharacter,;temp flag to store the id of the duplicated character we're working with so that we can use the CSV values of the original
907,ComPartner,;indicates if TARGET can join in on current COM
908,LastArea,;the area the player just left while moving to another area
909,HideSongs,;used to determine if songs should be displayed in the character info overview
910,MalletSemen,;semen enhanced by mallet
911,DangerousTravelBonus,;from daily travel fortune, affects risk
912,DangerousTravelDisaster,;from daily travel fortune, multiplier that increases chance of major disaster
913,ProposedToday,
914,HideFallingStates,;used to determine if falling states section should be collapsed in characer info
915,HideSkillAcquisition,used to determine if skill acquisition segment should be collapsed in character info
916,ウサギの出張お掃除, ;formerly 905 from tr branch, whoops
917,WeddingNight,;set during the wedding for deflowering purposes
