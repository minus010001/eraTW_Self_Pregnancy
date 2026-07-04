==============================================================
= Readme:
=	Emuera1824+v11+webp+test+Fix for Webp Exeption.
=		2021/03/01 by M
==============================================================

●概要
 このFixは、東etoマン氏のEmuera1829+v9+WebP_fixtest0001 として投稿された
 起動時エラー改善パッチに、昔一度挫折した残骸をサルベージ＆マージして、
 Emuera1824+v11 にリベースしたものです。
 正直、表に出すのも恥ずかしいコード品質ですが、恥を忍んで出しちゃいます。

●ライセンス
 Emuera本体側の改変に関しては本体のライセンスに準じます。
 WebPWrapper.cs 側に関しても同様にWebpWrapper の MITライセンス に準じます。

●同梱内容
★ Emuera_readme.txt
	本家readme。よく読んで。
★ 私家改造版Emuera_readme.txt
	Emuera1824+v11のreadme。よく読んで。
★ Readme for test+Fix.txt
	このファイルです。
★ Emuera1824+v11+webp+test+fix.exe
	Emuera本体 VS 2019 16.8.6 で Release ビルドしています
★ src1824+v11+webp+test+fix.7z
	ソース、変更箇所は下記
★ libwebp_x64.dll
★ libwebp_x86.dll
	動作確認用 libwebp.dll。NMAKE Version 19.28.29910 で私家ビルド (/favor:Blend)

●変更内容:
▼Ver 0.1.0
  Based on Emuera1829+v9+WebP_fixtest0001 by 東etoマン氏
  Based on Emuera1824+v11 by 妊）|дﾟ)の中の人

・ADD:    WebPライブラリに 専用Exeptionクラス WebPExeption を用意
・CHANGE: WebPのLoadで、ファイル読み込み時アクセスエラーは3回までリトライするように
・FIX:    Webpファイルかどうかの判定変更。
          パスに".webp"が含まれているかどうか、から拡張子が".webp"かどうかに変更
          (パスにwebpが入っていたら、拡張子じゃなくてもwebpラッパーが呼ばれてた…)
・CHANGE: 受け手の AppContents.cs で WebPExeption を処理。エラー時の処置を分離
・ADD:    Creator.Method.cs でも WebPライブラリを呼ぶように
          (これでGREATE系命令でwebpファイルが使えるかも？
          ただ、恥ずかしながらGREATE系命令群のテストスクリプトがわからず、未テストです)
・CHANGE: パス区切り文字(\)・パス区切り補助文字(/)を、ハードコードではなく
          .NET Framework から参照するように (別Forkで4.8化してる都合上…)
	Config/Config.cs
	Config/ConfigData.cs
	ContentAppContents.cs
	Program.cs
	Sys.cs


●お願い
  MSYS2/Mingw-64 や Intelコンパイラ、Clang/LLVM、Un*xクロスビルド環境などがあるなら
  できれば、それぞれでビルドした libwebp_x(64/86).dll を使ってみてください。
  あと、MONO でも通るかどうかも。

  (当方だとなぜか、古いVerのmingw64 gcc でビルドした libwebpで
   発生する例外が VCビルドの物と違ったり… 一応対応したつもりですが)

[EOF]
