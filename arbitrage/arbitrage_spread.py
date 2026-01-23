import requests
import json

#API key removed
API_KEY = ''

#sport keys from https://the-odds-api.com/sports-odds-data/sports-apis.html
SPORT_KEY = ['icehockey_nhl'
             
             ]
MARKET = 'spreads'

total_bet = 100 #total bet to wager

def fetch_pinnacle_odds(sport_key):
    url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds'
    params = {
        'apiKey': API_KEY,
        'markets': MARKET,
        'bookmakers': 'pinnacle',
        'oddsFormat': 'decimal'
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Error fetching odds:", response.text)
        return []
    
    with open('odds_data_pinnacle.json', 'w') as file:
        json.dump(response.json(), file, indent=2)

    #print(response.headers)
    return response.json()


def fetch_coolbet_odds(sport_key):
    url = f'https://api.the-odds-api.com/v4/sports/{sport_key}/odds'
    params = {
        'apiKey': API_KEY,
        'markets': MARKET,
        'bookmakers': 'coolbet',
        'oddsFormat': 'decimal'
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Error fetching odds:", response.text)
        return []
    
    with open('odds_data_coolbet.json', 'w') as file:
        json.dump(response.json(), file, indent=2)

    return response.json()


def check_arbitrage(total_bet, odds_1, odds_2):
    odds_1_percentage = 1/odds_1
    odds_2_percentage = 1/odds_2

    #check for arbitrage
    if (odds_1_percentage + odds_2_percentage) < 1:
       
        #solve for bets
        bet_1 = total_bet/(1+(odds_1/odds_2))
        bet_2 = total_bet - bet_1

        print(f"Bet for {odds_1} is {bet_1}")
        print(f"Bet for {odds_2} is {bet_2}")

        #calculate profit
        profit = (bet_1 * odds_1) - total_bet
        print(profit)

        #calculate ROI
        ROI = ((profit + total_bet) / total_bet - 1) * 100

        print(ROI)

def extract_odds(event, bookmaker_key):
    odds = {}
    for bookmaker in event.get('bookmakers', []):
        if bookmaker['key'] == bookmaker_key:
            for market in bookmaker.get('markets', []):
                if market['key'] == MARKET:
                    for outcome in market.get('outcomes', []):
                        odds[outcome['name']] = outcome['price']
    return odds

def main():

    for sport_key in SPORT_KEY:
        fetch_coolbet_odds(sport_key)
        fetch_pinnacle_odds(sport_key)

        with open('odds_data_pinnacle.json', 'r') as file:
            pinnacle_events = json.load(file)

        with open('odds_data_coolbet.json', 'r') as file:
            coolbet_events = json.load(file)

        if not pinnacle_events or not coolbet_events:
            print("No data to process")
            return    

    
        for pin_event in pinnacle_events:
            home_team = pin_event['home_team']
            away_team = pin_event['away_team']

            for cool_event in coolbet_events:
                if (cool_event['home_team'] == home_team and
                        cool_event['away_team'] == away_team):

                    pin_odds = extract_odds(pin_event, 'pinnacle')
                    cool_odds = extract_odds(cool_event, 'coolbet')

                    # Check both directions
                    if home_team in pin_odds and away_team in cool_odds:
                        print(f"\nMatch: {home_team} vs {away_team}")
                        print("Checking Pinnacle(Home) vs Coolbet(Away):")
                        check_arbitrage(total_bet, pin_odds[home_team], cool_odds[away_team])

                    if home_team in cool_odds and away_team in pin_odds:
                        print("Checking Coolbet(Home) vs Pinnacle(Away):")
                        check_arbitrage(total_bet, cool_odds[home_team], pin_odds[away_team])
        

if __name__ == '__main__':
    main()
