from aenum import Enum, skip


class CONSTS(Enum):
    EMOJI = {"Health": u'❤', "PlaneHP": u'💞', "Armor": u'🛡', "Consumption": u'🛢', "Acc": u'🎯', "Fire": u'🔥',
             "Reload": u'♻', "AA": u'📡', "Torp": u'🥢', "Air": u'🛩', "Evade": u'👥',
             "Speed": u'⏩', "Luck": u'🎱', "ASW": u'🛥', "Oxygen": u'☁', "Ammo": u'🎹',
             "ConstructTime": u'🛠', "Firepower": u'🔥', "Aviation": u'🛩', "RoF": u'♻',
             "Accuracy": u'🎯', "Torpedo": u'🥢', 'Coin': u'📀', "Medal": u'🎖', 'Tech': u'✨',
             "Oil": u'🛢', "Evasion": u'👥', "Anti-Air": u'📡', 'Specialized Core': u'🔬',
             'Notes': u'📄', 'DropLocation': "🗺", "Damage": u'💥', 'Bombs': u'💣', 'Spd': u'⏩'}

    @skip
    class SQL(Enum):
        API_URL = "https://azurlane.koumakan.jp/w/index.php?"
        WIKI_URL = "https://azurlane.koumakan.jp/"
        WIKIPEDIA_URL = "https://wikipedia.org/wiki/"

        # Cursed WikiApi SQL
        SHIP_TABLE_ALL_FIELDS = 'ShipGroup,ShipID,Name,CNName,JPName,KRName,Rarity,Nationality,ConstructTime,Type,SubtypeRetro,Class,Artist,ArtistLink,ArtistPixiv,ArtistTwitter,Voiced,VA,Remodel,RemodelId,Image,ImageShipyardIcon,ImageChibi,ImageIcon,ImageBanner,ImageKai,ImageShipyardIconKai,ImageChibiKai,ImageIconKai,ImageBannerKai,HealthInitial,Armor,FireInitial,AAInitial,TorpInitial,AirInitial,ReloadInitial,EvadeInitial,ConsumptionInitial,Speed,Luck,AccInitial,ASWInitial,OxygenInitial,AmmoInitial,HealthMax,FireMax,AAMax,TorpMax,AirMax,ReloadMax,EvadeMax,ConsumptionMax,AccMax,ASWMax,OxygenMax,AmmoMax,HealthKai,ArmorKai,FireKai,AAKai,TorpKai,AirKai,ReloadKai,EvadeKai,ConsumptionKai,SpeedKai,ASWKai,AccKai,OxygenKai,AmmoKai,Health120,Fire120,AA120,Torp120,Air120,Reload120,Evade120,Consumption120,Acc120,ASW120,Oxygen120,Ammo120,HealthKai120,FireKai120,AAKai120,TorpKai120,AirKai120,ReloadKai120,EvadeKai120,ConsumptionKai120,AccKai120,ASWKai120,OxygenKai120,AmmoKai120,Eq1Type,Eq1EffInit,Eq1EffInitMax,Eq1EffInitKai,Eq2Type,Eq2EffInit,Eq2EffInitMax,Eq2EffInitKai,Eq3Type,Eq3EffInit,Eq3EffInitMax,Eq3EffInitKai,LB1,LB2,LB3'
        ITEM_TABLE_ALL_FIELDS = 'Name,Image,Type,Stars,Nationality,Tech,Health,HealthMax,Torpedo,TorpMax,Firepower,FPMax,Aviation,AvMax,Evasion,EvasionMax,PlaneHP,PlaneHPMax,Reload,ReloadMax,ASW,ASWMax,Oxygen,OxygenMax,AA,AAMax,Luck,LuckMax,Acc,AccMax,Spd,SpdMax,Damage,DamageMax,RoF,RoFMax,Number,Spread,Angle,WepRange,Shells,Salvoes,Characteristic,PingFreq,VolleyTime,Coef,Ammo,AAGun1,AAGun2,Bombs1,Bombs2,DD,DDNote,CL,CLNote,CA,CANote,CB,CBNote,BM,BMNote,BB,BBNote,BC,BCNote,BBV,BBVNote,CV,CVNote,CVL,CVLNote,AR,ARNote,SS,SSNote,SSV,SSVNote,DropLocation,Notes'

    @skip
    class SHIP(Enum):
        CLASSES = {"DD": "Destroyer", "CL": "Light Cruiser", "CA": "Heavy Cruiser",
                   "CB": "Large Cruiser", "BM": "Monitor", "BB": "Battleship",
                   "BC": "Battlecruiser", "BBV": "Aviation Battleship", "CV": "Aircraft Carrier",
                   "CVL": "Light Aircraft Carrier", "AR": "Repair Ship", "SS": "Submarine",
                   "SSV": "Submarine Carrier", "AE": "Munition"}

        @skip
        class RARITY(Enum):
            """U0 N1 R2 E3 SR4 P4 UR5 D5"""
            FORMAT = {"Unreleased": u"**U-🔹🔹🔹🔹🔹❔", "Normal": u"**N-🔶🔹🔹🔹🔹**",
                      "Rare": u"**R-🔶🔶🔹🔹🔹**", "Elite": u"**E-🔶🔶🔶🔹🔹**", "Super Rare": u"**SR-🔶🔶🔶🔶🔹**",
                      "Ultra Rare": u"**UR-🔶🔶🔶🔶🔶**", "Decisive": u"**D-🔶🔶🔶🔶🔶**",
                      "Priority": u"**P-🔶🔶🔶🔶🔹**"}

            COLORS = {"Unreleased": 0xD3D3D3, "Normal": 0xD3D3D3,
                      "Rare": 0x41D7FF, "Elite": 0xCC7BFF, "Super Rare": 0xFDC637,
                      "Ultra Rare": 0xBD4000, "Decisive": 0xBD4000, "Priority": 0xFDC637}

        STAT_TYPES = {"Base Stats": "Initial", "Max Stats": "Max", "Cognitive Max Stats": "120",
                      "Retrofit Max Stats": "Kai", "Cognitive Retrofit Max Stats": "Kai120"}

        @skip
        class RETROFIT(Enum):
            """U0 N1 R2 E3 SR4 P4 UR5 D5"""
            RARITY = {"Unreleased": "Rare", "Normal": "Rare",
                      "Rare": "Elite", "Elite": "Super Rare", "Super Rare": "Ultra Rare",
                      "Ultra Rare": "Ultra Rare", "Decisive": "Decisive", "Priority": "Priority"}

            IMAGES = ("Image", "ImageShipyardIcon", "ImageChibi", "ImageIcon", "ImageBanner",
                      "ImageKai", "ImageShipyardIconKai", "ImageChibiKai", "ImageIconKai", "ImageBannerKai")

            MENU_REACTIONS = u'❌🛶🛥⛴🚤🛳🎯🏵🪀🗺ℹ🇷'
            MENU_TYPES = ("Base Stats", "Max Stats", "Cognitive Max Stats",
                          "Retrofit Max Stats", "Cognitive Retrofit Max Stats")

        @skip
        class NORMAL(Enum):
            IMAGES = ("Image", "ImageShipyardIcon", "ImageChibi", "ImageIcon", "ImageBanner")
            MENU_REACTIONS = u'❌🛶🛥⛴🎯🏵🪀🗺ℹ'
            MENU_TYPES = ("Base Stats", "Max Stats", "Cognitive Max Stats")

        @skip
        class STATS(Enum):
            # They really can't decide what text to use..

            TYPES = ("Health", "Armor", "Oil", "Acc", "Fire",
                     "Reload", "Anti-Air", "Torpedo", "Aviation", "Evasion",
                     "Speed", "Luck", "ASW", "Oxygen", "Ammo")

            # "Health", "Fire", "AA", "Torp", "Air", "Reload", "Evade", "Consumption", "Acc", "ASW", "Oxygen", "Ammo"
            # Not changing values are Luck, Speed, ConstructTime
            FORMAT = {"Health": "Health", "Armor": "Armor", "Oil": "Consumption", "Acc": "Acc",
                      "Fire": "Fire", "Reload": "Reload", "Anti-Air": "AA", "Torpedo": "Torp",
                      "Aviation": "Air", "Evasion": "Evade", "Speed": "Speed", "Luck": "Luck",
                      "ASW": "ASW", "Ammo": "Ammo", "Oxygen": "Oxygen", "Construction": "ConstructTime"}

    @skip
    class ITEM(Enum):
        BASE_STATS = ("Health", "Torpedo", "Firepower", "Aviation",
                      "Evasion", "PlaneHP", "Reload", "ASW",
                      "Oxygen", "AA", "Luck", "Acc", "Spd")

        MAX_STATS = ("HealthMax", "TorpMax", "FPMax", "AvMax",
                     "EvasionMax", "PlaneHPMax", "ReloadMax", "ASWMax",
                     "OxygenMax", "AAMax", "LuckMax", "AccMax", "SpdMax", "RoFMax",)

        RARITY_EMOJI = {'1': u'🥉', '2': u'🥈', '3': u'🥇', '4': u'🏅', '5': u'🎖', '6': u'🏆'}
        STARS = {'1': u'N-⭐', '2': u'N-⭐⭐', '3': u'R-⭐⭐⭐', '4': u'E-⭐⭐⭐⭐', '5': u'SR-⭐⭐⭐⭐⭐', '6': u'UR-⭐⭐⭐⭐⭐⭐'}
        COLOR = {'1': 0xCCCCCC, '2': 0xCCCCCC, '3': 0x41D7FF, '4': 0xCC7BFF, '5': 0xFDC637, '6': 0xBD4000}
