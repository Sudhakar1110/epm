no_cache = True
template = "templates/pages/epms/scorecards.html"

def get_context(context):
    context.no_cache = True
    context.title = "Scorecards"
    context.show_sidebar = False
