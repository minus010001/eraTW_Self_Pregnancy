Hello once again.
This is JPAnon here (English Hecatia's author), porting over the brewing guide feature I've written for the English version of TW, meant to make it  easier for a player to learn and remember the recipes for the various drinks in the game.
The brewing guide is an unlockable feature that lists all the sake bug recipes the player has previously learned, showing them as a list of options with the required ingredients, brewing time, and possible results.

It's unlocked through a set of two new achievements, which progress the player in the new 酒造家 TALENT.
The first rank is unlocked by brewing (or mixing) 10 different drinks, which unlocks the brewing guide and slightly increases the yield of the sake bug.
The second rank is unlocked by brewing or mixing all different drinks, which speeds up each brewing step slightly to a minimum of two days, which especially benefits the complex recipes.
For the two ranks, I used the terms 酒造家 and 杜氏. If these are not appropriate, please feel free to change them.

To facilitate the brewing guide, I've reworked how adding ingredients is handled in the code. @COM450_1, which previously hardcoded all the additions, has been replaced with @BREWING_GUIDE_MIX_MENU, which reads the various recipes from 酒関連.ERB, which has been expanded to contain all the information required. This also makes it easier to add new drinks and recipes, as everything required is now found in the same file, and allow the brewing menu to list the valid options dynamically instead of leaving most of them greyed out.
The following fields have been added:
CASE "ADDITIONS"
	This lists the various ingredients that can be added to the current content of the sake bug. All options are separated by a ／, and are used in the other fields.
	For steps that require two or more ingredients to be added at the same time, they should be linked together with a ＋ (e.g. "蒸留酒＋甘味材")
CASE "ITEM：[INGREDIENT(S) NAME]"
	This lists the name of the immediate result of adding the ingredients, often an intermediate stage.
CASE "QUANTITY：[INGREDIENT NAME]"
	This lists the quantity of a specific ingredient required.
	For steps that add two or more ingredients at once, this requires a separate field for each ingredient.
CASE "EXTRA：[INGREDIENT(S) NAME]"
	This lists any extra item the player receives for adding a particular set of ingredients, such as ポマース.
CASE "EXTRAQUANTITY：[INGREDIENT(S) NAME]"
	This lists the quantity of the extra item the player receives.
CASE "SPEED：[INGREDIENT(S) NAME]"
	This lists how many days the current brewing stage is sped up if a particular ingredient is added.
	Currently only valid for adding どぶろく to ただの水.
These fields are sufficient to handle all existing recipes.

For existing saves, the player's inventory is scanned for any valid drinks. Those will automatically be considered as having previously been brewed, filling out parts of the guide where possible.
Various existing characters have had their .csv files adjusted to add the new talent, where appropriate.

As I am not versed in the Japanese languages, a few parts will still need to be translated, which have all been marked with ";brewing todo translation" for convenience.
This affects the following functions:
@PRINT_BONUS_7
@REWARD_BONUS_7
@BONUS_NAME_7
@BREWING_GUIDE
@BREWING_GUIDE_WALK_ALL_PATHS
@BREWING_GUIDE_WRITE_PATH
@BREWING_GUIDE_COLOR_DRINK
@BREWING_GUIDE_MIX_MENU


Additionally, I've fixed a bug in @酒データ56 that led it to disappear after once day, as the "醸造日数" field was inadvertently set.
I've also rewritten @ALC_ID and @IS_ALC for performance. It now uses a map data structure initialized once at the start of the game to find the id belonging to a name instead of looping over every option each time.

I've put this patch in source control, which can be found here, which should help to get an overview of all the changes: https://gitgud.io/JPAnon/japanese-fixes/-/commit/b779a506df0df6930bc34f5e33717336db3b80be

I hope this will be sufficient to explain all the new features and changes that have been made to the existing functionality.
Additionally, I've made a separate patch which fixes some of the issues I found in the 4.973 release.

After this, I intend to bring over a lot of minor bugfixes that have previously been fixed on the English version.
After that's finished, I intend to look into bringing over content relating to marriage and concubinage, though this will require significant translation efforts on the Japanese side to complete.
