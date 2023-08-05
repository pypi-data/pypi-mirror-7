Welcome to django-bootstrap-span!
=================================

.. image:: https://travis-ci.org/stumc/django-bootstrap-span.svg?branch=master
    :target: https://travis-ci.org/stumc/django-bootstrap-span
.. image:: https://coveralls.io/repos/stumc/django-bootstrap-span/badge.png
    :target: https://coveralls.io/r/stumc/django-bootstrap-span

Abstract
--------

When using Django and Bootstrap V2 - for mobile responsive web pages - it is hard to control the horizontal width of the form fields. 

In the normal Bootstrap V2 world - developers add class="span1 span2 span3..." directives to the input field elements they want to control the horizontal sizes for. This is harder to do in the Django world - since the field definitions are already defined by the underlying model or form infrastructure. 

Adding these class span directives manually in the forms seems like a duplication of work (violating Django's DRY principle).

The **django-bootstrap-span** library solves this problem by applying class="spanN" CSS modifiers on a form's fields - setting the effective width (in spans) of the horizontal form input elements.

In conjunction with a Bootstrap V2 CSS, these "spanN" class definitions control how wide a form field elements are rendered in the HTML. The expected use of this is with django-bootstrap and your Django application.

NOTE This is not meant for use in Bootstrap V3, which no longer uses spanN classes.

How it works
------------

This library uses the maximum field widths gleaned from the underlying form or model definitions - to know how to correctly calculate the size of the class span attribute for the input field. 

Thus you do not need to repeat the field max length settings - as each field is HTML horizontally sized correctly.


Installing
----------

Install **django-bootstrap-span** with
``pip install django-bootstrap-span``.

Requires django-bootstrap (which, in turn, includes Twitter Bootstrap v2.0).

Usage
-----

Install the ``bootstrap_span`` application in your settings file::

    INSTALLED_APPS = (
     ...
        'bootstrap_toolkit',
        'bootstrap_span',
     ...
     )

Install ``apply_bootstrap_span`` form filter in each of your forms template \*.html files::

    {% load bootstrap_span %}
    {{ form | apply_bootstrap_span:"" | as_bootstrap }}

By default, the filter ``apply_bootstrap_span`` looks at each field in the form, and decides how many 
spans (span1 to span12) to assign to it.

Up to 12 spans (the default) can be assigned to an input field - each calculated based on it's fields defined maximum character width.

As a Bootstrap ''span'' is an arbitrary division of horizontal screen width - an adjustment is applied to scale from the maximum width (defined per form field in characters) to calculate to the number of spans.

This scaling is done using a scaling parameter called ''characters per span'' -which has a arbitraty default value of 5. That is to say each span is treated as this number of characters width.


You can change 
  - the maximum number of spans to allocate (in case you are placing a form in a part of the HTML which is span-limited) or 
  - the characters per span in each form (in case your want to alter the relative character density of the fields for your page)

in each form. 

For instance, if I wanted to render form's fields with a maximum of 11 spans and 3 characters width per span, I would use::

    {{ form|apply_bootstrap_span:"11,3"| as_bootstrap }}

Where should I apply this span setting?
---------------------------------------

You should normally apply the span settings to your form in the template html file. This is because the form may be placed inside a multi column HTML page which does not use the full 12 spans of the default screen. In this case you would set the maximum span parameter value to something less that the default 12 spans.

However you can use this in your view class via a decorator - and also via a mixin to your view class - though these are not recommended - as they go against the separation of the MVC responsibilities (mixing the MVC-controller (i.e. a Django view)- with the MVC-view (i.e. Django's template file).

A Fuller Example
----------------

Here is a fuller example using 11 spans and 6 characters per span, all enclosed in a form with crsf_token checking and an ''OK'' submit button::

        {% load bootstrap_toolkit %}
        
        <form method="post" action="." enctype="multipart/form-data">
        {% csrf_token %}
        {% load bootstrap_form_span %}
        {{ form|apply_bootstrap_span:"11,5"|as_bootstrap }}
        
        <input type="submit" class="btn" value="{% trans 'OK' %}" />
        
        </form>


