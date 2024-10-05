import dash
from utils import common

app = dash.Dash(__name__, external_stylesheets=["assets/bootstrap.min.css"],
                meta_tags=common.META_TAGS, title='PKPDAI', update_title=None, suppress_callback_exceptions=True)
app.title = 'PKPDAI'

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XK51SXFTR6"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-XK51SXFTR6');
    </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""

server = app.server
