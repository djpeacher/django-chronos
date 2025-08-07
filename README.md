# django-chronos [![PyPI version](https://img.shields.io/pypi/v/django-chronos.svg)](https://pypi.org/project/django-chronos/)

Django middleware that shows you how fast your pages load, right in your browser. Displays request timing and query counts for your views and middleware.

<p align="center">
    <img width="644" height="362" alt="django-chronos" src="https://github.com/user-attachments/assets/f1c61c50-d3a2-4a96-9078-40b2ea9b4430" />
</p>

## Installation

Install Django Chronos using pip:

```bash
pip install django-chronos
```

## Quick Start

1. **Add to INSTALLED_APPS** in your Django settings:

```python
INSTALLED_APPS = [
    # ... your other apps
    'chronos',
]
```

2. **Add middleware** to your Django settings (order matters):

```python
MIDDLEWARE = [
    'chronos.middleware.ChronosStartMiddleware',  # Must be first
    # ... your other middleware
    'chronos.middleware.ChronosEndMiddleware',    # Must be last
]
```

3. **Run your Django application** and visit any page. You'll see a stats overlayed in the bottom-left corner.

## Configuration

### `CHRONOS_SHOW_IN_PRODUCTION` (default: `False`)
Controls whether stats are shown in production mode (DEBUG=False). Stats are only shown to superusers in production. Stats always show in DEBUG mode.

```python
CHRONOS_SHOW_IN_PRODUCTION = True
```

### `CHRONOS_SWAP_METHOD` (default: `'prepend'`)
Controls how the stats are inserted into the response:
- `'prepend'`: Insert stats before the target
- `'append'`: Insert stats after the target  
- `'replace'`: Replace the target with stats

```python
CHRONOS_SWAP_METHOD = 'append'
```

### `CHRONOS_SWAP_TARGET` (default: `'</body>'`)
The string in the response where stats will be swapped in. Stats will not be displayed if this string does not exist in the response.

```python
CHRONOS_SWAP_TARGET = '</body>'
```

### Customizing the Stats Display

You can override the default stats display by creating your own `chronos/chronos.html` template in your Django project.

The template receives the following context variables:
- `middleware_cpu_time`, `middleware_sql_time`, `middleware_sql_count`, `middleware_total_time`
- `view_cpu_time`, `view_sql_time`, `view_sql_count`, `view_total_time`  
- `total_cpu_time`, `total_sql_time`, `total_sql_count`, `total_time`

**Note**: In production mode, the `*_sql_time` and `*_sql_count` variable values will be zero ([why?](https://docs.djangoproject.com/en/5.2/faq/models/#how-can-i-see-the-raw-sql-queries-django-is-running)). You can wrap these variables in `{% if debug %}` blocks to stop them from displaying in production.

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Appreciation

Adam Hill for the inspiration via his [Mastodon thread](https://indieweb.social/@adamghill/114950349384521325).
