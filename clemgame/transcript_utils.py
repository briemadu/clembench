from string import Template
from typing import Dict
from clemgame import file_utils

import html

CSS_STRING = file_utils.load_file("chat-two-tracks.css", file_ending=".css")

HTML_HEADER = '''
<!DOCTYPE html>
<html>
<head>
    <style>
        {}
    </style>
</head>
<body>

<br/>
'''

top_info = '''
<div class="top-info">
    <p>{}</p>
</div>

<br/>

<div class="chat">
'''

HTML_TEMPLATE = '''
    <div speaker="{}" class="msg {}">
        <p>{}</p>
    </div>
'''

HTML_FOOTER = '''
</div>

</body>
</html>
'''

TEX_HEADER = '''
\\documentclass{article}
\\usepackage{colortbl}
\\usepackage{makecell}
\\usepackage{multirow}
\\usepackage{supertabular}

\\begin{document}

\\newcounter{utterance}

\\twocolumn

{ \\footnotesize  \\setcounter{utterance}{1}
\\setlength{\\tabcolsep}{0pt}
\\begin{supertabular}{c@{$\;$}|p{.15\\linewidth}@{}p{.15\\linewidth}p{.15\\linewidth}p{.15\\linewidth}p{.15\\linewidth}p{.15\linewidth}}

    \\# & $\\;$A & \\multicolumn{4}{c}{Game Master} & $\\;\\:$B\\\\
    \\hline 
'''

TEX_BUBBLE_PARAMS = {
    "a-gm": ("0.8,1,0.9", "A$\\rangle$GM", "&", "& &", 4, 0.6),
    "b-gm": ("0.8,1,0.8", "GM$\\langle$B", "& & &", "", 4, 0.6),
    "gm-a": ("0.9,0.9,0.9", "A$\\langle$GM", "& &", "&", 4, 0.6),
    "gm-b": ("0.9,0.9,0.9", "GM$\\rangle$B", "& &", "&", 4, 0.6),
    "gm-gm": ("0.95,0.95,0.95", "GM$|$GM", "& & &", "& &", 2, 0.3)
}

TEX_TEMPLATE = Template('''
    \\theutterance \\stepcounter{utterance}  

    $cols_init \\multicolumn{$ncols}{p{$width\\linewidth}}{\\cellcolor[rgb]{$rgb}{%\n\t\\makecell[{{p{\\linewidth}}}]{% \n\t  \\tt {\\tiny [$speakers]}  \n\t $msg \n\t  } \n\t   } \n\t   } \n\t $cols_end \\\\ \n 
''')

TEX_FOOTER = '''
\\end{supertabular}
}

\\end{document}
'''


def _get_class_name(event):
    if event['from'] == 'GM' and event['to'] == 'Player 1':
        return "gm-a"
    if event['from'] == 'GM' and event['to'] == 'Player 2':
        return "gm-b"
    if event['from'] == 'Player 1' and event['to'] == 'GM':
        return "a-gm"
    if event['from'] == 'Player 2' and event['to'] == 'GM':
        return "b-gm"
    if event['from'] == 'GM' and event['to'] == 'GM':
        return "gm-gm"


def build_transcript(interactions: Dict, experiment_config: Dict, game_instance: Dict, dialogue_pair: str):
    """Create an html with the interaction transcript."""
    transcript = HTML_HEADER.format(CSS_STRING)
    title = f"Interaction Transcript for {experiment_config['name']}, " \
            f"episode {game_instance['game_id']} with {dialogue_pair}."
    transcript += top_info.format(title)
    # Collect all events over all turns (ignore turn boundaries here)
    events = [event for turn in interactions['turns'] for event in turn]
    for event in events:
        class_name = _get_class_name(event)
        msg_content = html.escape(f"{event['action']['content']}").replace('\n', '<br/>')
        if event['from'] == 'GM' and event['to'] == 'GM':
            speaker = f'Game Master: {event["action"]["type"]}'
        else:
            speaker = f"{event['from'].replace('GM', 'Game Master')} to {event['to'].replace('GM', 'Game Master')}"
        transcript += HTML_TEMPLATE.format(speaker, class_name, msg_content)
    transcript += HTML_FOOTER
    return transcript


def build_tex(interactions: Dict):
    tex = TEX_HEADER
    # Collect all events over all turns (ignore turn boundaries here)
    events = [event for turn in interactions['turns'] for event in turn]
    for event in events:
        class_name = _get_class_name(event).replace('msg ', '')
        msg_content = event['action']['content']
        if isinstance(msg_content, str):
            msg_content = msg_content.replace('\n', '\\\\ \\tt ')
        rgb, speakers, cols_init, cols_end, ncols, width = TEX_BUBBLE_PARAMS[class_name]
        tex += TEX_TEMPLATE.substitute(cols_init=cols_init,
                                       rgb=rgb,
                                       speakers=speakers,
                                       msg=msg_content,
                                       cols_end=cols_end,
                                       ncols=ncols,
                                       width=width)
    tex += TEX_FOOTER
    return tex
