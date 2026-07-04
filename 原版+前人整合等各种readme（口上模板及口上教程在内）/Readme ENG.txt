Hello again, this is JPAnon once more, this time bringing over bugfixes and adjustments to both general functionality and dialogues previously done by various contributors on the English version, alongside some reworks and tweaks I figured would be easiest to do at the source.
This patch does not contain any new functionality, only bugfixes and reworks of internal logic to restructure existing functionality to increase robustness and prevent possible issues in the future. Some of these may overlap with fixes from previous patches not made by me, but I've made sure to migrate those over and it should not lead to any issues.
I've tested most of the major changes I made, but given the scope, it wasn't possible to test every instance in detail, so if any new issues pop up, let me know and I'll make sure to take a look at it. I'll be monitoring Shitaraba, so I'll write fixes for anything that I see there relating to this patch.
This finishes my second big patch. I hope to bring over marriage sometime around the end of the year, though I won't make any promises.

What follows is a list of the individual changes contained in this patch, with git links for convenience.

Changelog:

#SET_KOJO_COLOR did not always target correct character
Affects: @SET_KOJO_COLOR
The function inadvertently passed TARGET into KOJO_ACTIVE_INFO instead of ARG, which could lead to incorrect results.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/68692a18a67cef16e7a7701aa082d16405478a82

#Removed remaining instances of IRAIEXIST
Affects:
	Removed entirely: @M_KOJO_少女長_IRAIEXIST_K15, @M_KOJO_EN01_IRAIEXIST_K27, @M_KOJO_IRAIEXIST_KX (from M_KOJO_K27_依頼.ERB), @M_KOJO_EGG_IRAIEXIST_K50, @M_KOJO_長短髪_IRAIEXIST_K59, @M_KOJO_IRAIEXIST_K60, @M_KOJO_IRAIEXIST_K64, @M_KOJO_IRAIEXIST_K142
	Converted and removed: @M_KOJO_ふたてゐ_IRAIEXIST_K53 to @M_KOJO_ふたてゐ_CHECK_K53_IRAI_BLOCKED, @M_KOJO_IRAIEXIST_K107 to @M_KOJO_CHECK_K107_IRAI_BLOCKED, @M_KOJO_IRAIEXIST_K113 to @M_KOJO_CHECK_K113_IRAI_BLOCKED, @M_KOJO_IRAIEXIST_K131 to @M_KOJO_CHECK_K131_IRAI_BLOCKED
IRAIEXIST is no longer used and has been replaced by CHECKED_KX_IRAI_BLOCKED, but there were still many instances remaining in the codebase, which can be confusing to (new) authors.
Existing ones have now been converted to IRAI_BLOCKED or removed.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/b8dc5662c13084bd23c69d43f386d46df0c1ddd9

#Corrected names of unadjusted template functions
Affects: @M_KOJO_MESSAGE_COM_K9_SUIKA, @M_KOJO_IRAI_K27, @M_KOJO_IRAI_1_K27, @M_KOJO_IRAI_2_K27, @M_KOJO_IRAI_3_K27, @M_KOJO_IRAI_4_K27, @M_KOJO_IRAI_5_K27, @M_KOJO_IRAI_6_K27, @M_KOJO_IRAI_7_K27, @M_KOJO_IRAI_8_K27, @M_KOJO_IRAI_9_K27, @M_KOJO_IRAI_10_K27, @M_KOJO_IRAI_11_K27, @M_KOJO_IRAI_12_K27, @M_KOJO_IRAI_13_K27, @M_KOJO_IRAI_16_K27, @M_KOJO_IRAI_依頼名_K27, @M_KOJO_IRAI_Y_K30, @M_KOJO_EVENT_K100_GRAVITY, 
Some KOJO functions had not been renamed when they were copied from the original template. These have now all been adjusted to match the target dialogue.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/4998d48b628cedeac9f50270c55bd8be4f3bc3af

#Fixed incorrect consent checks
Affects: @OneNightStay, @COM357, @PRINT_STATE_PERSONAL, @M_KOJO_EVENT_K60_10, @M_KOJO_EVENT_K60_24, @M_KOJO_EVENT_K60_25, @M_KOJO_MESSAGE_COM_K139_337_1, @M_KOJO_MESSAGE_COM_K142_302_1
Negation is evaluated before Bitwise AND, which would cause "!CFLAG:既成事実 & 合意_うふふ" checks to never be resolved to true.
These bitwise checks are now wrapped in parentheses to ensure they're evaluated correctly.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/db6e1b1165006c902ef64898704349e93a92e2cf

#Fixed incorrect call for EVENT 8
Affects: @AFFAIR_DISCLOSURE
The calls did not pass the arguments the KOJO template expects, which causes dialogue to not show up when they were called.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/21b1df403b9f4dc94d10605005110a9b0dedb4f2

#Remove duplicate calls to DAILY_MESSAGE in Yumemi's dialogue
Affects: @M_KOJO_DAILY_EVENT_K9_2, @M_KOJO_DAILY_EVENT_K9_4, @M_KOJO_DAILY_EVENT_K9_12
These would cause the descriptions to be printed twice, as it was already handled in KOJO_MESSAGE_SEND.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/34b949143d7161eaf523ab3a860d4326dd59a937

#Fix target check in @IRAI_一般18
Affects: @IRAI_一般18
While technically impossible to reach at present, one check checked for TARGET instead of CHARA, which could lead to incorrect results.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/784ae1a14334c432c377773766036c06619da5ca

#Redundant check in @共通の寝室
Affects: @共通の寝室
The CFLAG:ARG:初期位置 == 99 was unnecessary as the CFLAG:ARG:初期位置 == SUKIMA() is more correct.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/c47f089033206bba3f18edea29ad90664206e52e

#Kaguya EVENT 31 fixes
Affects: @M_KOJO_EVENT_K62_31
EVENTEND_TSUBUYAKI is now only called if there is actual dialogue printed, preventing empty blocks at the end of day.
Additionally, the intended increase to the jealousy flag now sets the correct value, instead of the unused CFLAG:62.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/b5eefe26091514d934512607ec0a7e6da535bb2c

#Stone Stacking fixes
Affects: @COM633, @StoneBattle_record, @STONE_NAMESET
-Fixed an issue where the final rank could never be achieved as it would check for and set the wrong ranks
-Fixed an issue where the last category would be listed in the progress overview.
-Fixed an issue where %STONE_UKETSUKENAME% would not be printed correctly when setting the name.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/131ea56bfc20e70829bf42fe4188fea425ad33c2

#Incorrect check in Reisen's dialogue
Affects: @M_KOJO_SPEVENT_K52_3
A check in M_KOJO_SPEVENT_K52_3 inadvertently checked Kagerou instead of Reisen. This is now fixed.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/9be73925ce9c0b56f56a179663c882dd80102169

#Music Scores fixes
Affects: @GET_SCORE_INFO_NO, @楽譜入手_陥落, @楽譜入手_弾幕勝負, @IRAI_REPORT
Score conditions adjusted:
	-The Positive and Negative has been changed to 1010 (楽譜入手方法：ランダム（キャラ無し）), matching it with other scores linked to characters but don't match any characters currently in the game.
	-魔法陣　～ Magic Square is now correctly unlocked by Sara instead of Misumaru.
	-狂気の瞳　～ Invisible Full Moon (Eiyashou) and 狂気の瞳　～ Invisible Full Moon (Kaeizuka) are now correctly unlocked by Reisen instead of Tewi.
	-ヴォヤージュ1970 can now also be unlocked by Eirin, in addition to Kaguya, as it's a shared track.
	-封じられた妖怪　～ Lost Place is now correctly unlocked by Yamame instead of Kisume.
Added special checks in @楽譜入手_陥落 and @楽譜入手_弾幕勝負 for Yousei Daisensou, as the fall state and Danmaku scores could only be unlocked by Marisa (who is included on a lot of albums and as each character can only unlock one fall state score, and would likely make the full album unobtainable without NG+), and not any of the fairies, who hand out scores from successful requests instead of performing.
Fixed issue where requests from any character could unlock scores from Yousei Daisensou and not just requests by the fairies.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/2fe36aaf82dc027ddc3cb79aac0d329803bb1249

#Cooking fixes
Affects: @COM413
-Ensure selection is reset when initiating command.
-Adjusted item checks to only allow positive values above zero.
-Ensure SELECT_DRG_2 is set correctly instead of setting SELECT_DRG for alcohol additives.
-Check if player has the required items and additives before finalizing.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/196c215b9e03126ed2410bc80a86067fcf950319

#Update_ImageSets adjustments
Affects: @UPDATE, @Update_ImageSets, @Update_ImageSets_Print_Row, @SET_IMAGE_WITH_HEADER
-Remove Update_ImageSets from the character loop in UPDATE as it already loops over all characters, improving performance.
-Header text is now directly aligned with portraits, ensuring correct positioning even when not using the default font size.
-Header text is now correct even if there are more standing portraits than face portraits.
-Fixed issue where characters with only new standing portraits would print too many headers.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/8f8d75476259b7d45e9d61b3b44e09cf93b36346

#Fix incorrectly configured cooking specialty bonuses for Biten and Hisami
Affects: @キャラデータ153, @キャラデータ156
These would not be applied correctly as they did not follow the expected format. This is now fixed and made consistent.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/da1660dc9fda64836c3cad663bd7328e78eab7cf

#Fix issue where using chocolate in COM180 twice would remove the effect
Affects: @COM180
The command added a value to STAIN instead of setting a bit, so using it twice would effectively unset bit 7.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/78926d92c241990eb2053f46949436f7b11c30c7

#Maternity leave check uses hardcoded values instead of CFLAG:産休タイプ for value 0
Affects: @PERCIEVE
This brings the functionality in line with the documentation for CFLAG:産休タイプ as described in 更新内容・readme.txt and ensures it will follow the csv definitions and potential adjustments from KOJO if an author desires as such, with the exception of Yuugi, whose drinking "job" takes special consideration.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/9b652a91b60f8c5156a3720aa45986e0f613f1ac

#Adjusted PickRandGrownChild to work on a per-child basis
Affects: @PickRandGrownChild
The original function would check for a random character with children and then pick a random child of them, which gave equal weighting to each mother but made it hard for a child to be selected if they have many siblings.
The revised version weighs each child separately, putting them not at a disadvantage.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/6edc4781af33adfb3f72cebbab28be60b0d9d025

#Removed vestigial request blocking functionality
Affects: CFLAG:一般依頼禁止, @BAN_COMMON_IRAI
These functions have been replaced with the IRAI_BLOCKED KOJO functions, but part of the previous functionality still remained.
This cleans up the old flags and functionality to prevent confusion.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/e4e5420ab3e22e7b968dda8a1b36d00208ef5aba

#Fixed bug in Medicine's poison counter
Affects: @K75_POISON_COUNTER
Due to the way CFLAG:1301, CFLAG:1302, CFLAG:1303 are implemented, the strength of Medicine's poison would only ever increase over time as the player continues to interact with her, which would eventually overwhelm all methods of reducing the effect, unless the player takes her as their lover.
This reverses the effect for those values so that the player now gradually builds up the expected immunity, with the values being somewhat reduced to keep it from overwhelming the other methods of reducing the poison effect.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/3a4368434c60acfd1df4afef962921b7af4f996f

#Fix incorrect character checks in image functions
Affects: @IMAGE_I1_特殊服装, @IMAGE_I2_特殊服装, @IMAGE_I3_特殊服装, @IMAGE_I4_特殊服装, @IMAGE_I5_特殊服装, @IMAGE_I6_特殊服装, @IMAGE_I7_特殊服装, @IMAGE_I8_特殊服装, @IMAGE_I11_特殊服装, @IMAGE_I11_特殊表情
These checks did not pass a character as an argument, which would cause it to default to the value of TARGET, which would cause images to not work correctly if they're in the same room with other characters if they're not actively selected.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/37826311dea1a166b7590335d3ab7819ec097d6a

#Fix issue where ADD_EXP_LESNIAN would use the wrong character
Affects: @ADD_EXP_LESNIAN
The assignment did not set ARG and as such would always target TARGET, potentially leading to incorrect behavior.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/dd43e8228ea2de72017d32259706bc3b3152f5f7

#Remove general FIRSTTIME being set for COM
Affects: @TURN_RESET, @COM0, @COM700
TURN_RESET used to always set FIRSTTIME for each COM, which could cause problems in situations such as when the first time a command is used happening in time stop, and then later in normal circumstances, which would lead to dialogue not recognizing it as the first time if there is supposed to be unique dialogue for it.
Since the results of these specific ones were only ever used in KOJO and by COM0, it's now been reworked to make KOJO fully responsible for COM-based FIRSTTIME calls, fixing these issues.
COM0 has been adjusted to check for kissing experience instead of FIRSTTIME now, which should also make the check more robust and include end-of-date kisses.
Additionally, the kissing consent check has been fixed, similarly to the sex consent check, so it should now work correctly.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/735a78db9d13298b82fad97abfbed372d1cdab2e

#SCOM result would always be ignored if previous command failed
Affects: @CALL_COM
If a previous command failed (TFLAG:前回のコマンド結果 set to zero or negative), it would automatically prevent any SCOM from happening.
Under specific circumstances, such as being inserted into a girl and then opening the item menu (COM490), then closing it, it could make commands such as the raw COM72, COM73, COM74, COM75 available, even though those should always redirect to the associated SCOM command.
This fixes it by preventing TFLAG:50 from being reset and instead rely on the SCOM's conditions to check if it's allowed.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/76da6a67cb11d0a4ba04468785202de11b1d10cd

#PALAM_MESSAGE_A could be called multiple times, or incorrect dialogue called
Affects: @KOJO_MESSAGE_PALAMCNG_CHECK, @KOJO_MESSAGE_PALAMCNG_A2
For commands that affect multiple people, PALAM_MESSAGE_A would be called for each separately, leading to duplicate, conflicting text.
This ensures that it's only called for the primary TARGET. Dialogue is still triggered normally.
The dialogue call for type 21 (パイズリフェラ) has also been corrected.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/d240659cb5878414d0b3931bd14f8a8ec905b41f

#Ensure TARGET is cleared if character is not present
Affects: @SOURCE_CHECK
It's possible for a TARGET to not be present through child interactions or if they move through dialogue, which could cause issues.
This ensures that the value is reset if it would ever be invalid.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/6eef1cbad91a590951069b32ed0629cf55354c07

#Fix issue where nearby oni would be included in bean throwing
Affects: @COM364
The check inadvertently checked for LOCAL instead of the intended TARGET:LOCAL.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/17e55d8c2aabd26dcf513c22dde6c181f935d285

#Prevent Rotor being printed twice
Affects: @COM40
The name of the command is already printed elsewhere, so this leads to duplicate text.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/ec9809895cd7df92a80bacadc8d3281edd0ed91b

#Prevent potential crash during sleep time calculation
Affects: @睡眠時間２
This could only occur with an alternate Chinese-origin Yorihime which is not in the Japanese version at present, but this will preempt possible future issues.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/22ce2ab25b1926f516e30aefae4bc39b70e3e1d8

#Workload would not be set on day change
Affects: @INFO_GO_NEXTDAY
Since BASE:仕事量 would only be set when the player wakes up, it wouldn't be set correctly if the player stays up until the next day, causing characters not to do their work.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/6837cc78e6553c3e1b356815bc4bc9cc9af8c6e7

#Breast blessing fixes and adjustments
Affects: @OPPAIANSWER, @PREGNANCY_BREAST_GROWTH_PERIOD
-MASTER is now a valid possible target.
-Target is not valid if male.
-Allow increase even if pushed to max because of pregnancy, this will instead remove the pregnancy adjustment so that it remains at max after pregnancy.
-Cannot increase below -1 if pregnant.
-Added checks to invalid input returning player to menu, instead of doing nothing.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/2c576fba6fd4e7a3d4cd439f3f794299568d981a

#Show current clothes in portrait when a character walks in
Affects: @AFFAIR_DISCLOSURE
This ensures that a character is always depicted in their active outfit (or lack of clothes) when they appear in AFFAIR_DISCLOSURE.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/cfdca8b1c1377ecc971cf430c0156a5d1cbb1baf

#Fix issue where lubrication did not increase shame gain
Affects: @SOURCE_露出
The value would end up as zero in all circumstances that did not involve Shinmyoumaru, making it not work as intended.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/a96dffa2450ab35129e981dce1b17475b1c43b51

#Only allow food delivery outside of timestop
Affects: @一般依頼17, @一般依頼18
Simple added check for immersion.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/744f0521aa6f257fc6dcb89270f4c16105eb0f26

#The message for a character leaving for work could trigger multiple times
Affects: @訪問帰宅処理
If a character is working before or after their outdoors hours, it would lead to them being transported to their home area each turn before being transported back to their work area, triggering their "leave for work" message every turn, while preventing their "is working" message from showing up correctly.
This fixes it by preventing 訪問帰宅処理 from doing anything while a character is working.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/396e3a1ca278fba9e2b37c8e1ea7f2793c9fc9d7

#NAME_FROM_PLACE does not work correctly for 灼熱地獄跡
Affects: @NAME_FROM_PLACE
This would trigger the ROAD_TO(MAPID) check, leading to an incorrect message when Yuuma leaves for work.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/3dbdb72279f4d579368862c6f1c46dce59119d7c

#Allowed entry into house check for characters with multiple rooms would allow it even if asleep
Affects: @MAP_CAN_MOVE_6, @MAP_CAN_MOVE_10, @OTHER_IN_ROOM_NUMBER
This check would succeed even if the owner is asleep, allowing the player free entry. It now only succeeds if anyone other than the owner is present.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/cabc394f40267b7df096ce98861b6269f517fd1c

#Some commands would add the wrong kind of same-sex exp to player
Affects: @COM313, @COM315, @SCOM62
These would always add to EXP:レズ経験 instead of checking for the correct type.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/9cb14a7d480caf072714f3e5fef4336c1ce51075

#A character losing their virginity as part of the ONABARE function could still be considered as sleeping
Affects: @SET_HISTORY_LOST_V, @HISTORY_LOST_TEXT
These checks did not properly check for this situation, so their virginity loss text would be marked as happening while asleep if it triggers during their sleeping time.
Additionally, this fixes an issue where SET_HISTORY_LOST_V would never set the unaware virginity loss talent.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/7c65f8954ce6c9143652a7b839bc84c2728b3a15

#KOJO calls for masturbation passed incorrect values for scenario 6
Affects: @ONANISM
For the high masturbation addiction scenario (自慰タイプ = 6), it would pass the value 3 for the vaginal+anal sub-scenario, and the value 1 for pure vaginal.
However, dialogue expects the values 1 and 2, respectively, so this would trigger the wrong dialogue or none at all.
This has been adjusted to match the templates and dialogues, and should now work as expected.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/146109241a3be63ee3f413df376f2bc485efc69f

#Clear next counter command when sex ends
Affects: @ENDUFUFU
TCVAR:次回カウンター would not be cleared when sex ends, which could cause it to trigger even though it's no longer valid. It's now cleared to prevent any issues.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/de70ce86fd9285133dc6416dc0dc53ccbcc212ef

#Profile descriptions for V/A insertion size check trigger when they shouldn't
Affects: @肉体情報
Insertion with a difference of 1 should be possible with either TALENT:禁断の知識 or enough EXP, but the check required both to be valid to keep it from printing the message.
It has been changed to an AND check to ensure that it only prints the text if the character both lacks the EXP and the player doesn't have the talent.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/0c15c8f0a39a6acbf2d517a4a222e4f4c312d018

#Fixes/adjustments to alternate dialogue handling
Affects: @情景描写, @UPDATE, @SKIP_MOVE, @PRINT_STATE_PERSONAL, @SPTALK, @KOJO_MESSAGE_SEND, @EVENT_COUNTE_MESSAGE(141-145), @CCOMF(141-145), @CCOM_ABLE(141-145), @CCOM_ORDER(141-145), @UNIQUE_COUNTER, @UNIQUE_COUNTER_ABLE, @UNIQUE_COUNTER_ORDER
-Manual calls to M_KOJO_K have been changed to KOJO_ACTIVE_INFO where possible.
-A remaining manual call to M_KOJO_COLOR_K that did not check for alternate dialogues has been changed to SET_KOJO_COLOR.
-A call to M_KOJO_EVENT_K{NO:TARGET}_26_1 in KOJO_MESSAGE_SEND now checks for alternate dialogues.
-Unique character counter commands have been reworked to function with alternate dialogues, and their logic made reusable.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/5d46c293898ec26057ceb3584507183857ccb5e8

#Firewood request did not check for correct quantity
Affects: @一般依頼14
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/f189627a21ad72dfdf6891e2fdc25a13f293b7cd

#When helping with work, work end dialogue could trigger before the work assistance dialogue
Affects: @COM304
COM304 called CHARA_JOBEND if the player's assistance pushed the remaining work value below zero. This has been removed to allow it to be handled by the normal system, which ensures a correct flow of dialogue.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/80ac8c5ffdc58b02addf6ea13f229db95c21e3ce

#Unaware virginity loss message could trigger after consensual sex
Affects: @COM355
The virginity loss flag was only cleared for nearby characters if the player triggers time stop, which could cause issues if the player moves away first.
It's now cleared for all characters, always.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/4fb02633b6e7d155dc0e4d1fa4ca7901de5718da

#Stone Stacking Contest adjustments
Affects: @STONEBATTLE, @STONECombiBattle, @STONE_STACKING_LUST_PENALTY
This makes some fixes and adjustments to how lust/desire(欲望) penalties are handled for both solo and duo play to make it more enjoyable.
-Fixed issue that would cause a crash if the player or their partner had zero lust in duo play.
-Lust penalty for solo play is now randomized like the duo penalty, and correctly checks MASTER instead of TARGET.
-Lust penalty is now capped to 25 if the player is under the WISEMAN effect, preventing the game from eventually becoming unwinnable. Penalty for partner is capped if they have less than 5% sexual frustration.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/aac696d7398723b9f991b20f5b5a73e8f5be482f

#Being kicked out for loitering at Kourindou could lead to a crash
Affects: @MESSAGE_COM626
An invalid value would be passed to SPTALK, causing a crash. This is now fixed.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/a3130860fa8f50cdb80215991c8a66305921a461

#Random mob fight from GO_OUT_EV1 could lead to MOVEMENT LOCATION ERROR
Affects: @GO_OUT_EV1
The mob is now moved to SUKIMA() if the player escapes or otherwise resolves the battle without taking the mob girl along, preventing this issue.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/9416994b94c7c6580c31b3373e85463d21405741

#Using King Crimson in Danmaku would not correctly reset the background color if FLAG:背景色推移 is disabled
Affects: @DANMAKU_BATTLE
It now correctly checks for FLAG:背景色推移 before calling SET_MAP_WEATHER_BGCOLOR.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/eae764b19ffa4eedb07b49eebd45146ae3e07ef6

#Ensure mobs loaded from previous versions are properly upgraded
Affects: @LOAD_MOBGIRL
This ensures that the value of NO and the sprites are all corrected when a mob girl is loaded from a save.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/72fcebe815339e3d30745c5e66b91fc06b7d8eff

#Ensure uncollectible panties are never marked as not collected
Affects: @PANTS_ALREADY_COLLECTED
The steal panties command could be printed pink in situations like with bikini bottoms, but since those aren't collectible, it could lead to confusion.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/4cb7cf898ef58e2c1e64aee5c0a05653bcdcda6f

#Travel time from shrine to moon was incorrect
Affects: @TIME_REQUIRED0
It now follows the table on top, and matches the moon->shrine time.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/d6b37377da2806396553f1d1cdc9ed31fb3e1ae6

#EVENTCOMEND pushed arguments to TIME_REQUIRED in wrong order
Affects: @EVENTCOMEND (EVENTCOMEND.ERB)
Arguments were flipped, and while this generally wouldn't cause issues since travel times are symmetrical, it could lead to incorrect behavior if they weren't.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/92e35665d76dc944afdc241929dbbeaa439af50b

#Fixed issue with stealth sex not being correctly checked for when a character goes to sleep
Affects: @CHARA_SLEEP
Since BASE:潜伏率 isn't cleared, it could lead to incorrect behavior even after sex ends. It's now changed to only trigger while actively doing stealth sex.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/ba8d000c335c02f83101a34ddf361ce6c3a83554

#Ensure CCOMs always trigger correctly during reverse sex
Affects: @EVENT_COUNTER
CCOMs do not trigger after certain commands, but this would cause issues if the player is pushed down by a character, since that could lead to the first one not triggering correctly.
This fixes it so that they're always allowed while pushed down.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/1249798f8a3ed9da6dfc8ca98a61d4c35497fd15

#Ensure TARGET is valid if character leaves through dialogue
Affects:  @INFO_RENEW_TARGET, @SOURCE_CHECK, @IN_ROOM_MEMBER
If a character is scripted to leave in their greeting dialogue (such as the disabled Kagerou code), it could lead to TARGET being set to an invalid value.
This ensures that the value of TARGET is set to a correct one if that ever happens, through an updated case in IN_ROOM_MEMBER that allows for selecting a random person in a specified area.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/695517e5f36f0d1f38c2716864230f38ef06f263

#RAND_PLACE place could decide on an unreacheable area for Bamboo Forest of the Lost
Affects: @RAND_PLACE
The location 8402 (永遠亭玄関) is no longer in use, which would cause issues when dealing with requests that place an item in this area, which would be impossible if the player chose the Bamboo Forest as their home map.
This moves this option to 8405 (調剤室), which is always accessible.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/6438acbd1a0430e0d284038428b2660a6b6114e5

#Negative reactions to COM330 increase MASTER's STA instead of decreasing it
Affects: @COM330
It now correctly decreases it, as would be expected.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/139f0c3b5d1b8c58ce8f2c307ab4713708492715

#Cancelling out of COM444 would still set the mob flag
Affects: @COM444
Bit 9 of TFLAG:一日一回 would always be set if the player invokes this command, even if they do not choose any mobs, which would cause the end-of-day question to trigger regardless.
It is now only set if the player actually invites a mob girl.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/3bdb544631be29145574060bef6fe7cff641ac2f

#Selecting the option to return to the player's room while already in that room would move them two spaces
Affects: @COM400
A check has been added to prevent any movement if the player is already at the destination.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/67331e8ca302f5ff387b858e3ba079c38cebdc22

#Flags for TSP pranks would only be cleared if the player is present, and some messages could trigger repeatedly
Affects: @時間停止解除, @EVENTCOMEND (EVENTCOMEND.ERB), @TIMESTOP_RESET
Dialogue changes: Hatate, Satori, Tewi, Meiling, Parsee, Eirin, Tsukasa
Template changes: @M_KOJO_EVENT_KX_17, @M_KOJO_XXX_EVENT_KX_17
This fixes various issues with the post-time stop sex handling for characters.
-The stolen panty message now no longer triggers every time the player cancels time stop. This is done by setting the CFLAG:ノーパン to 3 when time stop ends, if the previous value was 1. Existing dialogues that solely checked for 1 have been adjusted to also check for 3 in those instances.
-The dialogue for unconscious semen on face now clears the correct CFLAG, and no longer repeats like the stolen panty message.
-The flags associated with time stop sex are now always cleared even if the character is not in the same location as the player, as this could lead to situations where a character responds to their situation well after the actual event.
-Additionally, a new set of options for EVENT 17 have been added which trigger only if the character is not in the same location as the player, for situations where it's desirable to perform special handling for the character in question. I've also adjusted the existing templates to account for these.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/5961b407d54d3114fe5317abde9d1019565e879c

#Non-default body size for Shinmyoumaru is not restored correctly when using Miracle Mallet
Affects: @COM428
If the player adjusts Shinmyoumaru's default body size (such as through NG+), and then uses the Miracle Mallet to adjust her size, it would always be set to -5 the following day.
It now sets the value of CFLAG:変異前の形状 to ensure it will be reset to the original value the following day.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/e0fde39a55781b7d1d52f7bc1300ae7e220cedb2

#Move dialogue-specific image code to KOJO functions
Affects: @PrintOnanismImage, @GET_BASE_RESOURCE, @GET表情体形完整, @GET表情体形拆分组合, @GET_EFFECT_RESOURCE, @IMAGE_CHARA_OVERRIDE
	, @GET_BASE_RESOURCE_TRANS, @GET_EFFECT_RESOURCE_TRANS
	, @KOJO_MESSAGE_SEND
Dialogues affected: _ふらん Flandre, _長短髪 Koakuma, Eiki, Byakuren, Yuugi
Templates affected: M_KOJO_KX_IMAGE.ERB, M_KOJO_KX_X2_IMAGE.ERB
This allows dialogues to easily have their own logic specific to them without having to integrate it into the character's general image logic, reducing dependency on the dialogue's index and allowing for cleaner code. It will also prevent any potential issues should alternate dialogues be added later.
The KOJO image functions work similarly to the ones in IMAGE_IXX_○○.ERB, and will override the general functions if they return a value. Returning a negative value is treated as zero for any subsequent logic, but will still block the general function from being triggered.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/c11e6f26ce16d8bebb00dfdca764d34f742d7a60
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/04cc2724f14a8ed2a516f55c72cdda1bb3557e32

#Fix incorrect CHARA_INFO function name for _長短髪 Koakuma
Affects: @CHARA_INFO_KOJO_長短髪_K59
The text is intended for the alternate dialogue, but the function could only be called for the default dialogue.
It's now properly tied to the specific dialogue.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/9527d8fa366490ddc0b3a26046cea2fa07b6b1e8

#Partial reversion of CHARASORT_EX and MAKE_CHARA_LIST
Affects: @CHARASORT_EX, @MAKE_CHARA_LIST, @TARGETSET_CHACK, @RAND_CHARASELECT, @TEMP_SHOW_CHARA_LIST, @TEMP_FULL_ROSTER, @PREGNANCY_TYPE_OPTIONS, @登場キャラ切り替え, @DEBUG_IRAI_HAPPEN
	, @SHOW_APPEAR_LIST, @OPPAIANSWER, @SHOW_CHALALIST, @HITOSAGASI_2, @COM429, @SET_MIRADA, @SHOW_CHARA_LIST
CHARASORT_EX and MAKE_CHARA_LIST had been changed to #FUNCTIONs in a previous update, but as they're purely display-related functions and not expected to return a singular value as is expected from those, this could lead to some confusion in their usage.
MAKE_CHARA_LIST has been fully reverted to its previous state, while CHARASORT_EX retains the revised order but has been moved back to COMMON.ERB as its functionality is used beyond just the UPDATE functionality.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/9c72d4e65e01ecf0eb73ab898713a6467150a50b
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/e5a4f8972965655a3a886cb19c23444b90c0ee89

#Fix issue where QUICKFILTER for some categories would be unavailable to toggle despite commands being available
Affects: @フィルタ表示
COM316 and COM314 are covered in the V/A filters (in addition to the セクハラ filter), but as the toggles for the V and A filters are only available during sex, it would be impossible to enable them outside of it. These have been changed to always be available again.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/3890aa836ba440790c7a5061e91485d7ae121d01

#Field selection for MUSHI battles did not check for available fields for the current area
Affects: @SELECT_RANDOM_MUSHI_FIELD, @FIELD_SETBIT, @MUSHI_BATTLE_SELECTION, @NPC_MUSHI_BATTLE_SELECTION, MUSHI_ERH.ERH
A previous update changed a check in NPC_MUSHI_BATTLE_SELECTION from bitwise AND to bitwise OR, which would always evaluate to true, and effectively just pick any field instead of restricting it to those available in the given area.
I've moved it into a separate function and rewritten the logic to hopefully be clearer, along with adding more safety checks and a CONST for the maximum amount of field types, in case it ever gets expanded.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/8cab158d31d59ece18d83e3f2b525332a62f6de0

#Prevent Bites the Dust being triggered during the day
Affects: @OPTION
With the check disabled entirely, it was still possible to trigger it by typing in the option number manually, which could lead to unpredictable results.
I've fixed the check so it is now only possible to trigger it from the main menu, and not from the CONFIG menu during the day.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/0c62815cf9e0749bbfc0348332a7a5de681d5bd4

#Fixed CHECK_CLO checks for Shinmyoumaru
Affects: @IMAGE_I71_特殊服装
These checks didn't pass the character as an argument, so it would default to TARGET, which would lead to wrong result while looking at a different character.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/cb0a95267efcadd7bdc7a38c3210eef4966598f9

#Fixed debug log generating countless empty lines
Affects: @TEST_TEMPLIST
This would print large amounts of empty lines in the debug log each turn, making it hard to actually use it.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/fc809767d8ca131efdd68288a7d56b6864a32257

#Adjustments to image handling for shapeshifting
Affects: @IMAGE_CHARA_OVERRIDE, @GET_BASE_RESOURCE_TRANS, @GET表情体形完整_TRANS, @GET表情体形拆分组合_TRANS, @GET_FACETYPE_TRANS, @GET_EFFECT_RESOURCE_TRANS, most Chara_data files
This should allow a shapeshifted character (_別人変身版 Mamizou) to properly use most of the target character's alternate outfits and special effects as if they were the character themselves.
The logic in the image files is now split between the parts which are fixed to the character being transformed into (chiefly which image set is used), and the logic for a character's state, which is checked on the transforming character.
KOJO_MESSAGE_SEND has also been expanded to allow a different TARGET to be set for the IMAGE category than the dialogue/functions that will be used, though since that often relies on internal logic and character-unique variables, it won't apply the image logic in all cases. The code for those has been adjusted to check for the appropriate situation.
Furthermore, all checks to a character's outfit have been replaced with the simpler and more robust CURRENT_CLOTHES_SET for consistency.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/a9834697eb6e985350d2a7e39949ca952ed5136e

#Fix toggle for KOJO COM filter not being applied correctly
Affects: @QUICKFILTER
A previous update flipped the check in フィルタ表示 to show custom commands by default, but as QUICKFILTER had not been changed to match, this led to custom commands only being shown if the toggle was disabled.
This has now been fixed.
Additionally, I've changed the name of the CFLAG to match the adjusted functionality.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/4e7219cabed975773013a740ee165118cab257b5

#Remove unnecessary character-specific function in danmaku code
Affects: @DANMAKU_BATTLE, @POST_DANMAKU_CLOTHING_SET_156
After every danmaku battle, even those against other characters, the game would trigger a custom refresh specifically for Hisami, whose outfit changes after losing.
As it's generally undesireable to place such character-dependent code in general functions, and it's redundant since INFO_RENEW_EQUIP already triggers a refresh for all characters each turn, this has been removed to clean it up.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/cee749425641342a9660ed87451e76b89d58ed58

#No MARK dialogue shown for some characters
Dialogues affected: Star, Marisa, Lily White, Mystia, Sanae, Nazrin, Kogasa, Nue, Kasen, Rika, Flandre, Nitori, _ふたてゐ Tewi, Patchouli, Keine, Shinmyoumaru, Komachi, Shou, Kyouko, Seiga, Benben, Yatsuhashi, Raiko, Sagume, Hecatia, Kutaka, Mayumi, Miyoi
These characters have the MESSAGECHECK set for MARKCNG, but have no actual dialogue or descriptions written for it, causing those events to print nothing if triggered.
Other ones did not block the standard descriptions with a MESSAGECHECK but would still call MARK_MESSAGE manually, which would lead to duplicate text.
This comes from an old issue with old templates never calling MARK_MESSAGE, which is since fixed in the templates, but still persisted in a number of dialogues.
These have now been fixed.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/ee30e74560798fe00e28c4066acaf447728c8aff

Changes after this have been discovered through automated analysis of the code base, which may exclude edge cases.

#Wrong character's function being called in dialogue
Dialogues affected: Seiga
Seiga would use Miyoi's text color for one CCOM. This is now fixed.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/63038ad78cd57dbff1d557ace708d3e86f8f89f0

#Characters with disabled dialogue blocks
Dialogues affected: Reimu, _無個性 Reimu, Yumemi, Alice, Wriggle, Kanako, Suwako, Iku, Okuu, Nue, Ellen, Flandre, _EGG Flandre, Nitori, Reisen, Tewi, Patchouli, Miko, Kokoro, Koakuma, Mokou, Momiji, Shinmyoumaru, Eirin, Sekibanki, Komachi, Hina, Akyuu, Ichirin, Shou, Kyouko, Seiga, Yatsuhashi, Seija, Tokiko, Yuki, Sumireko, Clownpiece, Junko, Okina, Joon, Shion, Kutaka, Yachie, Tsukasa, Megumu, Momoyo, Enoko
These characters had blocks of dialogues that would never be used because the LOCAL toggle was set to zero but did have dialogue written for them.
It's possible that some of these were done on purpose, but as it's more likely that it was in error, so I've enabled the ones that looked complete here, while the obviously incomplete ones remain disabled.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/033d5fd9cbba3910567e9075f38574cbba42bb9d

#Characters who could trigger conscious dialogue during time stop
Dialogues affected: Reimu, _無個性 Reimu, Daiyousei, Eiki, Yuyuko, Seija, Yumeko
These characters have CFLAG:時間停止口上有 enabled but did not check for it in dialogue in all cases and would display regular dialogue during time stop.
These have been adjusted to prevent such occurrences.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/690db5b07a7b983b229fc2e01e28f08c23b1370f

#Characters with dialogue that should be SCOM instead of COM
Dialogues affected: Reimu, _無個性 Reimu, _tokicoli Lily White, _早苗追加 Sanae, Rika, Satori, Kagerou, Hina, Tokiko, Clownpiece
These commands can only trigger as SCOM, but for many characters are instead written for the base COM command and as such could never trigger.
These have been moved to the appropriate SCOM. I've also removed these from the templates to prevent future confusion.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/d33e97ca10c7f4615f37305b74b3d4b80bd46a74

#SELECTCASE instances not being able to reach all cases
Dialogues affected: Yumemi, Cirno, Remilia, _tokicoli Lily White, Wriggle, _EN01 Wriggle, Eiki, _早苗追加 Sanae, Kanako, Iku, _ENG01 Orin, Okuu, Hatate, Kasen, Reisen, Tewi, _ふたてゐ Tewi, Kokoro, Meiling, Momiji, Keine, Kosuzu, Eirin, Letty, Komachi, Tokiko, Mai (Kaikidan), Seiran, Ringo, Clownpiece, Hecatia, Okina, Mayumi, Tsukasa
For these, not all cases were accessible from the RAND call, had duplicate cases, or had no content written. These have been rewritten to use a IFRAND to only check for the correct cases.
Link: https://gitgud.io/JPAnon/japanese-fixes/-/commit/b3ccc708e3d822ac92fe0c9d5d5b1e676f8b16f3
