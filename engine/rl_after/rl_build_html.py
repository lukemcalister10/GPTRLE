import os
style   = open('_v20_style.css').read()
extra   = open('_extra.css').read()
body    = open('_body.html').read()
insights= open('_insights.html').read()
body    = body.replace('<!--INSIGHTS_CARD-->', insights)
engine  = open('_engine_block_v23.js').read()
features= open('_features_v23.js').read()
insjs   = open('_insights.js').read()
DATA    = open('rl_app_data.json').read().strip()
head = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>Real-Draft Value Engine</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Familjen+Grotesk:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">\n')
html = (head + style + '\n' + extra + '\n</head><body>\n' + body
        + '\n<script>\nconst D=' + DATA + ';\n' + engine + '\n' + features + '\n' + insjs + '\n</script></body></html>\n')
os.makedirs('/mnt/user-data/outputs',exist_ok=True)
open('/mnt/user-data/outputs/rl_draft_engine.html','w').write(html)
open('rl_draft_engine.html','w').write(html)
print('written',len(html),'bytes; data',len(DATA),'bytes')
