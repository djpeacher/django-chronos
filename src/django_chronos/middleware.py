from django.conf import settings
from django.db import connection
from django.template.loader import render_to_string
from time import perf_counter
from types import SimpleNamespace

# Timeline visualization:
#
# [M.start] --> [V.start] --> [V.end] --> [M.end]
#     |             |            |           |
#   Q1,T1         Q2,T2        Q3,T3       Q4,T4
#     |_____________|            |___________|
#    middleware_before          middleware_after
#                   |____________|
#                        view
#
# Where:
# - M = Middleware, V = View
# - Q1-Q4 = Query counts at each point
# - T1-T4 = Timestamps at each point

class ChronosStartMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.chronos = SimpleNamespace()
        request.chronos.q1 = len(connection.queries)
        request.chronos.t1 = perf_counter()

        response = self.get_response(request)

        request.chronos.t4 = perf_counter()
        request.chronos.q4 = len(connection.queries)

        # Should we show stats?
        show_in_production = getattr(settings, 'CHRONOS_SHOW_IN_PRODUCTION', False)
        display_stats = settings.DEBUG or (show_in_production and request.user.is_superuser)
        if not display_stats:
            return response

        chronos = request.chronos

        # Calculate query counts
        middleware_sql_count       = (chronos.q2 - chronos.q1) + (chronos.q4 - chronos.q3)
        view_sql_count             = chronos.q3 - chronos.q2
        total_sql_count            = middleware_sql_count + view_sql_count
        # assert total_sql_count == chronos.q4 - chronos.q1

        # Calculate sql times
        middleware_before_sql_time = sql_time(chronos.q1, chronos.q2)
        view_sql_time              = sql_time(chronos.q2, chronos.q3)
        middleware_after_sql_time  = sql_time(chronos.q3, chronos.q4)
        middleware_sql_time        = middleware_before_sql_time + middleware_after_sql_time
        total_sql_time             = middleware_sql_time + view_sql_time
        # assert total_sql_time == sql_time(chronos.q1, chronos.q4)

        # Calculate cpu times
        middleware_before_cpu_time = (chronos.t2 - chronos.t1) - middleware_before_sql_time
        view_cpu_time              = (chronos.t3 - chronos.t2) - view_sql_time
        middleware_after_cpu_time  = (chronos.t4 - chronos.t3) - middleware_after_sql_time
        middleware_cpu_time        = middleware_before_cpu_time + middleware_after_cpu_time
        total_cpu_time             = middleware_cpu_time + view_cpu_time
        # assert total_cpu_time == (chronos.t4 - chronos.t1) - total_sql_time

        # Render stats
        context = {
            "debug": settings.DEBUG,

            # Middleware stats
            "middleware_cpu_time": format_time(middleware_cpu_time),
            "middleware_sql_time": format_time(middleware_sql_time), 
            "middleware_sql_count": f"{middleware_sql_count:,}",
            "middleware_total_time": format_time(middleware_cpu_time + middleware_sql_time),

            # View stats
            "view_cpu_time": format_time(view_cpu_time),
            "view_sql_time": format_time(view_sql_time),
            "view_sql_count": f"{view_sql_count:,}",
            "view_total_time": format_time(view_cpu_time + view_sql_time),

            # Total stats
            "total_cpu_time": format_time(total_cpu_time),
            "total_sql_time": format_time(total_sql_time),
            "total_sql_count": f"{total_sql_count:,}",
            "total_time": format_time(total_cpu_time + total_sql_time),
        }
        stats = render_to_string("chronos/chronos.html", context, request)

        # Swap stats into response
        swap_method = getattr(settings, 'CHRONOS_SWAP_METHOD', 'prepend')
        swap_target = getattr(settings, 'CHRONOS_SWAP_TARGET', '</body>')
        if response and (content := getattr(response, "content", None)):
            if swap_method == 'replace':
                swap_content = stats
            elif swap_method == 'prepend':
                swap_content = stats + swap_target
            elif swap_method == 'append':
                swap_content = swap_target + stats
            else:
                swap_content = stats
            response.content = content.decode().replace(swap_target, swap_content)
            response["Content-Length"] = str(len(response.content))
        return response

class ChronosEndMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.chronos.q2 = len(connection.queries)
        request.chronos.t2 = perf_counter()

        response = self.get_response(request)

        request.chronos.t3 = perf_counter()
        request.chronos.q3 = len(connection.queries)

        return response

def sql_time(start=None, end=None):
    return sum(float(q['time']) for q in connection.queries[start:end])

def format_time(time_value):
    return f"{time_value * 1000:.2f}"