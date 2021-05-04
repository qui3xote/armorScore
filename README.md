# armorScore

armorScore gives Destiny players a simple but powerful and objective way to evaluate armor in their inventory. By evaluating armor relative to all the other armor in a players inventory, it can identiy pieces that look strong on paper (i.e.high stat scores) but in fact aren't useful because they are eclipsed by other pieces. It is designed to work alongside Destiny Item Manager and make it simple to quickly tag items in bulk. 

armorScore works by looking at every possible armor loadout and every combination of 1,2,3,4,5 and 6 stats to determine which load has the highest score. If a piece of armor is in the 'best' loadout then it receives 1 point.  At the end, each piece's score is divided by the total number of winning combinations. So a helmet with a score of '.25' was present 25% of winning combinations. vO.1 takes exported DIM armor file and runs the and appends the final scores to the notes column (leaving existing notes intact). This can be reviewed in excel or reimported directly to DIM.


#Known Issues
The results look good to me, but I can’t guarantee anything. *It's still up to you to decide whether to keep or scrap your items.* 

#Using armorScore

Using armorScore currently requires a working python 3 environment with pandas installed. I hope to provide binary executables or possibly host it on a webpage in the near future. armorScore.py is run from the commandline and accepts the following arguments:

  -h, --help show this help message and exit

  -o OUTPUTFILE  Where to store the results.

  -t use tiers instead of raw scores when selecting winners. Results in more ties and therefore more armor gets a score above zero.

  -b include blue items in scoring. By default armorScore only looks at legendary and exotic items.

  -e Pin,Prefer,Ignore How to handle exotic items. 
        Ignore will treat all loadouts equally regardless of whether they contain an exotic.
        Pin will only look at loadouts containing an exotic item.
        Prefer will score twice. Once for all loadouts, then once again for loadouts containing an exotic.

  -c will remote armorScores from the notes column and writeout a new file without running any scores.