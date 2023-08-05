## Intro

Ever get your SO/ hot date/ that bartender that kinda looks like Ryan
Gosling back to your place and when you go to put on some sweet jams for
a long night of ~~awkward hip convulsions~~ sexy fun times only to have
the mood somewhat dampened by the time it takes to open up your browser,
find a playlist and then click play? Enter Get Lucky, a command line interface that uses Songza to quickly set
the mood.
 
Enter Get Lucky.

Get Lucky is a command line interface that for Songza that'll let you set the mood with almost with minimal time at your computer.

## Installation
Get Lucky can be installed via pip.
On Linux/OSX:
```
sudo pip install GetLucky

```
On Windows:

```
pip install GetLucky
```

Or
```
git clone git://github.com/TannerBaldus/getlucky.git
cd getlucky/GetLucky
python setup.py install
```


## Usage

###Help Message ###
To view the help documentation you enter the command ```gl ``` or the option ```-h``` / ```--help``` after any command


###Getting Lucky###
When it gets hot and heavy, whether you need some sound cover so your roommate doesn't bust into your room concerned that you're torturing a porpoise (sorry Dave) or just enjoy some background music run the command:
```
gl lucky
```
This will play a random Songza playlist for getting lucky.

You can also pick an option that best describes how you like to get down. 
```
  -m, --makeout       
  -s, --sexy                                    
  -d, --seductive           
  -a, --aggressive                              
  -x, --extreme   
```

Example Calls:
```
gl lucky -m
```

```
gl lucky --seductive
```

###Not Getting Lucky###
Get Lucky is great for even when you're not rocking the cabash. You can quickly play Songza playlists
by activity, genre, or mood. These commands take the following form where ```< >``` denotes an argument.

```
gl mood <mood>  
gl genre <genre> 
gl activity <activity>
```
The arguments must be a valid Songza [mood](http://songza.com/discover/moods), [activity](http://songza.com/discover/activity), [genre](http://songza.com/discover/genre). Also if the argument is more than one word you must put it in quotes.

Example Calls
```
gl activity 'ballroom dancing'
```

```
gl genre metal
``` 