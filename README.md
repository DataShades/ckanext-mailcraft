[![Tests](https://github.com/DataShades/ckanext-mailcraft/actions/workflows/test.yml/badge.svg)](https://github.com/DataShades/ckanext-mailcraft/actions/workflows/test.yml)

# ckanext-mailcraft

The `ckanext-mailcraft` adds powerful email management features to CKAN, making it easier to style, track, and control outgoing messages.

**Features**
- Flexible Mailer – a custom mailer that can be easily extended to fit your needs
- Pre-styled Templates – an example email template you can customize to match your branding
- Email Logging – configurable option to save outgoing emails and view them in the dashboard
- Email Control – configurable option to temporarily stop outgoing messages when needed
- Redirection – configurable option to reroute all outgoing emails to one or more specified addresses

To enable the extension, add `mailcraft` to the `ckan.plugins` setting in your CKAN.
If you want to enable the dashboard you should also add `mailcraft_dashboard` to the `ckan.plugins` setting.

## Usage
To use a mailer, you just have to import it and initialize the mailer.

```python
from ckanext.mailcraft.utils import get_mailer

mailer = get_mailer()

mailer.mail_recipients(
    subject="Hello world",
    recipients=["test@gmail.com"],
    body="Hello world",
    body_html=tk.render(
        "mailcraft/emails/test.html",
        extra_vars={"site_url": mailer.site_url, "site_title": mailer.site_title},
    ),
)
```

> [!IMPORTANT]
> If you're using environment variables to configure the SMTP server, you must create the mailer instance within a method or function scope; otherwise, the mailer will take the config options from the CKAN config file.

## Dashboard
****
To access the dashboard, first ensure that the `mailcraft_dashboard` plugin is enabled in your CKAN configuration. Then you'll have a button at the top right of the CKAN interface that will take you to the Mailcraft dashboard.

![dashboard button](doc/button.png)

The dashboard provides an overview of all outgoing emails, including their status (sent, failed, etc.), recipients, and timestamps. You can filter and search through the emails to find specific ones.

![dashboard](doc/dashboard.png)

The `ckanext.mailcraft.save_emails` config option must be set to `true` to save outgoing emails and view them in the dashboard. You can also press the `View` button to see the full content of each email.

![mail body](doc/body.png)

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.9 and earlier | no            |
| 2.10+           | yes           |


## Installation

Use PyPI to install the extension with pip. Or check the Developer installation section.

```sh
pip install ckanext-mailcraft
```

## Config settings

Check the [config_declaration.yaml](ckanext/mailcraft/config_declaration.yaml) file to see all available config settings.

## Developer installation

To install ckanext-mailcraft for development, activate your CKAN virtualenv and
do:

```sh
git clone https://github.com/DataShades/ckanext-mailcraft.git
cd ckanext-mailcraft
python setup.py develop
pip install -r dev-requirements.txt
```

## Build CSS

Run this command from the `theme` folder.

```sh
npx sass styles.scss:./../assets/css/style.css -s compressed --no-source-map
```

## Tests

To run the tests, do:
```sh
pytest --ckan-ini=test.ini
```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
