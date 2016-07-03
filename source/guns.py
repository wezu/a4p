from collections import OrderedDict

guns=OrderedDict((
        ('saw',      {'icon':'gui/gun_saw.png',       'cost':0,    'model':'saw',      'hit_type':'melee',   'flash':None, 'bullet':None, 'ammo':(1,1), 'rof':1.0, 'dmg':50}),
        ('pistol',   {'icon':'gui/gun_pistol.png',    'cost':0,    'model':'pistol',   'hit_type':'hitscan', 'flash':None, 'bullet':None, 'ammo':(15,15), 'rof':1.0, 'dmg':50}),
        ('tool',     {'icon':'gui/gun_tool.png',      'cost':0,    'model':'tool',     'hit_type':'ray',     'flash':None, 'bullet':None, 'ammo':(50,50), 'rof':1.0, 'dmg':50}),
        ('smg',      {'icon':'gui/gun_smg.png',       'cost':50,   'model':'smg',      'hit_type':'hitscan', 'flash':None, 'bullet':None, 'ammo':(24,24), 'rof':1.0, 'dmg':50}),
        ('shotgun',  {'icon':'gui/gun_shotgun.png',   'cost':50,   'model':'shotgun',  'hit_type':'hitscan', 'flash':None, 'bullet':None, 'ammo':(8,8), 'rof':1.0, 'dmg':50}),
        ('hmg',      {'icon':'gui/gun_hmg.png',       'cost':100,  'model':'hmg',      'hit_type':'hitscan', 'flash':None, 'bullet':None, 'ammo':(120,120), 'rof':1.0, 'dmg':50}),
        ('sniper',   {'icon':'gui/gun_sniper.png',    'cost':100,  'model':'sniper',   'hit_type':'hitscan', 'flash':None, 'bullet':None, 'ammo':(5,5), 'rof':1.0, 'dmg':50}),
        ('mortar',   {'icon':'gui/gun_mortar.png',    'cost':200,  'model':'mortar',   'hit_type':'mortar',  'flash':None, 'bullet':None, 'ammo':(8,8), 'rof':1.0, 'dmg':50}),
        ('rocket',   {'icon':'gui/gun_rocket.png',    'cost':250,  'model':'rocket',   'hit_type':'rocket',  'flash':None, 'bullet':None, 'ammo':(4,4), 'rof':1.0, 'dmg':50}),
        ('lightning',{'icon':'gui/gun_lightning.png', 'cost':500,  'model':'lightning','hit_type':'ray',     'flash':None, 'bullet':None, 'ammo':(200,200), 'rof':1.0, 'dmg':50}),
        ('nuke',     {'icon':'gui/gun_nuke.png',      'cost':1000, 'model':'nuke',     'hit_type':'rocket',  'flash':None, 'bullet':None, 'ammo':(1,1), 'rof':1.0, 'dmg':50})
     ))
