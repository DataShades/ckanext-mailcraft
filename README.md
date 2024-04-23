[![Tests](https://github.com/mutantsan/ckanext-mailcraft/workflows/Tests/badge.svg?branch=main)](https://github.com/mutantsan/ckanext-mailcraft/actions)

# ckanext-mailcraft

The `ckanext-mailcraft` extension provides next features:
- A custom mailer that can be conveniently expanded as needed
- Prestyled email template
- A dashboard where you can view a list of all sent e-mails
- A function of stopping the sending of all emails sent through our mailer in order to debug the functionality.

Dashboard and config pages will be available only if you're using the `ckanext-admin-panel` extension. If not, only
mailer will be available.


## Usage
To use a mailer, you just have to import it.

    ```
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

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |

| 2.9 and earlier | no            |
| 2.10+           | yes           |


## Installation

Use PyPI to install the extension with pip. Or check the Developer installation section.


## Config settings

There's a separate page in admin panel to configure mailcraft settings. Check the `config_declaration.yaml` file. 


## Developer installation

To install ckanext-mailcraft for development, activate your CKAN virtualenv and
do:

    git clone https://github.com/mutantsan/ckanext-mailcraft.git
    cd ckanext-mailcraft
    python setup.py develop
    pip install -r dev-requirements.txt


## Tests

To run the tests, do:
    pytest --ckan-ini=test.ini


## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
