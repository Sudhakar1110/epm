no_cache = True
template = "templates/pages/epms/teams.html"

def get_context(context):
    context.no_cache = True
    context.title = "Teams"
    context.show_sidebar = False
