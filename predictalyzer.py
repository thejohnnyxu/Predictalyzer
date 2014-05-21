import json
import urllib.request
import os
import pprint
from bs4 import BeautifulSoup

pp = pprint.PrettyPrinter(indent=4)

# Steam Dev API Key
global apiKey
apiKey = 'D77171D2F475B06519F286FBF7485D4E'
global max_klls_isg
max_klls_isg = 0
global max_gpm_isg
max_gpm_isg = 0
global first_blood
first_blood = 0

heroList = {}
matchList = []
hw = {}

def main():
    print('Predictalyzer executing...')

    # generates json files for 4 pages of dotabuff
    getMatches(8)

    # generates the dict heroList
    genHerolist()

    for filename in os.listdir("matches"):
        if filename.endswith(".json"):
            try:
                mostKillsISG('matches/%s' %(filename))
                maxGPMISG('matches/%s' %(filename))
                latestFirstBlood('matches/%s' %(filename))
                predictalyze('matches/%s' %(filename))
            except:
                pass

    # prints results
    print('Most Kills in a Single Game -', max_klls_isg)
    print('Highest GPM in a Single Game -', max_gpm_isg)
    print('Latest First Blood - ', first_blood / 60)

    for heroID in heroList:
        findMost(heroID, 'kills')
        findMost(heroID, 'deaths')
        findMost(heroID, 'assists')
        findMost(heroID, 'cs')
        findMost(heroID, 'gpm')
        findMost(heroID, 'tower_damage')
        findMost(heroID, 'healing')
        findMost(heroID, 'net_kills')
        findMost(heroID, 'net_deaths')
        findMost(heroID, 'net_assists')
        findMost(heroID, 'picks')
        findMost(heroID, 'bans')

    # creates output.json with the stats
    json.dump(heroList, open('output.json', 'w'))

    for key, value in hw.items():
        print('Hero with the most %s - %s with %s' %(key, value[0], value[1]))

    #print('Hero with most kills in a single game -', hw_most_kills_name, hw_most_kills)
    #print('Hero with most deaths in a single game -', hw_most_deaths_name, hw_most_deaths)
    #print('Hero with most assists in a single game -', hw_most_assists_name, hw_most_assists)
    #print('Hero with most Last Hits in a single game -', hw_most_cs_name, hw_most_cs)
    #print('Hero with highest GPM in a single game -', hw_most_gpm_name, hw_most_gpm)
    #print('Hero with most tower damage in a single game -', hw_most_twr_name, hw_most_twr)
    #print('Hero with most healing in a single game -', hw_most_heal_name, hw_most_heal)

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
def isNumber(s):
    try:
        float(s)
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
            heroID = hero['id']
            heroName = hero['localized_name']
            heroList[heroID] = {'hero_name': heroName}

# in a single game
# most kills (both teams) - int
def mostKillsISG(jsonfile):
    global max_klls_isg
    with open(jsonfile, 'r+') as f:
        data = json.load(f)
        players = data['result']['players']
        total_kills = 0
        for player in players:
            kills = player['kills']
            total_kills += kills
            if total_kills > max_klls_isg:
                max_klls_isg = total_kills

# largest crit - int
# highest gpm - int
def maxGPMISG(jsonfile):
    global max_gpm_isg
    with open(jsonfile, 'r+') as f:
        data = json.load(f)
        players = data['result']['players']
        for player in players:
            heroid = player['hero_id']
            gpm = player['gold_per_min']
            if gpm > max_gpm_isg:
                max_gpm_isg = gpm

# latest first blood - int
def latestFirstBlood(jsonfile):
    global first_blood
    with open(jsonfile, 'r+') as f:
        data = json.load(f)
        fbTime = data['result']['first_blood_time']
        if fbTime > first_blood:
            first_blood = fbTime

# gets data for hero with questions
def predictalyze(jsonfile):
    with open(jsonfile, 'r+') as f:
        data = json.load(f)
        players = data['result']['players']
        for player in players:
            heroID = player['hero_id']

            # most kills - hero
            current_kills = player['kills']
            if 'kills' not in heroList[heroID]:
                heroList[heroID]['kills'] = current_kills
            else:
                if current_kills > heroList[heroID]['kills']:
                    heroList[heroID]['kills'] = current_kills

            # most kills across qualifiers - hero
            if 'net_kills' not in heroList[heroID]:
                heroList[heroID]['net_kills'] = current_kills
            else:
                heroList[heroID]['net_kills'] += current_kills

            # most deaths - hero
            current_deaths = player['deaths']
            if 'deaths' not in heroList[heroID]:
                heroList[heroID]['deaths'] = current_deaths
            else:
                if current_deaths > heroList[heroID]['deaths']:
                    heroList[heroID]['deaths'] = current_deaths

            # most deaths across qualifiers - hero
            if 'net_deaths' not in heroList[heroID]:
                heroList[heroID]['net_deaths'] = current_deaths
            else:
                heroList[heroID]['net_deaths'] += current_deaths

            # most assists - hero
            current_assists = player['assists']
            if 'assists' not in heroList[heroID]:
                heroList[heroID]['assists'] = current_assists
            else:
                if current_assists > heroList[heroID]['assists']:
                    heroList[heroID]['assists'] = current_assists

            # most deaths assists qualifiers - hero
            if 'net_assists' not in heroList[heroID]:
                heroList[heroID]['net_assists'] = current_assists
            else:
                heroList[heroID]['net_assists'] += current_assists

            # most last hits - hero
            current_cs = player['last_hits']
            if 'cs' not in heroList[heroID]:
                heroList[heroID]['cs'] = current_cs
            else:
                if current_cs > heroList[heroID]['cs']:
                    heroList[heroID]['cs'] = current_cs

            # highest gpm - hero
            current_gpm = player['gold_per_min']
            if 'gpm' not in heroList[heroID]:
                heroList[heroID]['gpm'] = current_gpm
            else:
                if current_gpm > heroList[heroID]['gpm']:
                    heroList[heroID]['gpm'] = current_gpm

            # most tower damage - hero
            current_td = player['tower_damage']
            if 'tower_damage' not in heroList[heroID]:
                heroList[heroID]['tower_damage'] = current_td
            else:
                if current_td > heroList[heroID]['tower_damage']:
                    heroList[heroID]['tower_damage'] = current_td

            # high total healing - hero
            current_healing = player['hero_healing']
            if 'healing' not in heroList[heroID]:
                heroList[heroID]['healing'] = current_healing
            else:
                if current_healing > heroList[heroID]['healing']:
                    heroList[heroID]['healing'] = current_healing

            # most picked - hero
            if heroList[heroID]['is_pick']:
                if 'picks' not in heroList[heroID]:
                    heroList[heroID]['picks'] = 1
                else:
                    heroList[heroID]['picks'] += 1
            else:
                if 'bans' not in heroList[heroID]:
                    heroList[heroID]['bans'] = 1
                else:
                    heroList[heroID]['bans'] += 1

            # most banned - hero
            # most first bloods - hero
            # number of heroes never picked or banned



def findMost(heroID, key):
    if key not in hw:
        hw[key] = ['', 0]
    else:
        if key in heroList[heroID]:
            if heroList[heroID][key] > hw[key][1]:
                hw[key][1] = heroList[heroID][key]
                hw[key][0] = heroList[heroID]['hero_name']





if __name__ == '__main__':
    main()