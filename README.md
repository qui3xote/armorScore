# armorScore

armorScore gives Destiny players a simple but powerful and objective way to evaluate armor in their inventory. By evaluating armor relative to all the other armor in a players inventory, it can identiy pieces that look strong on paper (i.e.high stat scores) but in fact aren't useful because they are eclipsed by other pieces. It is designed to work alongside Destiny Item Manager and make it simple to quickly tag items in bulk. 

armorScore works by looking at every possible armor loadout and every combination of 1,2,3,4,5 and 6 stats to determine which load has the highest score. If a piece of armor is in the 'best' loadout then it receives 1 point.  At the end, each piece's score is divided by the total number of winning combinations. So a helmet with a score of '.25' was present 25% of winning combinations. vO.1 takes exported DIM armor file and runs the and appends the final scores to the notes column (leaving existing notes intact). This can be reviewed in excel or reimported directly to DIM.


#Known Issues
1. The results look good to me, but I can’t guarantee anything. *It's still up to you to decide whether to keep or scrap your items.* 
2. I currently include all armor rarities in the ranking - if you have a lot of blue that you plan to shard, it could throw off your scores.
3. I don’t make special provisions for exotics (yet). That means a couple things: First, some of my ‘winning’ combos may include 2 exotics, which isn’t great and throws off the scores. Second, most of the time players want to build around their exotics - there may be pieces of armor that aren’t winners as a whole, but could be winners when we limit to combos that have at least one exotic in them.
4. I don’t account for ’tiers’ yet. Meaning that the winning combo has the highest absolute score, but there might be another loadout with the exact same tiers, just 1 point lower. This makes the ‘culling’ more aggressive.

#Using armorScore

Using armorScore currently requires a working python 3 environment with pandas installed. I hope to provide binary executables or possibly host it on a webpage in the near future. armorScore.py is run from the commandline and accepts the following arguments:

  -h, --help show this help message and exit

  -f FILENAME DIM export file to be processed.

  -o OUTPUTFILE  Where to store the results.


#Future Release Ideas:

'Exclude Blue' filter
Pin Exotics: Only consider combinations that include an exotic
Specify stat combos or specific stats (flag)
Rules based tagging?
Flag to clean out ArmorScore from notes
on re-run, overwrite existing scores