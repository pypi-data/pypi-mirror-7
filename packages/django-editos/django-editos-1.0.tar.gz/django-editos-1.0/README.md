# django-editos

django-editos is an app to manage and display editos

## Install

Using PyPI

    pip install django-editos

From source

   python setup.py install

## Basic usage

In settings.py

    add `geelweb.django.editos` to the `INSTALLED_APPS`

In the templates, load the editos tags

    {% load editos %}

and display the editos

    {% editos %}

## editos tag usage

    {% editos ['path/to/a/template.html'] %}

The only parameter is a tempalte file to render the editos

## Existing templates

 * editos/carousel.html, the default template. Render a Bootstrap 3 carousel
   http://getbootstrap.com/javascript/#carousel

## Create a template

The editos will be assign to the template in the `editos` variable

    {% for edito in editos %}
      {{ edito.title }}
    {% endfor %}
