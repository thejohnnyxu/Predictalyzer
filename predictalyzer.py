import json
import urllib.request
import os
import pprint
from bs4 import BeautifulSoup

pp = pprint.PrettyPrinter(indent=4)

# Steam Dev API Key
global apiKey
apiKey = 'D77171D2F475B06519F286FBF7485D4E'

heroList = {}
matchList = []
results = {}

def main():
    print('Predictalyzer executing...')

    # generates json files for 4 pages of dotabuff
    getMatches(1)

    # generates the dict heroList
    genHerolist()

    for filename in os.listdir("matches"):
        if filename.endswith(".json"):
            try:
                predictalyze('matches/%s' %(filename))
                findPickBans('matches/%s' %(filename))
            except:
                pass

    for heroID, value in heroList.items():
        heroName = heroList[heroID]['hero_name']
        # most kills across qualifiers - hero
        aggkills = sum(value['kills'])
        if aggkills > results['max_agg_kills'][1]:
            results['max_agg_kills'] = (heroName, aggkills)
        # most deaths across qualifiers - hero
        aggdeaths = sum(value['deaths'])
        if aggdeaths > results['max_agg_deaths'][1]:
            results['max_agg_deaths'] = (heroName, aggdeaths)
        # most deaths assists qualifiers - hero
        aggassists = sum(value['assists'])
        if aggassists > results['max_agg_assists'][1]:
            results['max_agg_assists'] = (heroName, aggassists)
        # number of heroes never picked or banned
        #print(heroName, value['picks'], value['bans'])
        if value['picks'] + value['bans'] == 0:
            if heroName not in results['never_pickban']:
                results['never_pickban'].append(heroName)

    # creates output.json with the stats
    json.dump(heroList, open('output.json', 'w'))
    # converts list of heroes never pick/ban into number
    results['never_pickban'] = [len(results['never_pickban'])]
    #pp.pprint(results)
    with open('predictions.txt', 'w') as f:
        for k, v in results.items():
            f.write(k)
            f.write(' - ')
            f.write(str(v))
            f.write(' ')
            f.write('\n')


# returns a list of matchIDs from http://dotabuff.com/matches/ti4
# pages = int() - number of pages to get matchIDs from
def getMatches(pages):
    for page in range(1, pages + 1):
        url = 'http://dotabuff.com/matches/ti4?page=%r' %(page)
        response = urllib.request.urlopen(url)
        soup = BeautifulSoup(response)
        for link in soup.findAll('a'):
            l = link.get('href')
            if l[:8] == '/matches':
                matchID = l[-9:]
                if isNumber(matchID):
                    matchList.append(int(matchID))

    dlMatches(matchList)

# downloads the json for each matchid from the matchList
def dlMatches(matches):
    global apiKey
    for matchID in matchList:
        path = 'matches/%s.json' %(matchID)
        if not os.path.exists(path):
            findmatch = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/?match_id=%s&key=%s' %(matchID, apiKey)
            response = urllib.request.urlopen(findmatch)
            content = response.read()
            data = json.loads(content.decode("utf8"))
            oFile = open(path, 'w')
            with oFile as outfile:
                json.dump(data, outfile)
                print('adding... %s.json' %(matchID))
            oFile.close()
        else:
            pass

# checks if string is all numbers
def isNumber(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

# creates dict heroList with heroID as key
# instantiate each dict with the hero's name
def genHerolist():
    with open('herolist.json', 'r+') as f:
        data = json.load(f)
        heroes = data['result']['heroes']
        for hero in heroes:
            heroID                           = hero['id']
            heroName                         = hero['localized_name']
            heroList[heroID]                 = {}
            heroList[heroID]['hero_name']    = heroName
            heroList[heroID]['kills']        = []
            heroList[heroID]['deaths']       = []
            heroList[heroID]['assists']      = []
            heroList[heroID]['last_hits']    = []
            heroList[heroID]['gold_per_min'] = []
            heroList[heroID]['tower_damage'] = []
            heroList[heroID]['hero_healing'] = []
            heroList[heroID]['picks']        = 0
            heroList[heroID]['bans']         = 0

    # instantiates results
    results['max_agg_kills']    = ('', 0)
    results['max_agg_deaths']   = ('', 0)
    results['max_agg_assists']  = ('', 0)
    results['never_pickban']    = []
    results['max_kills']        = ('', 0)
    results['max_deaths']       = ('', 0)
    results['max_assists']      = ('', 0)
    results['max_last_hits']    = ('', 0)
    results['max_gold_per_min'] = ('', 0)
    results['max_tower_damage'] = ('', 0)
    results['max_hero_healing'] = ('', 0)
    results['max_picks']        = ('', 0)
    results['max_bans']         = ('', 0)
    results['max_kills_isg']    = 0
    results['first_blood']      = 0


# gets data for hero with questions
def predictalyze(jsonfile):
    with open(jsonfile, 'r+') as f:
        data = json.load(f)
        players = data['result']['players']
        fbTime = data['result']['first_blood_time']
        total_kills = 0

        for player in players:
            heroID = player['hero_id']
            heroName = heroList[heroID]['hero_name']

            # list of all kills per heroID
            heroList[heroID]['kills'].append(player['kills'])
            if player['kills'] > results['max_kills'][1]:
                results['max_kills'] = (heroName, player['kills'])
            # list of all deaths per heroID
            heroList[heroID]['deaths'].append(player['deaths'])
            if player['deaths'] > results['max_deaths'][1]:
                results['max_deaths'] = (heroName, player['deaths'])
            # list of all assists per heroID
            heroList[heroID]['assists'].append(player['assists'])
            if player['kills'] > results['max_assists'][1]:
                results['max_assists'] = (heroName, player['assists'])
            # list of all last hits per heroID
            heroList[heroID]['last_hits'].append(player['last_hits'])
            if player['last_hits'] > results['max_last_hits'][1]:
                results['max_last_hits'] = (heroName, player['last_hits'])
            # list of all gpm per heroID
            heroList[heroID]['gold_per_min'].append(player['gold_per_min'])
            if player['gold_per_min'] > results['max_gold_per_min'][1]:
                results['max_gold_per_min'] = (heroName, player['gold_per_min'])
            # list of all tower damage per heroID
            heroList[heroID]['tower_damage'].append(player['tower_damage'])
            if player['tower_damage'] > results['max_tower_damage'][1]:
                results['max_tower_damage'] = (heroName, player['tower_damage'])
            # list of all healing per heroID
            heroList[heroID]['hero_healing'].append(player['hero_healing'])
            if player['hero_healing'] > results['max_hero_healing'][1]:
                results['max_hero_healing'] = (heroName, player['hero_healing'])
            # most kills (both teams) - int
            total_kills += player['kills']
            if total_kills > results['max_kills_isg']:
                results['max_kills_isg'] = total_kills
            # latest first blood - int
            if (fbTime / 60) > results['first_blood']:
                results['first_blood'] = (fbTime / 60)


# counts number of times each heroID is picked or banned
def findPickBans(jsonfile):
    with open(jsonfile, 'r+') as f:
        data = json.load(f)
        pickbans = data['result']['picks_bans']
        for hero in pickbans:
            if hero['is_pick']:
                heroList[hero['hero_id']]['picks'] += 1
            else:
                heroList[hero['hero_id']]['bans'] += 1

    for k, value in heroList.items():
        heroName = value['hero_name']
        picks = value['picks']
        bans  = value['bans']
        if picks > results['max_picks'][1]:
                results['max_picks'] = (heroName, picks)
        if bans > results['max_bans'][1]:
                results['max_bans'] = (heroName, bans)



if __name__ == '__main__':
    main()